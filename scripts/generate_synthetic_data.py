"""Generate fictional slot studio data that follows the schema in /schema.

Everything here is invented: game titles, families, vendors, costs and
performance. The goal is realistic *shape*, not realistic numbers:

- costs are fairly stable, revenue is very uneven (a few hits make most money)
- reskins are cheaper and faster than originals
- milestones slip, with a reason
- games launch on different dates, so their ages differ

Usage:
    python scripts/generate_synthetic_data.py [--seed 7] [--games 30]
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "synthetic"
DATA_DATE = date(2026, 9, 30)

FAMILIES = {
    # family: (theme, mechanic, volatility, hidden appeal factor)
    "Ember Fang": ("dragons", "hold_and_win", "high", 1.8),
    "Lucky Lagoon": ("fishing", "lines", "medium", 1.3),
    "Iron Crown": ("medieval", "ways", "high", 1.0),
    "Moon Orchard": ("fantasy", "cluster", "medium", 0.7),
    "Thunder Hogs": ("animals", "hold_and_win", "very_high", 1.1),
    "Neon Bazaar": ("retro", "lines", "low", 0.5),
}
TITLE_WORDS = ["Riches", "Vault", "Rush", "Legends", "Deluxe", "Frenzy", "Gold", "Quest", "Bonanza", "Nights"]
VENDORS = {
    # vendor: (cost factor, mean slip weeks)
    "Vendor North": (1.00, 1.5),
    "Vendor South": (0.85, 3.5),
    "in_house": (1.20, 2.0),
}
SLIP_REASONS = ["scope_change", "art_revisions", "vendor_capacity", "cert_findings", "math_changes"]
MILESTONES = [  # name, planned weeks after previous (original, reskin)
    ("kick_off", 0, 0),
    ("initial_prototype", 4, 2),
    ("client_prototype", 4, 2),
    ("alpha", 4, 2),
    ("beta", 6, 2),
    ("gold", 3, 1),
    ("master", 2, 1),
    ("certification", 3, 2),
    ("production", 2, 2),
    ("activation", 6, 6),
]
COST_BASE = {  # discipline: (original, reskin) budget in EUR
    "art": (60000, 18000),
    "animation": (35000, 10000),
    "front_end": (40000, 8000),
    "math": (25000, 2000),
    "audio": (9000, 4500),
    "qa": (15000, 5000),
    "certification": (6000, 5000),
    "translation": (4000, 4000),
    "production": (12000, 5000),
    "tools": (1000, 700),
}


def make_games(rng: random.Random, n: int) -> list[dict]:
    games, used = [], set()
    originals: dict[str, str] = {}
    start = date(2024, 1, 15)
    span = (DATA_DATE - timedelta(days=21) - start).days
    launches = sorted(start + timedelta(days=rng.randint(0, span)) for _ in range(n))
    for i, launch in enumerate(launches, 1):
        family = rng.choice(list(FAMILIES))
        theme, mechanic, vol, _ = FAMILIES[family]
        is_original = family not in originals or rng.random() < 0.15
        while True:
            title = f"{family} {rng.choice(TITLE_WORDS)}"
            if title not in used:
                used.add(title)
                break
        gid = f"G{i:03d}"
        seasonal = rng.random() < 0.15
        if seasonal:
            title += " Winter Edition"
        games.append({
            "game_id": gid,
            "title": title,
            "type": "original" if is_original else "reskin",
            "base_game_id": None if is_original else originals[family],
            "family": family,
            "theme": theme,
            "mechanic": mechanic,
            "volatility": vol,
            "rtp_theoretical": rng.choice([0.94, 0.95, 0.96, 0.96, 0.96]),
            "vendor": "in_house" if is_original and rng.random() < 0.6 else rng.choice(["Vendor North", "Vendor South"]),
            "launch_date": launch.isoformat(),
            "exclusive": rng.random() < 0.25,
            "seasonal": seasonal,
        })
        originals.setdefault(family, gid)
    return games


def make_costs(rng: random.Random, games: list[dict]) -> list[dict]:
    rows = []
    for g in games:
        k = 0 if g["type"] == "original" else 1
        vf = VENDORS[g["vendor"]][0]
        for disc, base in COST_BASE.items():
            budget = base[k] * (vf if disc in ("art", "animation", "front_end", "qa") else 1.0)
            actual = budget * rng.lognormvariate(0.03, 0.10)
            rows.append({"game_id": g["game_id"], "discipline": disc,
                         "budget_eur": round(budget, -1), "actual_eur": round(actual, -1)})
    return rows


def make_milestones(rng: random.Random, games: list[dict]) -> list[dict]:
    rows = []
    for g in games:
        k = 1 if g["type"] == "original" else 2
        mean_slip = VENDORS[g["vendor"]][1]
        weeks_to_activation = sum(m[k] for m in MILESTONES)
        # actual slips accumulate; work back from the real launch (activation)
        slips = [0.0] + [max(0.0, rng.gauss(mean_slip / 6, 0.8)) if rng.random() < 0.45 else 0.0
                         for _ in MILESTONES[1:]]
        total_slip = sum(slips)
        activation = date.fromisoformat(g["launch_date"])
        kick_off = activation - timedelta(weeks=weeks_to_activation + total_slip)
        planned = actual = kick_off
        for (name, *w), slip in zip(MILESTONES, slips):
            planned = planned + timedelta(weeks=w[k - 1])
            actual = actual + timedelta(weeks=w[k - 1] + slip)
            rows.append({
                "game_id": g["game_id"], "milestone": name,
                "planned_date": planned.isoformat(), "actual_date": actual.isoformat(),
                "slip_reason": rng.choice(SLIP_REASONS) if slip >= 0.5 else None,
            })
    return rows


def make_performance(rng: random.Random, games: list[dict]) -> list[dict]:
    rows = []
    for g in games:
        appeal = FAMILIES[g["family"]][3]
        luck = rng.lognormvariate(0, 0.9)  # most of the spread: hits are rare
        peak_bets = 45000 * appeal * luck * (1.15 if g["type"] == "original" else 1.0)
        house_edge = 1 - g["rtp_theoretical"]
        launch = date.fromisoformat(g["launch_date"])
        d = launch
        day = 0
        while d <= DATA_DATE:
            ramp = min(1.0, (day + 1) / 10)
            decay = math.exp(-day / (60 if g["seasonal"] else 420))
            if g["seasonal"] and day > 75:
                decay *= 0.3
            excl = 0.35 if g["exclusive"] and day < 28 else 1.0
            weekend = 1.15 if d.weekday() >= 5 else 1.0
            bets = peak_bets * ramp * (0.25 + 0.75 * decay) * excl * weekend * rng.uniform(0.85, 1.15)
            # daily RTP noise is larger for high volatility games
            sd = {"low": 0.02, "medium": 0.04, "high": 0.07, "very_high": 0.10}[g["volatility"]]
            ggr = bets * (house_edge + rng.gauss(0, sd))
            rows.append({"game_id": g["game_id"], "date": d.isoformat(),
                         "bets_eur": round(bets, 2), "ggr_eur": round(ggr, 2)})
            d += timedelta(days=1)
            day += 1
    return rows


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--games", type=int, default=30)
    a = p.parse_args()
    rng = random.Random(a.seed)
    games = make_games(rng, a.games)
    write("games", games)
    write("costs", make_costs(rng, games))
    write("milestones", make_milestones(rng, games))
    write("daily_performance", make_performance(rng, games))
    print(f"Data date: {DATA_DATE}. All data is fictional.")


if __name__ == "__main__":
    main()
