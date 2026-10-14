#!/opt/homebrew/bin/python3
"""Deterministic audit of the paper's machine-checkable claims. Log-only.

Checks, each PASS or FAIL with the evidence:
  1. Every cell of the BEIR tables in paper/main.tex (legs, nDCG@10,
     Recall@100, the three appendix tables) equals the value in results/*.json
     or results/keyword_facts.json at the precision the cell shows.
  2. Table 1's cells equal results/production-aggregates.json.
  3. The ceiling inequality 2/(k+K-1) > 1/k holds iff K <= k, over a grid.
  4. hybrid.ceiling_report flags an empty leg, clears a live list, and does not
     fire on an all-empty union.
  5. The prose figures of Section 6 and the abstract follow from the result
     files, the per-query rows and results/keyword_facts.json (empty counts,
     content-token ordering, the ArguAna self-match, excess ceiling queries and
     their overlap, no missed empty leg, natural row counts, nDCG and recall
     comparisons, stopword-drop latency ratios).
Writes review/orrery-audit.md and exits 1 on any FAIL.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dead_retriever import RRF_K, ceiling_report, rrf_fuse  # noqa: E402

TEX = (ROOT / "paper" / "main.tex").read_text()
RES = {p.name: json.loads(p.read_text()) for p in (ROOT / "results").glob("beir_*.json")}
AGG = json.loads((ROOT / "results" / "production-aggregates.json").read_text())
KF = {f["dataset"]: f for f in json.loads((ROOT / "results" / "keyword_facts.json").read_text())}
ENC = {"bge": "BAAI_bge-base-en-v1.5", "nomic": "nomic-ai_nomic-embed-text-v1.5", "e5": "intfloat_e5-base-v2"}
COLL = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test", "ArguAna": "beir_arguana",
        "SciDocs": "beir_scidocs", "FiQA": "beir_fiqa_test", "TREC-COVID": "beir_trec-covid"}
DATASET = {"SciFact": "beir/scifact/test", "NFCorpus": "beir/nfcorpus/test", "ArguAna": "beir/arguana",
           "SciDocs": "beir/scidocs", "FiQA": "beir/fiqa/test", "TREC-COVID": "beir/trec-covid"}
SWEEP_COLL = ("SciFact", "NFCorpus")
OUT = []


def check(name, ok, evidence):
    OUT.append((name, bool(ok), evidence))


def cond(enc, coll, c):
    return RES[f"{COLL[coll]}__{ENC[enc]}.json"]["conditions"][c]


def perquery(enc, coll):
    by = defaultdict(dict)
    for line in (ROOT / "results" / f"{COLL[coll]}__{ENC[enc]}.perquery.jsonl").read_text().splitlines():
        row = json.loads(line)
        by[row["qid"]][row["condition"]] = row
    return by


def table_rows(label):
    i = TEX.index(label)
    start = TEX.rfind("\\begin{tabular}", 0, i)
    end = TEX.index("\\end{tabular}", start)
    rows = []
    for line in TEX[start:end].split("\n"):
        line = line.strip()
        if "&" in line and not line.startswith(("\\toprule", "\\midrule", "\\bottomrule")):
            rows.append([c.strip().rstrip("\\").strip() for c in line.split("&")])
    return rows


def shown(cell, value):
    """Does `value`, rounded to the precision `cell` shows, print as `cell`?"""
    s = cell.replace("\\%", "")
    dec = len(s.split(".")[1]) if "." in s else 0
    return round(value, dec) == float(s)


def check_full_table(label, enc):
    for cells in table_rows(label):
        if cells[0] not in COLL:
            continue
        coll, c = cells[0], cells[1].replace("-", "_")
        r = cond(enc, coll, c)
        check(f"{label} {coll} {c} nDCG@10", shown(cells[2], r["ndcg_cut_10"]), f"json {r['ndcg_cut_10']:.4f} vs tex {cells[2]}")
        check(f"{label} {coll} {c} R@100", shown(cells[3], r["recall_100"]), f"json {r['recall_100']:.4f} vs tex {cells[3]}")
        if cells[4] != "--":
            key = "empty_rate" if "empty_rate" in r else "keyword_empty_rate"
            check(f"{label} {coll} {c} kw empty", shown(cells[4], 100 * r[key]), f"json {100*r[key]:.2f}% vs tex {cells[4]}")
        if cells[5] != "--":
            check(f"{label} {coll} {c} at ceiling", shown(cells[5], 100 * r["at_ceiling_rate"]), f"json {100*r['at_ceiling_rate']:.2f}% vs tex {cells[5]}")
        if cells[6] != "--":
            check(f"{label} {coll} {c} both-leg", shown(cells[6], r["multi_leg_docs_mean"]), f"json {r['multi_leg_docs_mean']:.3f} vs tex {cells[6]}")


def shown_range(cell, values):
    """A cell like '87.2--88.4\\%' or '0.0\\%' against a set of percentages."""
    s = cell.replace("\\%", "")
    lo, hi = (s.split("--") + [s])[:2] if "--" in s else (s, s)
    return shown(lo, min(values)) and shown(hi, max(values))


def check_legs_table():
    rows = table_rows("\\label{tab:legs}")
    seen = set()
    for cells in rows:
        if cells[0] not in COLL:
            continue
        coll = cells[0]
        seen.add(coll)
        s = RES[f"{COLL[coll]}__{ENC['bge']}.json"]
        f = KF[DATASET[coll]]
        check(f"legs {coll} docs", cells[1].replace("\\,", "") == str(s["n_docs"]), f"json {s['n_docs']} vs tex {cells[1]}")
        check(f"legs {coll} queries", cells[2].replace("\\,", "") == str(s["n_queries"]) == str(f["n_queries"]), f"json {s['n_queries']} vs tex {cells[2]}")
        check(f"legs {coll} tokens", shown(cells[3], f["tokens_mean"]), f"facts {f['tokens_mean']:.2f} vs tex {cells[3]}")
        for i, hyb in ((4, "hybrid_and"), (6, "hybrid_or")):
            empties = {cond(e, coll, hyb)["keyword_empty_rate"] for e in ENC}
            check(f"legs {coll} {hyb} kw empty (encoder-independent)", len(empties) == 1 and shown(cells[i].replace("\\%", ""), 100 * next(iter(empties))), f"{empties} vs tex {cells[i]}")
            ceil = [100 * cond(e, coll, hyb)["at_ceiling_rate"] for e in ENC]
            check(f"legs {coll} {hyb} at ceiling range", shown_range(cells[i + 1], ceil), f"{[round(c, 2) for c in ceil]} vs tex {cells[i + 1]}")
    check("legs table has all six collections", seen == set(COLL), f"{sorted(seen)}")


def check_effect_table(label, metric):
    seen = set()
    for cells in table_rows(label):
        if cells[0] not in COLL:
            continue
        coll = cells[0]
        seen.add(coll)
        vals = [cond(e, coll, c)[metric] for e in ENC for c in ("dense", "hybrid_and", "hybrid_or")]
        ok = len(cells) == 10 and all(shown(t, v) for t, v in zip(cells[1:], vals))
        check(f"{label} {coll}", ok, f"json {[round(v, 4) for v in vals]} vs tex {cells[1:]}")
    check(f"{label} has all six collections", seen == set(COLL), f"{sorted(seen)}")


def check_table1():
    k = AGG["keyword_leg_2026-08-18"]
    rows = {r[0]: r for r in table_rows("\\label{tab:prod}")}
    exp = {
        "Queries on which the keyword leg returned any row": (f"{k['queries_keyword_returned_rows_before']} / {k['queries']}", f"{k['queries_keyword_returned_rows_after']} / {k['queries']}"),
        "Queries with a document found by both legs": (f"{k['queries_with_document_in_both_legs_before']} / {k['queries']}", f"{k['queries_with_document_in_both_legs_after']} / {k['queries']}"),
    }
    for name, (b, a) in exp.items():
        r = rows.get(name)
        check(f"Table 1: {name}", r is not None and r[1] == b and r[2] == a, f"tex {r[1:] if r else None} vs aggregates {(b, a)}")
    r = rows.get("Maximum fused score over the top 100 results")
    check("Table 1: max fused score before", r is not None and "0.0167" in r[1] and abs(k["max_fused_score_top100_before"] - 1 / 60) < 1e-6, f"{r[1] if r else None}")
    lo, hi = k["max_fused_score_top100_after_range"]
    check("Table 1: max fused score after range", r is not None and f"{lo}" in r[2] and f"{hi}" in r[2], f"{r[2] if r else None}")
    r = rows.get("Keyword leg latency, conversational queries")
    lo, hi = k["keyword_latency_ms_after_range"]
    check("Table 1: latency after", r is not None and f"{lo} -- {hi}" in r[2], f"{r[2] if r else None}")
    check("prose: raw OR latency 161 ms", "161\\,ms" in TEX and k["keyword_latency_ms_raw_or_no_stopword_drop"] == 161, "")


def check_inequality():
    bad = [(k, K) for k in range(1, 201) for K in range(1, 301) if (2.0 / (k + K - 1) > 1.0 / k) != (K <= k)]
    check("ceiling inequality 2/(k+K-1) > 1/k iff K <= k over [1,200]x[1,300]", not bad, f"{len(bad)} exceptions")
    k = RRF_K
    check("K>k: rank k in both legs scores exactly 1/k", abs(2.0 / (2 * k) - 1.0 / k) < 1e-12, f"{2.0/(2*k):.6f}")
    check("K>k: rank 90 in both legs scores below 1/k", 2.0 / (k + 90) < 1.0 / k, f"{2.0/(k+90):.6f}")
    rel0, rel10 = 1.0 / (k + 1), 1.0 / (k + 11)
    check("prose: relative step 1.6% at the top and 1.4% around rank 10", round(100 * rel0, 1) == 1.6 and round(100 * rel10, 1) == 1.4, f"{100*rel0:.2f}% {100*rel10:.2f}%")


def check_diagnostic():
    s, r = rrf_fuse({"dense": ["a", "b", "c"], "keyword": []})
    rep = ceiling_report(s, r)
    check("ceiling_report flags an empty leg", rep.at_ceiling and rep.empty_legs == ["keyword"] and abs(rep.max_score - 1 / RRF_K) < 1e-12, f"max {rep.max_score:.6f}")
    s, r = rrf_fuse({"dense": ["a", "b"], "keyword": ["b", "z"]})
    rep = ceiling_report(s, r)
    check("ceiling_report clears a live two-leg list", not rep.at_ceiling and rep.multi_leg_docs == 1, f"multi {rep.multi_leg_docs}")
    s, r = rrf_fuse({"a": [], "b": []})
    rep = ceiling_report(s, r)
    check("ceiling_report does not fire on an all-empty union", not rep.at_ceiling and rep.max_score == 0.0, f"max {rep.max_score}")


def said(*fragments):
    """Every fragment appears in the paper (whitespace-normalised), so a check
    is tied to text that is actually there."""
    flat = " ".join(TEX.split())
    return all(" ".join(f.split()) in flat for f in fragments)


def r3(x):
    return round(x + 0.0, 3)


def check_prose_beir():
    pq = {(e, c): perquery(e, c) for e in ENC for c in COLL}
    # The leg: AND empty counts, OR empties, content tokens and their ordering.
    exp_and = {"SciFact": (294, 300), "SciDocs": (942, 1000), "FiQA": (530, 648), "TREC-COVID": (37, 50), "NFCorpus": (164, 323)}
    for coll, (e, n) in exp_and.items():
        by = pq[("bge", coll)]
        got = sum(1 for r in by.values() if r["hybrid_and"]["keyword_empty"])
        check(f"prose: AND empty {e} of {n} on {coll}", got == e and len(by) == n and KF[DATASET[coll]]["and_empty"] == e, f"{got}/{len(by)}")
    check("prose: the five empty counts are named", said("294 of SciFact's 300", "942 of SciDocs's 1\\,000", "530 of FiQA's 648", "37 of TREC-COVID's 50", "164 of NFCorpus's 323"), "")
    or_empty = {c: sum(1 for r in pq[("bge", c)].values() if r["hybrid_or"]["keyword_empty"]) for c in COLL}
    check("prose: after the fix only NFCorpus has empty legs, 25 (7.7%)", or_empty["NFCorpus"] == 25 and all(v == 0 for c, v in or_empty.items() if c != "NFCorpus") and said("25 title queries (7.7\\%)"), f"{or_empty}")
    five = ["SciFact", "SciDocs", "FiQA", "TREC-COVID", "NFCorpus"]
    kept = [round(KF[DATASET[c]]["kept_tokens_mean"], 1) for c in five]
    rate = [round(100 * cond("bge", c, "hybrid_and")["keyword_empty_rate"], 1) for c in five]
    check("prose: content tokens 8.7, 7.3, 6.2, 5.7, 2.5 against empty 98.0, 94.2, 81.8, 74.0, 50.8, both descending",
          kept == [8.7, 7.3, 6.2, 5.7, 2.5] and rate == [98.0, 94.2, 81.8, 74.0, 50.8] and kept == sorted(kept, reverse=True) and rate == sorted(rate, reverse=True)
          and said("8.7 content tokens per query on SciFact, 7.3 on SciDocs, 6.2 on FiQA, 5.7 on TREC-COVID and 2.5 on NFCorpus", "98.0, 94.2, 81.8, 74.0 and 50.8\\%"), f"{kept} {rate}")
    toks = {c: KF[DATASET[c]]["tokens_mean"] for c in COLL}
    check("prose: NFCorpus shortest queries; TREC-COVID about as long as FiQA and SciDocs; ArguAna 195",
          min(toks, key=toks.get) == "NFCorpus" and abs(toks["TREC-COVID"] - toks["FiQA"]) < 1 and abs(toks["TREC-COVID"] - toks["SciDocs"]) < 1.5 and round(toks["ArguAna"]) == 195, f"{toks}")
    # Stopword drop.
    b = {c: cond("bge", c, "bm25_or") for c in COLL}
    raw = {c: cond("bge", c, "bm25_or_raw") for c in COLL}
    ratio = {c: raw[c]["mean_query_ms"] / b[c]["mean_query_ms"] for c in COLL}
    check("prose: raw OR 2.6 to 18 times slower", round(min(ratio.values()), 1) == 2.6 and round(max(ratio.values())) == 18 and said("2.6 to 18 times slower"), f"{ {c: round(v, 2) for c, v in ratio.items()} }")
    check("prose: 10.2 vs 3.0 ms SciFact, 2.1 vs 0.8 NFCorpus, 782 vs 44 ArguAna",
          (round(raw["SciFact"]["mean_query_ms"], 1), round(b["SciFact"]["mean_query_ms"], 1)) == (10.2, 3.0)
          and (round(raw["NFCorpus"]["mean_query_ms"], 1), round(b["NFCorpus"]["mean_query_ms"], 1)) == (2.1, 0.8)
          and (round(raw["ArguAna"]["mean_query_ms"]), round(b["ArguAna"]["mean_query_ms"])) == (782, 44), "")
    d_nd = {c: raw[c]["ndcg_cut_10"] - b[c]["ndcg_cut_10"] for c in COLL}
    check("prose: raw OR within 0.008 nDCG@10 of OR on five collections",
          all(abs(v) <= 0.0085 for c, v in d_nd.items() if c != "FiQA") and abs(d_nd["FiQA"]) > 0.0085, f"{ {c: round(v, 4) for c, v in d_nd.items()} }")
    check("prose: FiQA raw OR better by 0.009 nDCG@10 and 0.012 R@100 at 5.8x",
          r3(d_nd["FiQA"]) == 0.009 and r3(raw["FiQA"]["recall_100"] - b["FiQA"]["recall_100"]) == 0.012 and round(ratio["FiQA"], 1) == 5.8 and said("better by 0.009 nDCG@10 and 0.012 Recall@100, at 5.8 times the cost"), "")
    # ArguAna.
    fa = KF["beir/arguana"]
    and_n = [r["hybrid_and"]["n_keyword"] for r in pq[("bge", "ArguAna")].values()]
    check("prose: ArguAna AND leg one document on 1,402, two on 4, never empty",
          sum(1 for n in and_n if n == 1) == 1402 and sum(1 for n in and_n if n == 2) == 4 and len(and_n) == 1406 and said("one document for 1\\,402 of the 1\\,406 queries and two for the other four"), "")
    check("prose: ArguAna query text returned on all 1,406; own id on 1,298 (rank 1 on 1,296); 108 under another id; 1 relevant",
          fa["and_returns_query_text"] == 1406 and fa["and_returns_query_itself"] == 1298 and fa["and_query_itself_at_rank_1"] == 1296
          and 1406 - 1298 == 108 and fa["and_any_relevant_hit"] == 1, f"{fa}")
    check("prose: one document on 99.7% of queries", round(100 * 1402 / 1406, 1) == 99.7 and said("one document on 99.7\\% of queries"), "")
    shares = all(min(r["hybrid_and"]["multi_leg_docs"] for r in pq[(e, "ArguAna")].values()) >= 1 for e in ENC)
    never = all(cond(e, "ArguAna", "hybrid_and")["at_ceiling_rate"] == 0.0 for e in ENC)
    same = all(r3(cond(e, "ArguAna", "hybrid_and")[m] - cond(e, "ArguAna", "dense")[m]) == 0.0 for e in ENC for m in ("ndcg_cut_10", "recall_100"))
    check("prose: ArguAna dense shares the document on every query, ceiling never fires, hybrid-and = dense to 3 decimals", shares and never and same, "")
    # What fusion did with an empty list.
    for e in ENC:
        sf = pq[(e, "SciFact")]
        n = sum(1 for r in sf.values() if r["hybrid_and"]["keyword_empty"] and r["hybrid_and"]["n_dense"] == r["dense"]["n_dense"] and abs(r["hybrid_and"]["max_score"] - 1 / 60) < 1e-12)
        check(f"prose: SciFact {e}: the 294 empty-leg queries have dense's count and max exactly 1/60", n == 294, f"{n}")
    def diffs(coll, m):
        return [cond(e, coll, "hybrid_and")[m] - cond(e, coll, "dense")[m] for e in ENC]
    check("prose: SciFact hybrid-and vs dense at most 0.002 nDCG@10 and 0.000 R@100",
          max(abs(r3(x)) for x in diffs("SciFact", "ndcg_cut_10")) == 0.002 and max(abs(r3(x)) for x in diffs("SciFact", "recall_100")) == 0.0, "")
    check("prose: SciDocs hybrid-and vs dense at most 0.002 and 0.000",
          max(abs(r3(x)) for x in diffs("SciDocs", "ndcg_cut_10")) == 0.002 and max(abs(r3(x)) for x in diffs("SciDocs", "recall_100")) == 0.0, "")
    nf = sorted(r3(x) for x in diffs("NFCorpus", "ndcg_cut_10"))
    tc = sorted(r3(x) for x in diffs("TREC-COVID", "ndcg_cut_10"))
    check("prose: NFCorpus hybrid-and above dense by 0.008 to 0.013; TREC-COVID below by 0.027 to 0.039",
          (nf[0], nf[-1]) == (0.008, 0.013) and (tc[0], tc[-1]) == (-0.039, -0.027) and said("by 0.008 to 0.013 nDCG@10", "below by 0.027 to 0.039"), f"{nf} {tc}")
    live = {c: sum(1 for r in pq[("bge", c)].values() if not r["hybrid_and"]["keyword_empty"]) for c in COLL}
    check("prose: live AND legs NFCorpus 159, SciDocs 58, FiQA 118, TREC-COVID 13", (live["NFCorpus"], live["SciDocs"], live["FiQA"], live["TREC-COVID"]) == (159, 58, 118, 13), f"{live}")
    # The ceiling against the row count.
    runs = missed = 0
    excess = defaultdict(int)
    shared, long_ = [], []
    for (e, c), by in pq.items():
        for hyb in ("hybrid_and", "hybrid_or"):
            for q, r in by.items():
                row = r[hyb]
                runs += 1
                if row["keyword_empty"] and not row["at_ceiling"]:
                    missed += 1
                if row["at_ceiling"] and not row["keyword_empty"]:
                    excess[(e, c, hyb)] += 1
                    if row["multi_leg_docs"] > 0:
                        shared.append((e, c, hyb, row["n_keyword"], row["multi_leg_docs"]))
                    if row["n_keyword"] >= 4:
                        long_.append(c)
    tot_and = sum(v for k, v in excess.items() if k[2] == "hybrid_and")
    tot_or = sum(v for k, v in excess.items() if k[2] == "hybrid_or")
    check("prose: 22,362 hybrid query runs, no empty leg missed", runs == 22362 and missed == 0 and said("22\\,362 hybrid query runs"), f"{runs} runs, {missed} missed")
    check("prose: 176 excess, 164 buggy and 12 fixed; none on SciFact or ArguAna",
          tot_and + tot_or == 176 and tot_and == 164 and tot_or == 12 and not any(k[1] in ("SciFact", "ArguAna") for k in excess) and said("176 query runs, 164 under the buggy builder and 12 under the fixed one"), f"{tot_and} {tot_or}")
    def rng(coll):
        v = [excess.get((e, coll, "hybrid_and"), 0) for e in ENC]
        return min(v), max(v)
    exp = {"NFCorpus": ((2, 3), (1.3, 1.9)), "SciDocs": ((5, 7), (8.6, 12.1)), "FiQA": ((35, 43), (29.7, 36.4)), "TREC-COVID": ((7, 8), (53.8, 61.5))}
    for coll, (cnt, pcts) in exp.items():
        lo, hi = rng(coll)
        check(f"prose: {coll} buggy excess {cnt[0]} to {cnt[1]} of {live[coll]} ({pcts[0]} to {pcts[1]}%)",
              (lo, hi) == cnt and (round(100 * lo / live[coll], 1), round(100 * hi / live[coll], 1)) == pcts, f"{lo}-{hi}/{live[coll]}")
    check("prose: 174 of 176 shared nothing; two FiQA fixed-builder runs (bge, e5) with 100 keyword docs and one shared",
          len(shared) == 2 and sorted(s[0] for s in shared) == ["bge", "e5"] and all(s[1] == "FiQA" and s[2] == "hybrid_or" and s[3] == 100 and s[4] == 1 for s in shared)
          and said("In 174 of the 176"), f"{shared}")
    check("prose: ceiling over a leg of four or more on 39 runs, all FiQA, TREC-COVID, SciDocs",
          len(long_) == 39 and set(long_) <= {"FiQA", "TREC-COVID", "SciDocs"} and said("on 39 runs, all on FiQA, TREC-COVID and SciDocs"), f"{len(long_)} {sorted(set(long_))}")
    nat = json.loads((ROOT / "results" / "natural_lengths.json").read_text())
    nb = {b["n_keyword"]: (b["fired"], b["total"]) for b in nat["buckets"]}
    check("prose: pooled without ArguAna 137/726 (18.9%), 35/588 (6.0%), 4/6,636 (0.1%)",
          nat["pooled_without"] == "beir_arguana" and nb["1-3"] == (137, 726) and nb["4-49"] == (35, 588) and nb["50-100"] == (4, 6636)
          and round(100 * 137 / 726, 1) == 18.9 and round(100 * 35 / 588, 1) == 6.0 and round(100 * 4 / 6636, 1) == 0.1, f"{nb}")
    bc = nat["by_collection"]
    short = {c: (bc[COLL[c]]["1-3"]["fired"], bc[COLL[c]]["1-3"]["total"]) for c in ("NFCorpus", "SciDocs", "FiQA", "TREC-COVID")}
    check("prose: short-list rate 13/330, 18/141, 90/219, 16/18", short == {"NFCorpus": (13, 330), "SciDocs": (18, 141), "FiQA": (90, 219), "TREC-COVID": (16, 18)}
          and said("13 of 330 on NFCorpus (3.6k documents), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k)"), f"{short}")
    sizes = {c: RES[f"{COLL[c]}__{ENC['bge']}.json"]["n_docs"] for c in COLL}
    check("prose: corpus sizes 3.6k, 26k, 58k, 171k", (round(sizes["NFCorpus"] / 1000, 1), round(sizes["SciDocs"] / 1000), round(sizes["FiQA"] / 1000), round(sizes["TREC-COVID"] / 1000)) == (3.6, 26, 58, 171), f"{sizes}")
    check("prose: sweep zero contrasted with the two natural FiQA runs at n = 100", len(shared) == 2 and said("It did occur twice in the natural FiQA runs above, both with $n = 100$"), "")
    # Effectiveness.
    sh_and = max(cond(e, c, "hybrid_and")["multi_leg_docs_mean"] for e in ENC for c in COLL)
    sh_or = [cond(e, c, "hybrid_or")["multi_leg_docs_mean"] for e in ENC for c in COLL]
    check("prose: shared documents at most 4.0 per query before, 19.0 to 43.7 after",
          round(sh_and, 1) == 4.0 and round(min(sh_or), 1) == 19.0 and round(max(sh_or), 1) == 43.7, f"{sh_and:.2f} {min(sh_or):.2f} {max(sh_or):.2f}")
    def count(a, bb, m):
        return sum(1 for e in ENC for c in COLL if cond(e, c, a)[m] - cond(e, c, bb)[m] >= 0.0005)
    n1, n2, n3 = count("hybrid_or", "dense", "ndcg_cut_10"), count("hybrid_or", "dense", "recall_100"), count("hybrid_and", "hybrid_or", "ndcg_cut_10")
    check("prose: repaired above dense nDCG 5/18, R@100 9/18; buggy above repaired nDCG 12/18",
          (n1, n2, n3) == (5, 9, 12) and said("above \\textsc{dense} at nDCG@10 in 5 and above it at Recall@100 in 9", "at nDCG@10 in 12"), f"{n1} {n2} {n3}")
    ties = sum(1 for e in ENC for c in COLL for a, bb, m in (("hybrid_or", "dense", "ndcg_cut_10"), ("hybrid_or", "dense", "recall_100"), ("hybrid_and", "hybrid_or", "ndcg_cut_10"))
               if abs(cond(e, c, a)[m] - cond(e, c, bb)[m]) < 0.0005)
    check("effectiveness counts have no near-ties (|d| < 0.0005)", ties == 0, f"{ties}")
    bm_arg = cond("bge", "ArguAna", "bm25_or")["ndcg_cut_10"]
    beaten = [e for e in ENC if cond(e, "ArguAna", "dense")["ndcg_cut_10"] < bm_arg]
    only = all(cond(e, c, "dense")["ndcg_cut_10"] >= cond("bge", c, "bm25_or")["ndcg_cut_10"] for e in ENC for c in COLL if c != "ArguAna")
    check("prose: ArguAna the one collection where BM25 (0.360) beats two encoders", r3(bm_arg) == 0.360 and sorted(beaten) == ["e5", "nomic"] and only, f"{beaten}")
    g = lambda e, c: r3(cond(e, c, "hybrid_or")["ndcg_cut_10"] - cond(e, c, "dense")["ndcg_cut_10"])
    check("prose: gains e5 +0.059 and nomic +0.027 (ArguAna), +0.004 nomic and +0.007 e5 (SciFact), e5 +0.018 (TREC-COVID)",
          (g("e5", "ArguAna"), g("nomic", "ArguAna"), g("nomic", "SciFact"), g("e5", "SciFact"), g("e5", "TREC-COVID")) == (0.059, 0.027, 0.004, 0.007, 0.018), "")
    fq_bm = cond("bge", "FiQA", "bm25_or")["ndcg_cut_10"]
    fq_d = sorted(cond(e, "FiQA", "dense")["ndcg_cut_10"] for e in ENC)
    fq_l = sorted(-g(e, "FiQA") for e in ENC)
    check("prose: FiQA BM25 0.224 against 0.376 to 0.406; repaired hybrid 0.037 to 0.059 below dense",
          r3(fq_bm) == 0.224 and (r3(fq_d[0]), r3(fq_d[-1])) == (0.376, 0.406) and (fq_l[0], fq_l[-1]) == (0.037, 0.059), f"{fq_d} {fq_l}")
    # Abstract.
    check("abstract: 50.8 to 98.0% on five collections, 174 and two, 5 of 18",
          said("50.8 to 98.0\\% of queries on five collections", "in 174 runs", "in two, the case depth", "in 5 of 18 collection--encoder pairs"), "")


def check_sweep():
    sweeps = {p.name: json.loads(p.read_text()) for p in (ROOT / "results").glob("*.sweep.json")}
    check("sweep: four files", len(sweeps) == 4, f"{len(sweeps)}")
    cells = runs = 0
    eq = leak0 = True
    for s in sweeps.values():
        for c in s["cells"]:
            cells += 1
            runs += c["live_queries"]
            eq &= abs(c["fired_rate"] - c["disjoint_rate"]) < 1e-12
            leak0 &= c["fired_with_overlap_rate"] == 0.0
    check("sweep: 60 cells and 17,940 live-leg runs", cells == 60 and runs == 17940, f"{cells} cells, {runs} runs")
    check("sweep: fired rate equals disjoint rate in every cell", eq, "")
    check("sweep: ceiling never fired with overlap present", leak0, "")
    bge = {coll: sweeps[f"{COLL[coll]}__{ENC['bge']}.sweep.json"] for coll in SWEEP_COLL}
    rows = {r[0]: r for r in table_rows("\\label{tab:sweep}") if r[0].strip().isdigit()}
    for coll_i, coll in enumerate(SWEEP_COLL):
        for c in bge[coll]["cells"]:
            cell = rows[str(c["n"])][1 + 2 * coll_i + (0 if c["K"] == 60 else 1)]
            check(f"sweep table {coll} n={c['n']} K={c['K']}", shown(cell, 100 * c["fired_rate"]), f"json {100*c['fired_rate']:.2f}% vs tex {cell}")
    # Prose ranges at n = 1, 3, 10 and >= 20, over both encoders, K = 60 for the first three.
    def rates(n, K):
        return [c["fired_rate"] for s in sweeps.values() for c in s["cells"] if c["n"] == n and c["K"] == K]
    def rng(n, K):
        r = rates(n, K)
        return round(100 * min(r), 1), round(100 * max(r), 1)
    check("prose: cap 1 at K=60 is 8.7 to 15.1%", rng(1, 60) == (8.7, 15.1), f"{rng(1,60)}")
    check("prose: cap 3 at K=60 is 2.7 to 6.7%", rng(3, 60) == (2.7, 6.7), f"{rng(3,60)}")
    check("prose: cap 10 at K=60 is 0.7 to 2.3%", rng(10, 60) == (0.7, 2.3), f"{rng(10,60)}")
    big = [c["fired_rate"] for s in sweeps.values() for c in s["cells"] if c["n"] >= 20]
    check("prose: cap>=20 at most 1.7%, under 1% in 11 of 20 cells", len(big) == 20 and max(big) <= 0.0175 and sum(1 for r in big if r < 0.01) == 11, f"max {100*max(big):.1f}%, under 1%: {sum(1 for r in big if r < 0.01)}/{len(big)}")
    deeper = all(c100["fired_rate"] <= c60["fired_rate"] for s in sweeps.values()
                 for c60 in s["cells"] if c60["K"] == 60 for c100 in s["cells"] if c100["K"] == 100 and c100["n"] == c60["n"])
    check("prose: a deeper dense list never raises a figure", deeper, "")
    # Hidden overlap is possible only when (n-1)(K-1) >= k^2; count those cells and runs, and that the leak is zero there.
    k = RRF_K
    leak_cells = [c for s in sweeps.values() for c in s["cells"] if (c["n"] - 1) * (c["K"] - 1) >= k * k]
    check("prose: hidden overlap possible in 8 cells (K=100, n in {50,100}), 2,392 runs, none observed",
          len(leak_cells) == 8 and all(c["K"] == 100 and c["n"] in (50, 100) for c in leak_cells)
          and sum(c["live_queries"] for c in leak_cells) == 2392 and all(c["fired_with_overlap_rate"] == 0.0 for c in leak_cells),
          f"{len(leak_cells)} cells, {sum(c['live_queries'] for c in leak_cells)} runs")
    nom = {coll: sweeps[f"{COLL[coll]}__{ENC['nomic']}.sweep.json"] for coll in SWEEP_COLL}
    d1 = max(abs(a["fired_rate"] - b["fired_rate"]) for coll in SWEEP_COLL for a in bge[coll]["cells"] for b in nom[coll]["cells"] if a["n"] == b["n"] == 1 and a["K"] == b["K"])
    d3 = max(abs(a["fired_rate"] - b["fired_rate"]) for coll in SWEEP_COLL for a in bge[coll]["cells"] for b in nom[coll]["cells"] if a["n"] == b["n"] >= 3 and a["K"] == b["K"])
    check("caption: nomic within 4.4 points at n=1 and 1.0 point from n=3", d1 <= 0.044 and d3 <= 0.010, f"{100*d1:.1f} {100*d3:.1f}")


def main():
    check_sweep()
    check_legs_table()
    check_effect_table("\\label{tab:ndcg}", "ndcg_cut_10")
    check_effect_table("\\label{tab:recall}", "recall_100")
    for enc in ENC:
        check_full_table(f"\\label{{tab:full-{enc}}}", enc)
    check_table1()
    check_inequality()
    check_diagnostic()
    check_prose_beir()
    fails = [o for o in OUT if not o[1]]
    lines = ["# Orrery audit of paper/main.tex against results/ and dead_retriever/ (log-only)", "",
             f"{len(OUT) - len(fails)} PASS, {len(fails)} FAIL", ""]
    lines += [f"- {'PASS' if ok else 'FAIL'}  {name}  ({ev})" for name, ok, ev in OUT]
    (ROOT / "review" / "orrery-audit.md").write_text("\n".join(lines) + "\n")
    print(lines[2])
    print("\n".join(l for l in lines[4:] if l.startswith("- FAIL")))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
