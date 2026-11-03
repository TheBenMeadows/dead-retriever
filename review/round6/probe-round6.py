#!/opt/homebrew/bin/python3
"""Round-6 probes (rewrite, round 1 of 3). Log-only; prints PASS/REFUTED per claim.

K3-1  The stopword-drop sentence quotes raw-difference roundings (0.010, 0.012) where
      the stated rule is differences of printed three-decimal values (0.011, 0.013).
CDX-2 With two retrievers, every nonempty fused list has max >= 1/k, so "<= 1/k" and
      "= 1/k" coincide on nonempty lists; no at-ceiling row has both lists empty.
CDX-4 The abstract's "174 nonempty keyword lists" counts hybrid query runs, and the
      same keyword list recurs across encoders: count distinct (collection, builder, qid).
ARG-1 The OR builders quote each token (so "no quoted token matches" is true of OR too).
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = {p.name: json.loads(p.read_text()) for p in (ROOT / "results").glob("beir_*.json") if not p.name.endswith(".sweep.json")}
ENC = ["BAAI_bge-base-en-v1.5", "nomic-ai_nomic-embed-text-v1.5", "intfloat_e5-base-v2"]
COLL = ["beir_scifact_test", "beir_nfcorpus_test", "beir_arguana", "beir_scidocs", "beir_fiqa_test", "beir_trec-covid"]


def r3(x):
    return round(x + 0.0, 3)


def cond(coll, enc, c):
    return RES[f"{coll}__{enc}.json"]["conditions"][c]


def k3_rounding():
    fi_raw, fi_or = cond("beir_fiqa_test", ENC[0], "bm25_or_raw"), cond("beir_fiqa_test", ENC[0], "bm25_or")
    printed = round(r3(fi_raw["recall_100"]) - r3(fi_or["recall_100"]), 3)
    raw = r3(fi_raw["recall_100"] - fi_or["recall_100"])
    print(f"K3-1 FiQA R@100 raw-OR minus OR: printed-values diff {printed}, raw diff {raw} -> "
          f"{'REFUTED' if printed == raw else 'PASS (text said ' + str(raw) + ', rule gives ' + str(printed) + ')'}")
    worst = []
    for coll in COLL:
        if coll == "beir_fiqa_test":
            continue
        a, b = cond(coll, ENC[0], "bm25_or_raw"), cond(coll, ENC[0], "bm25_or")
        worst.append((coll, round(r3(b["ndcg_cut_10"]) - r3(a["ndcg_cut_10"]), 3), r3(b["ndcg_cut_10"] - a["ndcg_cut_10"])))
    hi_p, hi_r = max(w[1] for w in worst), max(w[2] for w in worst)
    print(f"K3-1 nDCG@10 OR minus raw-OR, five collections: printed-values max {hi_p}, raw max {hi_r}; per collection {worst} -> "
          f"{'REFUTED' if hi_p == hi_r else 'PASS (text said 0.010, rule gives ' + str(hi_p) + ')'}")


def perquery():
    rows = defaultdict(list)
    for coll in COLL:
        for enc in ENC:
            for line in (ROOT / "results" / f"{coll}__{enc}.perquery.jsonl").read_text().splitlines():
                r = json.loads(line)
                rows[(coll, enc)].append(r)
    return rows


def cdx_2(rows):
    k = 60
    below = both_empty = 0
    n = 0
    for (coll, enc), rs in rows.items():
        for r in rs:
            if r["condition"] not in ("hybrid_and", "hybrid_or"):
                continue
            n += 1
            if r["n_dense"] + r["n_keyword"] > 0 and r["max_score"] < 1 / k - 1e-12:
                below += 1
            if r["at_ceiling"] and r["n_dense"] == 0 and r["n_keyword"] == 0:
                both_empty += 1
    print(f"CDX-2 {n} hybrid runs: nonempty fused lists with max < 1/k: {below}; at-ceiling rows with both lists empty: {both_empty} -> "
          f"{'PASS' if below == 0 and both_empty == 0 else 'REFUTED'}")


def cdx_4(rows):
    runs, lists = 0, set()
    for (coll, enc), rs in rows.items():
        for r in rs:
            if r["condition"] in ("hybrid_and", "hybrid_or") and r["at_ceiling"] and not r["keyword_empty"] and r["multi_leg_docs"] == 0:
                runs += 1
                lists.add((coll, r["condition"], r["qid"]))
    print(f"CDX-4 zero-overlap ceilings over a nonempty keyword list: {runs} query runs over {len(lists)} distinct (collection, builder, query) keyword lists -> "
          f"{'PASS (the unit is runs, not lists)' if runs != len(lists) else 'REFUTED'}")


def arg_1():
    src = (ROOT / "dead_retriever" / "hybrid.py").read_text()
    m = re.findall(r"def (or_raw|or_bm25|and_quoted)\b.*?(?=\ndef |\Z)", src, re.S)
    quoted = {name: ('f\'"{' in body or '"\'"\'' in body or 'f"\\"{' in body or "'\"'" in body) for name, body in
              [(mm, src[src.index(f"def {mm}"):].split("\ndef ")[0]) for mm in m]}
    print(f"ARG-1 builders that quote each token: {quoted} -> {'PASS' if all(quoted.get(b) for b in ('or_raw', 'or_bm25')) else 'CHECK BY HAND'}")


if __name__ == "__main__":
    k3_rounding()
    rows = perquery()
    cdx_2(rows)
    cdx_4(rows)
    arg_1()
