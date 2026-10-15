"""Portfolio review: the tool behind the Performance review agent (layer 6).

Reads the four tables in the schema and writes:
- report.md     a readable review for a Product Lead
- summary.json  the same facts in a structured form, for an agent to use

The key rule: compare games at the same age (days since launch), never on
total GGR. Games too young for a window are reported as "not yet".

Usage:
    python examples/portfolio_review/analyze.py [--config path/to/config.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def validate_config(cfg: dict) -> None:
    windows = cfg.get("windows_days", [])
    if not windows or any(type(w) is not int or w <= 0 for w in windows):
        raise ValueError("windows_days must contain positive integers.")
    if 30 not in windows or cfg.get("main_window_days") not in windows:
        raise ValueError("windows_days must include 30 and main_window_days.")
    if not 0 < cfg.get("revenue_share", 0) <= 1:
        raise ValueError("revenue_share must be greater than 0 and at most 1.")
    if type(cfg.get("min_group_size")) is not int or cfg["min_group_size"] < 1:
        raise ValueError("min_group_size must be a positive integer.")


def validate_tables(t: dict) -> None:
    games = t["games"]
    if games.empty or games["game_id"].isna().any() or games["game_id"].duplicated().any():
        raise ValueError("games must have non-empty, unique game_id values.")
    ids = set(games["game_id"])
    for name, keys in [("costs", ["game_id", "discipline"]), ("milestones", ["game_id", "milestone"]), ("daily_performance", ["game_id", "date"])]:
        table = t[name]
        if table.empty or table[keys].isna().any().any() or table.duplicated(keys).any():
            raise ValueError(f"{name}: missing keys or duplicate rows.")
        if not set(table["game_id"]).issubset(ids):
            raise ValueError(f"{name}: unknown game_id.")
    for name, columns in [("costs", ["budget_eur", "actual_eur"]), ("daily_performance", ["bets_eur", "ggr_eur"])]:
        for column in columns:
            series = pd.to_numeric(t[name][column], errors="raise")
            if series.isna().any() or not series.map(lambda x: float("-inf") < x < float("inf")).all():
                raise ValueError(f"{name}.{column}: finite numeric values required.")
            t[name][column] = series
    if (t["costs"][["budget_eur", "actual_eur"]] < 0).any().any() or (t["daily_performance"]["bets_eur"] < 0).any():
        raise ValueError("Costs and bets must be non-negative. Daily GGR may be negative.")
    p = t["daily_performance"]
    cutoff = p["date"].max()
    for row in games.itertuples():
        dates = p.loc[p["game_id"] == row.game_id, "date"]
        expected = pd.date_range(row.launch_date, cutoff, freq="D")
        if pd.isna(row.launch_date) or len(expected) == 0 or set(dates) != set(expected):
            raise ValueError(f"{row.game_id}: daily coverage must run from launch through the common data cutoff; missing/pre-launch dates are not zero.")
        if row.game_id not in set(t["costs"]["game_id"]):
            raise ValueError(f"{row.game_id}: costs are required.")
        milestones = t["milestones"].loc[t["milestones"]["game_id"] == row.game_id]
        if not {"kick_off", "activation"}.issubset(set(milestones["milestone"])):
            raise ValueError(f"{row.game_id}: kick_off and activation milestones are required.")
        if milestones[["planned_date", "actual_date"]].isna().any().any():
            raise ValueError(f"{row.game_id}: milestone dates are required by this completed-project example.")


def load(cfg: dict) -> dict[str, pd.DataFrame]:
    d = (HERE / cfg["data_dir"]).resolve()
    t = {name: pd.read_csv(d / f"{name}.csv") for name in ["games", "costs", "milestones", "daily_performance"]}
    t["games"]["launch_date"] = pd.to_datetime(t["games"]["launch_date"])
    t["daily_performance"]["date"] = pd.to_datetime(t["daily_performance"]["date"])
    for c in ["planned_date", "actual_date"]:
        t["milestones"][c] = pd.to_datetime(t["milestones"][c])
    validate_tables(t)
    return t


def per_game(t: dict, cfg: dict) -> pd.DataFrame:
    g = t["games"].set_index("game_id").copy()
    p = t["daily_performance"].merge(g[["launch_date"]], left_on="game_id", right_index=True)
    p["day"] = (p["date"] - p["launch_date"]).dt.days
    data_date = p["date"].max()
    g["days_live"] = (data_date - g["launch_date"]).dt.days + 1
    g["ggr_total"] = p.groupby("game_id")["ggr_eur"].sum()
    for w in cfg["windows_days"]:
        val = p[p["day"] < w].groupby("game_id")["ggr_eur"].sum()
        g[f"ggr_{w}d"] = val.where(g["days_live"] >= w)  # NaN = not old enough yet

    cost = t["costs"].groupby("game_id")[["budget_eur", "actual_eur"]].sum()
    g = g.join(cost)

    # break-even: first day cumulative studio revenue >= actual cost
    share = cfg["revenue_share"]
    p = p.sort_values(["game_id", "day"])
    p["cum_rev"] = p.groupby("game_id")["ggr_eur"].cumsum() * share
    p = p.join(g["actual_eur"], on="game_id")
    be = p[p["cum_rev"] >= p["actual_eur"]].groupby("game_id")["day"].min()
    g["break_even_day"] = be
    g["profit_to_date"] = g["ggr_total"] * share - g["actual_eur"]

    m = t["milestones"]
    ko = m[m.milestone == "kick_off"].set_index("game_id")
    act = m[m.milestone == "activation"].set_index("game_id")
    g["weeks_planned"] = (act["planned_date"] - ko["planned_date"]).dt.days / 7
    g["weeks_actual"] = (act["actual_date"] - ko["actual_date"]).dt.days / 7
    g["slip_weeks"] = g["weeks_actual"] - g["weeks_planned"]
    g.attrs["data_date"] = data_date.date().isoformat()
    return g


def group_table(g: pd.DataFrame, by: str, col: str, min_n: int) -> pd.DataFrame:
    sub = g.dropna(subset=[col])
    out = sub.groupby(by)[col].agg(games="count", median="median", low="min", high="max")
    out["warning"] = out["games"].apply(lambda n: "small group" if n < min_n else "")
    return out.sort_values("median", ascending=False)


def pct(value) -> str:
    return "not available" if value is None or pd.isna(value) else f"{value:.0%}"


def rounded(value):
    return None if pd.isna(value) else round(float(value), 3)


def eur(x) -> str:
    if pd.isna(x):
        return "not yet"
    return f"{x/1000:,.0f}k"


def md_table(df: pd.DataFrame, money_cols: list[str]) -> str:
    df = df.copy()
    for c in money_cols:
        df[c] = df[c].apply(eur)
    df = df.reset_index()
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    rows = ["| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def build(cfg: dict) -> tuple[str, dict]:
    validate_config(cfg)
    t = load(cfg)
    g = per_game(t, cfg)
    W = cfg["main_window_days"]
    col = f"ggr_{W}d"
    min_n = cfg["min_group_size"]
    share = cfg["revenue_share"]

    # 1. why age matters: rank on total vs rank at the same age
    rank = g[["title", "days_live", "ggr_total", col]].copy()
    rank["rank_total"] = rank["ggr_total"].rank(ascending=False).astype(int)
    rank["rank_fair"] = rank[col].rank(ascending=False)
    moved = rank.dropna(subset=["rank_fair"]).copy()
    moved["rank_fair"] = moved["rank_fair"].astype(int)
    moved["moved"] = (moved["rank_total"] - moved["rank_fair"]).abs()
    top_moves = moved.sort_values("moved", ascending=False).head(5)

    # 2. cost is predictable, revenue is not
    cv_cost = g.groupby("type")["actual_eur"].agg(lambda s: s.std() / s.mean())
    cv_rev = g.dropna(subset=[col]).groupby("type")[col].agg(lambda s: s.std() / s.mean())
    top_share = g[col].dropna().sort_values(ascending=False)
    if top_share.empty:
        raise ValueError("No games have completed the main comparison window.")
    n_top = max(1, round(len(top_share) * 0.2))
    top20 = top_share.head(n_top).sum() / top_share.sum() if top_share.sum() > 0 else None

    groups = {by: group_table(g, by, col, min_n) for by in ["family", "type", "exclusive", "vendor"]}
    slip_vendor = g.groupby("vendor")[["weeks_planned", "weeks_actual", "slip_weeks"]].median().round(1)
    reasons = t["milestones"]["slip_reason"].value_counts()
    young = g[g[col].isna()][["title", "days_live"]]

    games_tbl = g[["title", "type", "family", "days_live", "ggr_30d", col, "actual_eur", "break_even_day"]].copy()
    games_tbl["break_even_day"] = games_tbl["break_even_day"].apply(lambda v: "not yet" if pd.isna(v) else int(v))
    games_tbl = games_tbl.sort_values(col, ascending=False)

    lines = [
        "# Portfolio review",
        "",
        f"Data up to **{g.attrs['data_date']}**. {len(g)} games. Revenue share used: {share:.0%}. "
        f"Main comparison window: **{W} days after launch**.",
        "",
        f"> Generated by `analyze.py`. All figures in EUR. Input label: {cfg.get('data_label', 'unverified')}.",
        "",
        "## Key facts",
        "",
        f"1. **Observed reskin variation.** Cost varies by {pct(cv_cost.get('reskin', float('nan')))} between reskins; "
        f"GGR at {W} days varies by {pct(cv_rev.get('reskin', float('nan')))}.",
        f"2. **Observed GGR concentration.** The top {n_top} games ({n_top/len(top_share):.0%}) make "
        f"{pct(top20)} of GGR at {W} days.",
        f"3. **{int((g['profit_to_date'] > 0).sum())} of {len(g)} games** have cumulative GGR × configured share above recorded actual cost; this is not net profit.",
        f"4. **{len(young)} game{'s are' if len(young) != 1 else ' is'} younger than {W} days** and left out of the comparisons.",
        "",
        "## Why age matters",
        "",
        f"Ranking on total GGR rewards old games. Ranking at {W} days aligns time since launch, but does not control for distribution or other differences. Biggest changes:",
        "",
        md_table(top_moves.set_index("title")[["days_live", "rank_total", "rank_fair", "moved"]], []),
        "",
        f"## Patterns (median GGR at {W} days)",
        "",
    ]
    for by, tbl in groups.items():
        lines += [f"### By {by}", "", md_table(tbl, ["median", "low", "high"]), ""]
    lines += [
        "## Schedule (kick off to activation, median weeks)",
        "",
        md_table(slip_vendor, []),
        "",
        "Slip reasons, all milestones:",
        "",
        md_table(reasons.rename("count").to_frame(), []),
        "",
        "## All games",
        "",
        md_table(games_tbl.set_index("title"), ["ggr_30d", col, "actual_eur"]),
        "",
        "## Limits of this review",
        "",
        "- Break-even day is zero-based: 0 is launch day. Revenue share is an assumption; taxes, fees and other unrecorded costs are excluded.",
        "- Correlation only. A family doing well can be the theme, the math, the marketing or luck.",
        f"- Groups with fewer than {min_n} games are flagged and should not drive decisions.",
        "- Exclusive and seasonal games have a different curve. Compare them with their own kind.",
        "",
    ]

    summary = {
        "data_label": cfg.get("data_label", "unverified"),
        "data_date": g.attrs["data_date"],
        "revenue_share": share,
        "main_window_days": W,
        "games": json.loads(g.reset_index().to_json(orient="records", date_format="iso")),
        "groups": {by: json.loads(tbl.reset_index().to_json(orient="records")) for by, tbl in groups.items()},
        "slip_by_vendor": json.loads(slip_vendor.reset_index().to_json(orient="records")),
        "slip_reasons": reasons.to_dict(),
        "facts": {
            "cost_variation_reskin": rounded(cv_cost.get("reskin", float("nan"))),
            "revenue_variation_reskin": rounded(cv_rev.get("reskin", float("nan"))),
            "top_20pct_share_of_ggr": rounded(top20) if top20 is not None else None,
            "games_paid_back": int((g["profit_to_date"] > 0).sum()),
            "games_too_young": young.index.tolist(),
        },
    }
    return "\n".join(lines), summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config.json"))
    ap.add_argument("--output-dir", type=Path, default=HERE)
    ap.add_argument("--overwrite", action="store_true", help="Explicitly replace existing output files")
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    outputs = [args.output_dir / "report.md", args.output_dir / "summary.json"]
    if not args.overwrite and any(p.exists() for p in outputs):
        ap.error("Output already exists. Choose a new --output-dir or explicitly use --overwrite.")
    report, summary = build(cfg)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(summary, indent=2, allow_nan=False)
    outputs[0].write_text(report, encoding="utf-8")
    outputs[1].write_text(encoded, encoding="utf-8")
    print(f"Wrote {outputs[0]} and {outputs[1]}")



if __name__ == "__main__":
    main()
