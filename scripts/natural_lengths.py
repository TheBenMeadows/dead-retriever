#!/opt/homebrew/bin/python3
"""Ceiling rate conditional on the keyword leg's NATURAL row count, from the
per-query rows written by beir_run.py (both hybrid conditions, K = 100).
This is what an operator sees: the leg returned n documents on its own, and
the ceiling did or did not fire. The truncation sweep (sweep_live_list.py)
measures a cap instead.

    scripts/natural_lengths.py
"""
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
BUCKETS = [(1, 1), (2, 3), (4, 9), (10, 49), (50, 99), (100, 100)]


def bucket(n):
    for lo, hi in BUCKETS:
        if lo <= n <= hi:
            return f"{lo}" if lo == hi else f"{lo}-{hi}"
    return None


def main():
    agg = defaultdict(lambda: [0, 0])  # bucket -> [fired, total]
    per_file = {}
    for p in sorted(R.glob("*.perquery.jsonl")):
        local = defaultdict(lambda: [0, 0])
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if not r["condition"].startswith("hybrid") or r["n_keyword"] == 0:
                continue
            b = bucket(r["n_keyword"])
            for d in (agg, local):
                d[b][1] += 1
                d[b][0] += int(r["at_ceiling"])
        per_file[p.name] = {b: (f, t) for b, (f, t) in local.items()}
    out = {"buckets": [], "per_file": per_file}
    for lo, hi in BUCKETS:
        b = f"{lo}" if lo == hi else f"{lo}-{hi}"
        f, t = agg[b]
        out["buckets"].append({"n_keyword": b, "fired": f, "total": t, "rate": f / t if t else None})
        print(f"n_keyword={b:>6}: fired {f:4d} / {t:5d} = {100*f/t if t else float('nan'):5.1f}%")
    (R / "natural_lengths.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
