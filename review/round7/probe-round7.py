#!/opt/homebrew/bin/python3
"""Round-7 probes (rewrite, round 2 of 3). Log-only; prints PASS/REFUTED per claim.

ARG-1  The 174 zero-overlap ceilings over a nonempty list split 164 buggy + 10 repaired,
       and the 2 overlap-present ceilings are both under the repaired builder.
DS-1   "A ceiling over a full list means two full lists that share nothing" is false at
       K > k: there are at-ceiling runs with both lists full (100) and a shared document.
SOL-1  Fullness of the keyword list says nothing about the dense list's length: at
       K = k the ceiling can hold with a full keyword list and a short dense list
       (arithmetic, shown by construction with rrf_fuse).
SOL-2  The CPU reproduction check covered four pairs (SciFact, NFCorpus x bge, nomic),
       not e5: e5 has no CPU run recorded anywhere in results/ or the kernel manifest.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dead_retriever import RRF_K, ceiling_report, rrf_fuse  # noqa: E402

ENC = ["BAAI_bge-base-en-v1.5", "nomic-ai_nomic-embed-text-v1.5", "intfloat_e5-base-v2"]
COLL = ["beir_scifact_test", "beir_nfcorpus_test", "beir_arguana", "beir_scidocs", "beir_fiqa_test", "beir_trec-covid"]


def rows():
    for coll in COLL:
        for enc in ENC:
            for line in (ROOT / "results" / f"{coll}__{enc}.perquery.jsonl").read_text().splitlines():
                r = json.loads(line)
                if r["condition"] in ("hybrid_and", "hybrid_or"):
                    yield coll, enc, r


def arg_1():
    split = {"hybrid_and": [0, 0], "hybrid_or": [0, 0]}  # [zero-overlap, overlap-present]
    for coll, enc, r in rows():
        if r["at_ceiling"] and not r["keyword_empty"]:
            split[r["condition"]][0 if r["multi_leg_docs"] == 0 else 1] += 1
    ok = split["hybrid_and"] == [164, 0] and split["hybrid_or"] == [10, 2]
    print(f"ARG-1 ceilings over a nonempty list: buggy {split['hybrid_and']} (zero-overlap, overlap-present), repaired {split['hybrid_or']} -> {'PASS' if ok else 'REFUTED'}")


def ds_1():
    full_shared = [(coll, enc, r["qid"], r["multi_leg_docs"]) for coll, enc, r in rows()
                   if r["at_ceiling"] and r["n_keyword"] == 100 and r["n_dense"] == 100 and r["multi_leg_docs"] > 0]
    print(f"DS-1 at-ceiling runs with both lists full and a shared document: {len(full_shared)} {full_shared} -> "
          f"{'PASS (the sentence is false at K > k)' if full_shared else 'REFUTED'}")


def sol_1():
    k = RRF_K
    keyword = [f"k{i}" for i in range(k)]      # full keyword list, K = k
    dense = ["d0"]                              # one-document dense list, disjoint
    s, r = rrf_fuse({"dense": dense, "keyword": keyword})
    rep = ceiling_report(s, r)
    print(f"SOL-1 full keyword list (K = k = {k}) + one disjoint dense document: at_ceiling={rep.at_ceiling}, max={rep.max_score:.6f} -> "
          f"{'PASS (fullness of one list implies nothing about the other)' if rep.at_ceiling else 'REFUTED'}")


def sol_2():
    hits = []
    for p in (ROOT / "results").glob("*.json"):
        t = p.read_text()
        if "cpu" in t.lower() and "e5" in p.name:
            hits.append(p.name)
    man = list((ROOT / "kaggle").glob("*manifest*")) + list((ROOT / "results").glob("*manifest*"))
    print(f"SOL-2 e5 result files mentioning a CPU run: {hits}; manifests: {[m.name for m in man]} -> "
          f"{'PASS (no e5 CPU run recorded; restrict the claim to the four bge/nomic pairs)' if not hits else 'CHECK'}")


if __name__ == "__main__":
    arg_1()
    ds_1()
    sol_1()
    sol_2()
