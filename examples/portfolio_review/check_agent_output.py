"""Check that every number in an agent's draft can be traced to summary.json.

The performance-review card says: "Every figure can be traced to the data."
This script enforces that rule with code. It does not judge wording or reasoning.

Accepted formats for a value v from summary.json:
  909k / 1,379k  -> v rounded to thousands
  1.4m           -> v rounded to one decimal of millions
  57%            -> v * 100, only for share fields (share, variation, pct, rtp)
  2.6 / 14       -> v at the precision written

Ignored: blockquote lines (provenance notes), list and heading numbers at the
start of a line, game IDs (G030), the data cutoff date, and numbers that are
part of summary field names (for example 90 in ggr_90d, 20 in top_20pct).
"""
import argparse
import json
import re
import sys
from pathlib import Path

NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s?([km%])?(?![\w])", re.IGNORECASE)


SHARE_KEYS = ("share", "variation", "pct", "rtp")


def summary_values(summary) -> tuple[list[float], set[int], list[float]]:
    """Return all numeric values, numbers found in field names, and share-type values."""
    values: list[float] = []
    shares: list[float] = []
    key_numbers: set[int] = set()

    def walk(node, key=""):
        if isinstance(node, dict):
            for k, value in node.items():
                key_numbers.update(int(n) for n in re.findall(r"\d+", str(k)))
                # Explicit percentage labels (top_20pct) encode a percentage;
                # day windows (ggr_90d) do not.
                shares.extend(float(n) / 100 for n in re.findall(r"(\d+(?:\.\d+)?)pct(?:_|$)", str(k)))
                walk(value, str(k))
        elif isinstance(node, list):
            for item in node:
                walk(item, key)
        elif isinstance(node, bool) or node is None:
            return
        elif isinstance(node, (int, float)):
            values.append(float(node))
            if any(s in key.lower() for s in SHARE_KEYS):
                shares.append(float(node))

    walk(summary)
    return values, key_numbers, shares


def _matches(token: float, decimals: int, suffix: str, values: list[float], key_numbers: set[int],
             shares: list[float]) -> bool:
    tol = 0.5 * 10 ** -decimals
    if not suffix and decimals == 0 and int(token) in key_numbers:
        return True
    for v in values:
        if suffix == "k" and abs(v / 1_000 - token) <= tol:
            return True
        if suffix == "m" and abs(v / 1_000_000 - token) <= tol:
            return True
        if not suffix and abs(v - token) <= tol:
            return True
    if suffix == "%":
        if any(abs(v * 100 - token) <= tol for v in shares):
            return True
    return False


def untraceable_numbers(text: str, summary: dict) -> list[str]:
    values, key_numbers, shares = summary_values(summary)
    problems = []
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(">"):
            continue
        stripped = re.sub(r"^(#+\s*)?\d+\.\s", "", stripped)  # list or heading numbers
        stripped = stripped.replace(str(summary.get("data_date", "")), "")
        stripped = re.sub(r"\bG\d+\b", "", stripped)
        for match in NUMBER.finditer(stripped):
            raw, suffix = match.group(1), (match.group(2) or "").lower()
            number = raw.replace(",", "")
            decimals = len(number.split(".")[1]) if "." in number else 0
            if not _matches(float(number), decimals, suffix, values, key_numbers, shares):
                problems.append(f"line {line_no}: {match.group(0).strip()}")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    args = parser.parse_args(argv)

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    problems = untraceable_numbers(args.draft.read_text(encoding="utf-8"), summary)
    if problems:
        print(f"{len(problems)} number(s) not found in {args.summary.name}:")
        for p in problems:
            print("  " + p)
        print("Check these by hand before anyone reads the draft.")
        return 1
    print(f"Numeric presence check passed for {args.draft.name}. Attribution and reasoning still need human review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
