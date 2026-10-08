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


def load(cfg: dict) -> dict[str, pd.DataFrame]:
    d = (HERE / cfg["data_dir"]).resolve()
    t = {name: pd.read_csv(d / f"{name}.csv") for name in ["games", "costs", "milestones", "daily_performance"]}
    t["games"]["launch_date"] = pd.to_datetime(t["games"]["launch_date"])
    t["daily_performance"]["date"] = pd.to_datetime(t["daily_performance"]["date"])
    for c in ["planned_date", "actual_date"]:
        t["milestones"][c] = pd.to_datetime(t["milestones"][c])
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
    n_top = max(1, round(len(top_share) * 0.2))
    top20 = top_share.head(n_top).sum() / top_share.sum()

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
        "> Generated by `analyze.py`. All figures in EUR. Data in this repo is fictional.",
        "",
        "## Key facts",
        "",
        f"1. **Cost is predictable, revenue is not.** Cost varies by {cv_cost.get('reskin', float('nan')):.0%} between reskins; "
        f"GGR at {W} days varies by {cv_rev.get('reskin', float('nan')):.0%}.",
        f"2. **A few games make most of the money.** The top {n_top} games ({n_top/len(top_share):.0%}) make "
        f"{top20:.0%} of GGR at {W} days.",
        f"3. **{int((g['profit_to_date'] > 0).sum())} of {len(g)} games** have paid back their cost so far.",
        f"4. **{len(young)} game{'s are' if len(young) != 1 else ' is'} younger than {W} days** and left out of the comparisons.",
        "",
        "## Why age matters",
        "",
        f"Ranking on total GGR rewards old games. Ranking at {W} days is fair. Biggest changes:",
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
        "- Correlation only. A family doing well can be the theme, the math, the marketing or luck.",
        f"- Groups with fewer than {min_n} games are flagged and should not drive decisions.",
        "- Exclusive and seasonal games have a different curve. Compare them with their own kind.",
        "",
    ]

    summary = {
        "data_date": g.attrs["data_date"],
        "revenue_share": share,
        "main_window_days": W,
        "games": json.loads(g.reset_index().to_json(orient="records", date_format="iso")),
        "groups": {by: json.loads(tbl.reset_index().to_json(orient="records")) for by, tbl in groups.items()},
        "slip_by_vendor": json.loads(slip_vendor.reset_index().to_json(orient="records")),
        "slip_reasons": reasons.to_dict(),
        "facts": {
            "cost_variation_reskin": round(float(cv_cost.get("reskin", float("nan"))), 3),
            "revenue_variation_reskin": round(float(cv_rev.get("reskin", float("nan"))), 3),
            "top_20pct_share_of_ggr": round(float(top20), 3),
            "games_paid_back": int((g["profit_to_date"] > 0).sum()),
            "games_too_young": young.index.tolist(),
        },
    }
    return "\n".join(lines), summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config.json"))
    cfg = json.loads(Path(ap.parse_args().config).read_text())
    report, summary = build(cfg)
    (HERE / "report.md").write_text(report, encoding="utf-8")
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {HERE/'report.md'} and {HERE/'summary.json'}")


if __name__ == "__main__":
    main()
