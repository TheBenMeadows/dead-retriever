#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8"]
# ///
"""Figure 1: the ceiling's firing rate against the keyword leg's natural row
count, one line per collection, from results/*.perquery.jsonl (both hybrid
conditions, all encoders). Writes paper/fig-ceiling-length.pdf and .png.

    scripts/figure.py
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
BUCKETS = [(1, 1), (2, 3), (4, 9), (10, 49), (50, 99), (100, 100)]
LABELS = ["1", "2--3", "4--9", "10--49", "50--99", "100"]
COLL = [("beir_trec-covid", "TREC-COVID"), ("beir_fiqa_test", "FiQA"), ("beir_scidocs", "SciDocs"),
        ("beir_nfcorpus_test", "NFCorpus"), ("beir_scifact_test", "SciFact"), ("beir_arguana", "ArguAna")]
# Categorical hues in fixed order (validated: lightness, chroma, CVD separation).
COLOR = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SMALL = 10  # a bucket with fewer runs than this is drawn hollow


def bucket(n):
    for i, (lo, hi) in enumerate(BUCKETS):
        if lo <= n <= hi:
            return i
    return None


def main():
    counts = defaultdict(lambda: [0, 0])
    for p in sorted(RES.glob("*.perquery.jsonl")):
        coll = p.name.split("__")[0]
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if not r["condition"].startswith("hybrid") or r["n_keyword"] == 0:
                continue
            c = counts[(coll, bucket(r["n_keyword"]))]
            c[1] += 1
            c[0] += int(r["at_ceiling"])
    plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.linewidth": 0.6})
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    x = list(range(len(BUCKETS)))
    for (coll, name), color in zip(COLL, COLOR):
        ys, full, hollow = [], [], []
        for i in x:
            fired, total = counts[(coll, i)]
            y = 100.0 * fired / total if total else float("nan")
            ys.append(y)
            (full if total >= SMALL else hollow).append((i, y))
        ax.plot(x, ys, color=color, linewidth=1.5, label=name, zorder=3)
        if full:
            ax.plot(*zip(*full), linestyle="none", marker="o", markersize=5, color=color, zorder=4)
        if hollow:
            ax.plot(*zip(*hollow), linestyle="none", marker="o", markersize=5, markerfacecolor="white",
                    markeredgecolor=color, markeredgewidth=1.2, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace("--", "–") for l in LABELS])
    ax.set_xlabel("documents returned by the keyword leg")
    ax.set_ylabel("queries at the ceiling (%)")
    ax.set_ylim(-3, 103)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(axis="y", color="#e4e4e0", linewidth=0.6, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper right", ncol=2, handlelength=1.6)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(ROOT / "paper" / f"fig-ceiling-length.{ext}", dpi=200)
    for (coll, name) in COLL:
        print(name, [f"{counts[(coll, i)][0]}/{counts[(coll, i)][1]}" for i in x])


if __name__ == "__main__":
    main()
