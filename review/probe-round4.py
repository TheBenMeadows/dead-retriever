#!/opt/homebrew/bin/python3
"""Round-4 council probes: each reviewer claim about the IRRJ draft that a
script can decide, reproduced against results/ and paper/main.tex.
Prints REPRODUCED / REFUTED with the evidence. Log-only.

    review/probe-round4.py
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
TEX = " ".join((ROOT / "paper" / "main.tex").read_text().split())
ENC = {"bge": "BAAI_bge-base-en-v1.5", "nomic": "nomic-ai_nomic-embed-text-v1.5", "e5": "intfloat_e5-base-v2"}
COLL = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test", "ArguAna": "beir_arguana",
        "SciDocs": "beir_scidocs", "FiQA": "beir_fiqa_test", "TREC-COVID": "beir_trec-covid"}
KF = {f["dataset"]: f for f in json.loads((RES / "keyword_facts.json").read_text())}


def summ(c, e):
    return json.loads((RES / f"{COLL[c]}__{ENC[e]}.json").read_text())


def cond(c, e, k):
    return summ(c, e)["conditions"][k]


def pq(c, e):
    by = defaultdict(dict)
    for line in (RES / f"{COLL[c]}__{ENC[e]}.perquery.jsonl").read_text().splitlines():
        r = json.loads(line)
        by[r["qid"]][r["condition"]] = r
    return by


def say(verdict, name, evidence):
    print(f"{verdict:11s} {name}\n            {evidence}")


def main():
    # P1 ArguAna "never useful": the AND leg retrieved a relevant document on one query.
    rel = KF["beir/arguana"]["and_any_relevant_hit"]
    nd = cond("ArguAna", "bge", "bm25_and")["ndcg_cut_10"]
    say("REPRODUCED" if rel > 0 and "never useful" in TEX else "REFUTED", "P1 'never useful' is contradicted by one relevant AND hit",
        f"and_any_relevant_hit={rel}, bm25_and nDCG@10={nd:.6f}")

    # P2 identical ids are scored (no exclusion), and which collections are exposed.
    src = (ROOT / "scripts" / "beir_run.py").read_text()
    i = src.index("def evaluate(run, qrels):")
    excl = "!= q" in src[i:i + 900]
    say("REPRODUCED" if not excl else "REFUTED", "P2 evaluation keeps a document whose id equals the query id (BEIR drops it)",
        f"exclusion in evaluate(): {excl}; query ids that are corpus ids: ArguAna 1,298/1,406, FiQA 55/648, others 0 (idoverlap probe 10-14)")

    # P3 rounding: prose bounds computed before rounding disagree with the printed tables.
    sf = [(e, cond("SciFact", e, "hybrid_and")["ndcg_cut_10"] - cond("SciFact", e, "dense")["ndcg_cut_10"]) for e in ENC]
    worst = max(sf, key=lambda t: abs(t[1]))
    printed = round(cond("SciFact", "e5", "hybrid_and")["ndcg_cut_10"], 3) - round(cond("SciFact", "e5", "dense")["ndcg_cut_10"], 3)
    say("REPRODUCED" if abs(worst[1]) > 0.002 else "REFUTED", "P3a SciFact 'at most 0.002' exceeds 0.002",
        f"worst {worst[0]} {worst[1]:.6f}; printed-table difference {printed:.3f}")
    nf = cond("NFCorpus", "bge", "hybrid_or")["recall_100"] - cond("NFCorpus", "bge", "dense")["recall_100"]
    say("REPRODUCED" if round(cond("NFCorpus", "bge", "hybrid_or")["recall_100"], 3) == round(cond("NFCorpus", "bge", "dense")["recall_100"], 3) and nf > 0 else "REFUTED",
        "P3b one of the 9 Recall@100 gains prints as a tie", f"NFCorpus bge h-or minus dense = {nf:.6f}")
    ar = cond("ArguAna", "bge", "bm25_or_raw")["ndcg_cut_10"] - cond("ArguAna", "bge", "bm25_or")["ndcg_cut_10"]
    say("REPRODUCED" if abs(ar) > 0.008 else "REFUTED", "P3c 'within 0.008' fails on ArguAna", f"{ar:.6f}")
    ratios = {(c, e): cond(c, e, "bm25_or_raw")["mean_query_ms"] / cond(c, e, "bm25_or")["mean_query_ms"] for c in COLL for e in ENC}
    lo = min(ratios, key=ratios.get)
    say("REPRODUCED" if round(ratios[lo], 1) < 2.6 else "REFUTED", "P3d '2.6 to 18 times' lower end is below 2.6 over all runs",
        f"min {lo} {ratios[lo]:.3f}; bge-only min {min(v for (c, e), v in ratios.items() if e == 'bge'):.3f}")
    say("REPRODUCED", "P3e 4/6,636 printed as 0.1%", f"{100 * 4 / 6636:.3f}%")

    # P4 SciFact omitted from the per-collection short-list rates; corpus size is not monotone with it.
    nat = json.loads((RES / "natural_lengths.json").read_text())["by_collection"]
    sfs = nat["beir_scifact_test"]["1-3"]
    say("REPRODUCED" if "SciFact" not in TEX[TEX.index("13 of 330"):TEX.index("13 of 330") + 200] else "REFUTED",
        "P4 SciFact (0/18 short-list firings at 5.2k docs) omitted from the corpus-size list", f"SciFact 1-3: {sfs}")

    # P5 collinearity: corpus size does not follow the content-token ordering.
    order = ["SciFact", "SciDocs", "FiQA", "TREC-COVID", "NFCorpus"]
    sizes = [summ(c, "bge")["n_docs"] for c in order]
    mono = sizes == sorted(sizes) or sizes == sorted(sizes, reverse=True)
    say("REPRODUCED" if not mono and "corpus size, document length and vocabulary differ along the same ordering" in TEX else "REFUTED",
        "P5 'corpus size ... differ along the same ordering' is false for corpus size", f"sizes in content-token order: {sizes}")

    # P6 "live on more queries the hybrid did move" illustrated by TREC-COVID (13 live) vs SciDocs (58 live).
    live = {c: sum(1 for r in pq(c, "bge").values() if not r["hybrid_and"]["keyword_empty"]) for c in ("NFCorpus", "SciDocs", "TREC-COVID")}
    say("REPRODUCED" if live["TREC-COVID"] < live["SciDocs"] else "REFUTED", "P6 'live on more queries' contradicted by TREC-COVID", f"live AND legs {live}")

    # P7 pooled length buckets mix builders; share of the 1-3 bucket from the buggy builder.
    mix = defaultdict(lambda: [0, 0])
    for c in COLL:
        if c == "ArguAna":
            continue
        for e in ENC:
            for r in pq(c, e).values():
                for hyb in ("hybrid_and", "hybrid_or"):
                    n = r[hyb]["n_keyword"]
                    if 1 <= n <= 3:
                        mix[hyb][1] += 1
                        mix[hyb][0] += int(r[hyb]["at_ceiling"])
    tot = mix["hybrid_and"][1] + mix["hybrid_or"][1]
    say("REPRODUCED", "P7 the 1-3 bucket pools both builders",
        f"buggy {mix['hybrid_and'][0]}/{mix['hybrid_and'][1]} fired, fixed {mix['hybrid_or'][0]}/{mix['hybrid_or'][1]} fired; buggy share {100 * mix['hybrid_and'][1] / tot:.0f}%")

    # P8 TREC-COVID 16/18 short-list runs are six distinct queries.
    q = set()
    for e in ENC:
        for qid, r in pq("TREC-COVID", e).items():
            for hyb in ("hybrid_and", "hybrid_or"):
                if 1 <= r[hyb]["n_keyword"] <= 3:
                    q.add(qid)
    say("REPRODUCED" if len(q) == 6 else "REFUTED", "P8 TREC-COVID short-list runs are six queries", f"{len(q)} distinct queries")

    # P9 abstract "restores overlap on every collection": ArguAna already overlapped.
    a = cond("ArguAna", "bge", "hybrid_and")["multi_leg_docs_mean"]
    say("REPRODUCED" if a >= 1 and "restores overlap on every collection" in TEX else "REFUTED", "P9 'restores overlap' wrong for ArguAna", f"ArguAna hybrid-and both-leg mean {a:.4f}")

    # P10 the mechanism sentence: in how many of the 12 buggy>repaired pairs is the buggy hybrid also above dense?
    wins = [(c, e) for c in COLL for e in ENC if cond(c, e, "hybrid_and")["ndcg_cut_10"] - cond(c, e, "hybrid_or")["ndcg_cut_10"] >= 0.0005]
    above = [(c, e) for c, e in wins if cond(c, e, "hybrid_and")["ndcg_cut_10"] - cond(c, e, "dense")["ndcg_cut_10"] >= 0.0005]
    say("REPRODUCED" if len(above) <= 4 else "REFUTED", "P10 the 12 buggy>repaired pairs are mostly abstention, not exact-match gains",
        f"{len(wins)} pairs; buggy hybrid also above dense in {len(above)}: {above}")

    # P11 'rank one' vs Section 2's 0-based ranks; 'chunk or abstract' on BEIR; doc2query superlative; CombSUM.
    say("REPRODUCED" if "at rank one on 1\\,296" in TEX else "REFUTED", "P11a 'rank one' against 0-based ranks in Section 2", "")
    say("REPRODUCED" if "1\\,400-character chunk or one abstract" in TEX else "REFUTED", "P11b production chunk size applied to BEIR", "")
    say("REPRODUCED" if "cheapest form of document expansion \\citep{nogueira2019doc2query}" in TEX else "REFUTED", "P11c doc2query cited for a superlative it does not make", "")
    say("REPRODUCED" if "CombSUM and CombMNZ \\citep{fox1994combination} reward documents returned by several systems" in TEX else "REFUTED",
        "P11d CombSUM credited with CombMNZ's multi-system reward", "")

    # Claims judged wrong (exonerations).
    k = 60
    rel_single = (1 / (k) - 1 / (k + 1)) / (1 / k)
    rel_double = (2 / (k) - 2 / (k + 1)) / (2 / k)
    say("REFUTED", "X1 (agyx) 'same step at twice the scale' is false",
        f"relative step single {rel_single:.5f} = double {rel_double:.5f}; absolute doubles. The sentence says exactly that.")
    say("REFUTED", "X2 (agyx) abstract lacks K<=k before 'therefore'", "the preceding sentence sets 'with per-retriever depth K <= k'; 'therefore' carries it")


if __name__ == "__main__":
    main()
