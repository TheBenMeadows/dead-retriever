#!/opt/homebrew/bin/python3
"""Ceiling rate conditional on the keyword leg's NATURAL row count, from the
per-query rows written by beir_run.py (both hybrid conditions, K = 100).
This is what an operator sees: the leg returned n documents on its own, and
the ceiling did or did not fire. The truncation sweep (sweep_live_list.py)
measures a cap instead.

Rates are given per collection and pooled over every collection except
ArguAna, whose quoted-AND leg returns the query's own document and so is
never disjoint from the dense leg (results/keyword_facts.json).

    scripts/natural_lengths.py
"""
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
BUCKETS = [(1, 3), (4, 49), (50, 100)]
SET_ASIDE = "beir_arguana"


def bucket(n):
    for lo, hi in BUCKETS:
        if lo <= n <= hi:
            return f"{lo}-{hi}"
    return None


def main():
    pooled = defaultdict(lambda: [0, 0])  # bucket -> [fired, total]
    by_coll = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for p in sorted(R.glob("*.perquery.jsonl")):
        coll = p.name.split("__")[0]
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if not r["condition"].startswith("hybrid") or r["n_keyword"] == 0:
                continue
            b = bucket(r["n_keyword"])
            targets = [by_coll[coll][b]] + ([] if coll == SET_ASIDE else [pooled[b]])
            for t in targets:
                t[1] += 1
                t[0] += int(r["at_ceiling"])
    out = {"pooled_without": SET_ASIDE, "buckets": [], "by_collection": {}}
    for lo, hi in BUCKETS:
        b = f"{lo}-{hi}"
        f, t = pooled[b]
        out["buckets"].append({"n_keyword": b, "fired": f, "total": t, "rate": f / t if t else None})
        print(f"pooled n_keyword={b:>6}: fired {f:4d} / {t:5d} = {100*f/t if t else float('nan'):5.1f}%")
    for coll, bs in sorted(by_coll.items()):
        out["by_collection"][coll] = {b: {"fired": f, "total": t} for b, (f, t) in bs.items()}
        print(coll, {b: f"{f}/{t}" for b, (f, t) in bs.items()})
    (R / "natural_lengths.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
