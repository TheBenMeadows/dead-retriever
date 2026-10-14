#!/opt/homebrew/bin/python3
"""Print the paper's BEIR table rows and the per-query facts the text cites,
from results/*.json, results/*.perquery.jsonl and results/keyword_facts.json.

    scripts/tables.py            # all tables, then per-query facts
"""
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"
ENC = {"bge": "BAAI_bge-base-en-v1.5", "nomic": "nomic-ai_nomic-embed-text-v1.5", "e5": "intfloat_e5-base-v2"}
COLL = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test", "ArguAna": "beir_arguana",
        "SciDocs": "beir_scidocs", "FiQA": "beir_fiqa_test", "TREC-COVID": "beir_trec-covid"}
DATASET = {"SciFact": "beir/scifact/test", "NFCorpus": "beir/nfcorpus/test", "ArguAna": "beir/arguana",
           "SciDocs": "beir/scidocs", "FiQA": "beir/fiqa/test", "TREC-COVID": "beir/trec-covid"}
ORDER = ["bm25_and", "bm25_or_raw", "bm25_or", "dense", "hybrid_and", "hybrid_or"]
LABEL = {c: c.replace("_", "-") for c in ORDER}


def pct(x):
    return f"{100 * x:.1f}\\%"


def summary(coll, enc):
    return json.loads((R / f"{COLL[coll]}__{ENC[enc]}.json").read_text())


def perquery_rows(coll, enc):
    by = defaultdict(dict)
    for line in (R / f"{COLL[coll]}__{ENC[enc]}.perquery.jsonl").read_text().splitlines():
        row = json.loads(line)
        by[row["qid"]][row["condition"]] = row
    return by


def kfacts():
    return {f["dataset"]: f for f in json.loads((R / "keyword_facts.json").read_text())}


def legs_table():
    """Table 2: the keyword leg and the ceiling, per collection. Encoder-dependent
    columns (at ceiling) are given as the range over the three encoders."""
    kf = kfacts()
    for coll in COLL:
        s = summary(coll, "bge")
        f = kf[DATASET[coll]]
        cells = [coll, f"{s['n_docs']:,}".replace(",", "\\,"), f"{s['n_queries']:,}".replace(",", "\\,"),
                 f"{f['tokens_mean']:.1f}"]
        for hyb in ("hybrid_and", "hybrid_or"):
            empties = {summary(coll, e)["conditions"][hyb]["keyword_empty_rate"] for e in ENC}
            assert len(empties) == 1, (coll, hyb, empties)
            ceil = sorted(summary(coll, e)["conditions"][hyb]["at_ceiling_rate"] for e in ENC)
            rng = pct(ceil[0]) if ceil[0] == ceil[-1] else f"{100 * ceil[0]:.1f}--{pct(ceil[-1])}"
            cells += [pct(empties.pop()), rng]
        print(" & ".join(cells) + r" \\")


def effect_table(metric):
    """Table 3/4: dense, hybrid-and, hybrid-or per collection and encoder."""
    for coll in COLL:
        cells = [coll]
        for enc in ENC:
            c = summary(coll, enc)["conditions"]
            cells += [f"{c[k][metric]:.3f}" for k in ("dense", "hybrid_and", "hybrid_or")]
        print(" & ".join(cells) + r" \\")


def full_table(enc):
    """Appendix: all six conditions for one encoder (no timing column; the
    SciFact and NFCorpus runs were timed on a different machine)."""
    for coll in COLL:
        d = summary(coll, enc)["conditions"]
        for c in ORDER:
            r = d[c]
            cells = [coll, LABEL[c], f"{r['ndcg_cut_10']:.3f}", f"{r['recall_100']:.3f}"]
            if c.startswith("bm25"):
                cells += [pct(r["empty_rate"]), "--", "--"]
            elif c == "dense":
                cells += ["--", "--", "--"]
            else:
                m = r["multi_leg_docs_mean"]
                cells += [pct(r["keyword_empty_rate"]), pct(r["at_ceiling_rate"]), f"{m:.2f}" if m < 1 else f"{m:.1f}"]
            print(" & ".join(cells) + r" \\")
        print(r"\midrule")


def perquery_facts():
    """Facts about individual queries that the aggregate means cannot give."""
    tot = defaultdict(int)
    for coll in COLL:
        for enc in ENC:
            by = perquery_rows(coll, enc)
            n = len(by)
            for hyb in ("hybrid_and", "hybrid_or"):
                empty = [q for q, r in by.items() if r[hyb]["keyword_empty"]]
                ceiling = [q for q, r in by.items() if r[hyb]["at_ceiling"]]
                excess = [q for q in ceiling if q not in empty]
                missed = [q for q in empty if q not in ceiling]
                shared = [q for q in excess if by[q][hyb]["multi_leg_docs"] > 0]
                long_leg = [q for q in excess if by[q][hyb]["n_keyword"] >= 4]
                tot["runs"] += n
                tot["missed"] += len(missed)
                tot["excess"] += len(excess)
                tot["excess_shared"] += len(shared)
                tot["excess_4plus"] += len(long_leg)
                print(f"{enc} {coll} {hyb}: n={n} empty={len(empty)} ceiling={len(ceiling)} excess={len(excess)} "
                      f"missed={len(missed)} excess_with_shared_docs={len(shared)} excess_leg4plus={len(long_leg)} "
                      f"excess n_keyword={sorted(by[q][hyb]['n_keyword'] for q in excess)}")
                for q in shared:
                    print(f"    shared-at-ceiling {q}: n_keyword={by[q][hyb]['n_keyword']} "
                          f"multi_leg_docs={by[q][hyb]['multi_leg_docs']} max={by[q][hyb]['max_score']:.6f}")
    print("totals:", dict(tot))


def pair_counts():
    """How often each comparison goes which way over the 18 collection-encoder pairs."""
    cmp = defaultdict(lambda: [0, 0, 0])  # better, tie(|d|<0.0005), worse
    for coll in COLL:
        for enc in ENC:
            c = summary(coll, enc)["conditions"]
            for name, a, b, m in (("hor>dense ndcg", "hybrid_or", "dense", "ndcg_cut_10"),
                                  ("hor>dense r100", "hybrid_or", "dense", "recall_100"),
                                  ("hand>hor ndcg", "hybrid_and", "hybrid_or", "ndcg_cut_10"),
                                  ("hor>hand r100", "hybrid_or", "hybrid_and", "recall_100")):
                d = c[a][m] - c[b][m]
                cmp[name][0 if d >= 0.0005 else (2 if d <= -0.0005 else 1)] += 1
    for k, (b, t, w) in cmp.items():
        print(f"{k}: yes {b}, tie {t}, no {w}")


if __name__ == "__main__":
    print("% Table 2 (legs)")
    legs_table()
    print("% Table 3 (nDCG@10)")
    effect_table("ndcg_cut_10")
    print("% Table 4 (Recall@100)")
    effect_table("recall_100")
    for enc in ENC:
        print(f"% Appendix ({enc})")
        full_table(enc)
    print("% per-query facts")
    perquery_facts()
    print("% pair counts")
    pair_counts()
