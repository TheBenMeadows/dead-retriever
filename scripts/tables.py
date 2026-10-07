#!/opt/homebrew/bin/python3
"""Print the paper's BEIR table rows and the per-query facts the text cites,
from results/*.json and results/*.perquery.jsonl.

    scripts/tables.py            # both encoders, rows + facts
"""
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
ENC = {"bge": "BAAI_bge-base-en-v1.5", "nomic": "nomic-ai_nomic-embed-text-v1.5"}
COLL = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test"}
ORDER = ["bm25_and", "bm25_or_raw", "bm25_or", "dense", "hybrid_and", "hybrid_or"]
LABEL = {c: c.replace("_", "-") for c in ORDER}


def pct(x):
    return f"{100 * x:.1f}\\%"


def rows(enc, conds):
    for coll, prefix in COLL.items():
        d = json.loads((R / f"{prefix}__{ENC[enc]}.json").read_text())["conditions"]
        for c in conds:
            r = d[c]
            cells = [coll, LABEL[c], f"{r['ndcg_cut_10']:.3f}", f"{r['recall_100']:.3f}", f"{r['mean_query_ms']:.1f}"]
            if c.startswith("bm25"):
                cells += [pct(r["empty_rate"]), "--", "--"]
            elif c == "dense":
                cells += ["--", "--", "--"]
            else:
                cells += [pct(r["keyword_empty_rate"]), pct(r["at_ceiling_rate"]), f"{r['multi_leg_docs_mean']:.2f}" if r["multi_leg_docs_mean"] < 1 else f"{r['multi_leg_docs_mean']:.1f}"]
            print(" & ".join(cells) + r" \\")
        print(r"\midrule")


def perquery(enc):
    """Facts about individual queries that the aggregate means cannot give."""
    for coll, prefix in COLL.items():
        by = defaultdict(dict)
        for line in (R / f"{prefix}__{ENC[enc]}.perquery.jsonl").read_text().splitlines():
            row = json.loads(line)
            by[row["qid"]][row["condition"]] = row
        n = len(by)
        for hyb in ("hybrid_and", "hybrid_or"):
            empty = [q for q, r in by.items() if r[hyb]["keyword_empty"]]
            ceiling = [q for q, r in by.items() if r[hyb]["at_ceiling"]]
            excess = [q for q in ceiling if q not in empty]
            missed = [q for q in empty if q not in ceiling]
            nonempty = n - len(empty)
            overlap_of_excess = [by[q][hyb]["multi_leg_docs"] for q in excess]
            kw_sizes = [by[q][hyb]["n_keyword"] for q in excess]
            print(f"{enc} {coll} {hyb}: n={n} empty={len(empty)} ceiling={len(ceiling)} excess={len(excess)} "
                  f"missed={len(missed)} excess/nonempty={len(excess)}/{nonempty}={100*len(excess)/max(1,nonempty):.1f}% "
                  f"excess multi_leg_docs={overlap_of_excess} excess n_keyword={kw_sizes}")
        # On empty-leg queries, hybrid_and's fused list is dense's list: same n and max score 1/60.
        same = sum(1 for q, r in by.items() if r["hybrid_and"]["keyword_empty"]
                   and abs(r["hybrid_and"]["max_score"] - 1 / 60) < 1e-12 and r["hybrid_and"]["n_dense"] == r["dense"]["n_dense"])
        print(f"{enc} {coll}: empty-leg queries where hybrid_and max=1/60 and dense count matches: {same}")


if __name__ == "__main__":
    print("% Table 2 (bge)")
    rows("bge", ORDER)
    print("% Table 3 (nomic)")
    rows("nomic", ["dense", "hybrid_and", "hybrid_or"])
    print("% per-query facts")
    perquery("bge")
    perquery("nomic")
