#!/opt/homebrew/bin/python3
"""Paired randomization tests on the effectiveness comparisons, from
results/*.pereval.jsonl (one row per query and condition, written by
beir_run.py). Writes results/significance.json.

For each collection-encoder pair, metric (nDCG@10, Recall@100) and comparison
(hybrid-or vs dense, hybrid-and vs dense, hybrid-and vs hybrid-or): the mean
paired difference and a two-sided p-value from a sign-flip randomization test
(Smucker, Allan and Carterette 2007) with R random flips, seeded. Holm's
correction is applied within each family of 18 pairs (one family per metric
and comparison).

    scripts/significance.py [--trials 100000]
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
METRICS = ("ndcg_cut_10", "recall_100")
COMPARISONS = (("hybrid_or", "dense"), ("hybrid_and", "dense"), ("hybrid_and", "hybrid_or"))
SEED = 20261014


def randomization_p(diffs, trials, rng):
    """Two-sided p-value of the mean paired difference under random sign flips.
    The observed assignment counts as one trial, so p is never zero."""
    n = len(diffs)
    if n == 0:
        return 1.0
    obs = abs(sum(diffs)) / n
    if obs == 0.0:
        return 1.0
    hits = 1
    for _ in range(trials):
        s = 0.0
        for d in diffs:
            s += d if rng.random() < 0.5 else -d
        if abs(s) / n >= obs - 1e-15:
            hits += 1
    return hits / (trials + 1)


def holm(pvals):
    """Holm-adjusted p-values, same order as the input."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    m = len(pvals)
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def load(path):
    by = defaultdict(dict)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        by[r["condition"]][r["qid"]] = r
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=100000)
    a = ap.parse_args()
    rng = random.Random(SEED)
    rows = []
    for path in sorted(R.glob("*.pereval.jsonl")):
        tag = path.name[: -len(".pereval.jsonl")]
        by = load(path)
        for m in METRICS:
            for x, y in COMPARISONS:
                qids = sorted(set(by[x]) & set(by[y]))
                diffs = [by[x][q][m] - by[y][q][m] for q in qids]
                rows.append({"tag": tag, "metric": m, "a": x, "b": y, "n": len(qids),
                             "mean_diff": sum(diffs) / len(diffs) if diffs else 0.0,
                             "p": randomization_p(diffs, a.trials, rng)})
    fam = defaultdict(list)
    for i, r in enumerate(rows):
        fam[(r["metric"], r["a"], r["b"])].append(i)
    for idx in fam.values():
        for i, p in zip(idx, holm([rows[i]["p"] for i in idx])):
            rows[i]["p_holm"] = p
    out = {"test": "paired sign-flip randomization, two-sided", "trials": a.trials, "seed": SEED,
           "correction": "Holm within each (metric, comparison) family", "rows": rows}
    (R / "significance.json").write_text(json.dumps(out, indent=1) + "\n")
    for r in rows:
        print(f"{r['tag']:55s} {r['metric']:12s} {r['a']:>10s}-{r['b']:<10s} n={r['n']:5d} d={r['mean_diff']:+.4f} p={r['p']:.4f} holm={r['p_holm']:.4f}")


if __name__ == "__main__":
    main()
