#!/opt/homebrew/bin/python3
"""Deterministic audit of the paper's machine-checkable claims. Log-only.

Checks, each PASS or FAIL with the evidence:
  1. Every cell of Tables 2 and 3 in paper/main.tex equals the value in
     results/*.json at the precision the cell shows.
  2. Table 1's cells equal results/production-aggregates.json.
  3. The ceiling inequality 2/(k+K-1) > 1/k holds iff K <= k, over a grid.
  4. hybrid.ceiling_report flags an empty leg, clears a live list, and does not
     fire on an all-empty union.
  5. The prose figures of Section 6 follow from the result files and the
     per-query rows (empty counts, excess ceiling queries and their overlap,
     hybrid-and equals dense on empty-leg queries, no missed empty leg,
     nDCG and recall comparisons, stopword-drop latency ratio).
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
ENC = {"bge": "BAAI_bge-base-en-v1.5", "nomic": "nomic-ai_nomic-embed-text-v1.5"}
COLL = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test"}
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


def check_beir_table(label, enc):
    for cells in table_rows(label):
        if cells[0] not in COLL:
            continue
        coll, c = cells[0], cells[1].replace("-", "_")
        r = cond(enc, coll, c)
        check(f"{label} {coll} {c} nDCG@10", shown(cells[2], r["ndcg_cut_10"]), f"json {r['ndcg_cut_10']:.4f} vs tex {cells[2]}")
        check(f"{label} {coll} {c} R@100", shown(cells[3], r["recall_100"]), f"json {r['recall_100']:.4f} vs tex {cells[3]}")
        check(f"{label} {coll} {c} ms", shown(cells[4], r["mean_query_ms"]), f"json {r['mean_query_ms']:.2f} vs tex {cells[4]}")
        if cells[5] != "--":
            key = "empty_rate" if "empty_rate" in r else "keyword_empty_rate"
            check(f"{label} {coll} {c} kw empty", shown(cells[5], 100 * r[key]), f"json {100*r[key]:.2f}% vs tex {cells[5]}")
        if cells[6] != "--":
            check(f"{label} {coll} {c} at ceiling", shown(cells[6], 100 * r["at_ceiling_rate"]), f"json {100*r['at_ceiling_rate']:.2f}% vs tex {cells[6]}")
        if cells[7] != "--":
            check(f"{label} {coll} {c} both-leg", shown(cells[7], r["multi_leg_docs_mean"]), f"json {r['multi_leg_docs_mean']:.3f} vs tex {cells[7]}")


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


def check_prose_beir():
    # Empty counts named in the text.
    sf, nf = perquery("bge", "SciFact"), perquery("bge", "NFCorpus")
    e_sf = sum(1 for r in sf.values() if r["hybrid_and"]["keyword_empty"])
    e_nf = sum(1 for r in nf.values() if r["hybrid_and"]["keyword_empty"])
    check("prose: 294 of 300 SciFact queries empty under AND", e_sf == 294 and len(sf) == 300, f"{e_sf}/{len(sf)}")
    check("prose: 164 of 323 NFCorpus queries empty under AND", e_nf == 164 and len(nf) == 323, f"{e_nf}/{len(nf)}")
    e_or = sum(1 for r in nf.values() if r["hybrid_or"]["keyword_empty"])
    check("prose: 25 NFCorpus queries still empty after the fix", e_or == 25, f"{e_or}")
    # hybrid-and equals dense on empty-leg queries: same count, max exactly 1/60.
    same = sum(1 for r in sf.values() if r["hybrid_and"]["keyword_empty"] and r["hybrid_and"]["n_dense"] == r["dense"]["n_dense"] and abs(r["hybrid_and"]["max_score"] - 1 / 60) < 1e-12)
    check("prose: on the 294 empty-leg SciFact queries hybrid-and max = 1/60 with dense's count", same == 294, f"{same}")
    # No missed empty leg anywhere; excess queries all have zero overlap and keyword lists of 1 or 3.
    total_runs, missed, excess_bad = 0, 0, []
    excess_counts = {}
    for enc in ENC:
        for coll in COLL:
            by = perquery(enc, coll)
            for hyb in ("hybrid_and", "hybrid_or"):
                total_runs += len(by)
                for q, r in by.items():
                    row = r[hyb]
                    if row["keyword_empty"] and not row["at_ceiling"]:
                        missed += 1
                    if row["at_ceiling"] and not row["keyword_empty"]:
                        excess_counts[(enc, coll, hyb)] = excess_counts.get((enc, coll, hyb), 0) + 1
                        if row["multi_leg_docs"] != 0 or row["n_keyword"] not in (1, 3):
                            excess_bad.append((enc, coll, hyb, q, row["multi_leg_docs"], row["n_keyword"]))
    check("prose: 2492 hybrid query runs, no empty leg missed by the ceiling", total_runs == 2492 and missed == 0, f"runs {total_runs}, missed {missed}")
    check("prose: excess ceiling queries all have zero overlap and 1 or 3 keyword docs", not excess_bad, f"{excess_bad[:3]}")
    check("prose: excess counts AND 3/3, OR bge 3, OR nomic 2, SciFact none",
          excess_counts.get(("bge", "NFCorpus", "hybrid_and")) == 3 and excess_counts.get(("nomic", "NFCorpus", "hybrid_and")) == 3
          and excess_counts.get(("bge", "NFCorpus", "hybrid_or")) == 3 and excess_counts.get(("nomic", "NFCorpus", "hybrid_or")) == 2
          and not any(k[1] == "SciFact" for k in excess_counts), f"{excess_counts}")
    check("prose: excess rates 3/159 = 1.9%, 3/298 = 1.0%, 2/298 = 0.7%", round(300 / 159, 1) == 1.9 and round(300 / 298, 1) == 1.0 and round(200 / 298, 1) == 0.7, "")
    # Effectiveness statements.
    b_sf, b_nf = {c: cond("bge", "SciFact", c) for c in ("dense", "hybrid_and", "hybrid_or", "bm25_or", "bm25_or_raw")}, {c: cond("bge", "NFCorpus", c) for c in ("dense", "hybrid_and", "hybrid_or", "bm25_or", "bm25_or_raw")}
    n_sf, n_nf = {c: cond("nomic", "SciFact", c) for c in ("dense", "hybrid_and", "hybrid_or")}, {c: cond("nomic", "NFCorpus", c) for c in ("dense", "hybrid_and", "hybrid_or")}
    check("prose: SciFact hybrid-and vs dense differ by 0.001 nDCG and 0.000 R@100 (bge)", round(abs(b_sf["hybrid_and"]["ndcg_cut_10"] - b_sf["dense"]["ndcg_cut_10"]), 3) == 0.001 and round(abs(b_sf["hybrid_and"]["recall_100"] - b_sf["dense"]["recall_100"]), 3) == 0.0, "")
    check("prose: NFCorpus hybrid-and vs dense differ by 0.008 nDCG and 0.005 R@100 (bge)", round(abs(b_nf["hybrid_and"]["ndcg_cut_10"] - b_nf["dense"]["ndcg_cut_10"]), 3) == 0.008 and round(abs(b_nf["hybrid_and"]["recall_100"] - b_nf["dense"]["recall_100"]), 3) == 0.005, "")
    check("prose: stopword drop three times faster, not less effective", b_sf["bm25_or_raw"]["mean_query_ms"] / b_sf["bm25_or"]["mean_query_ms"] > 2.5 and b_sf["bm25_or"]["ndcg_cut_10"] >= b_sf["bm25_or_raw"]["ndcg_cut_10"] and b_nf["bm25_or"]["ndcg_cut_10"] >= b_nf["bm25_or_raw"]["ndcg_cut_10"], f"ratio {b_sf['bm25_or_raw']['mean_query_ms']/b_sf['bm25_or']['mean_query_ms']:.1f}")
    buggy_beats_fixed = sum(1 for d in (b_sf, b_nf, n_sf, n_nf) if d["hybrid_and"]["ndcg_cut_10"] > d["hybrid_or"]["ndcg_cut_10"])
    check("prose: buggy hybrid beats fixed hybrid at nDCG@10 in 3 of 4 pairs", buggy_beats_fixed == 3, f"{buggy_beats_fixed}")
    check("prose: bge fixed hybrid below dense at nDCG@10 on both collections", b_sf["hybrid_or"]["ndcg_cut_10"] < b_sf["dense"]["ndcg_cut_10"] and b_nf["hybrid_or"]["ndcg_cut_10"] < b_nf["dense"]["ndcg_cut_10"], "")
    check("prose: NFCorpus buggy hybrid beats dense (bge)", b_nf["hybrid_and"]["ndcg_cut_10"] > b_nf["dense"]["ndcg_cut_10"], "")
    check("prose: nomic R@100 0.928 -> 0.958 (SciFact), 0.298 -> 0.309 (NFCorpus)", round(n_sf["dense"]["recall_100"], 3) == 0.928 and round(n_sf["hybrid_or"]["recall_100"], 3) == 0.958 and round(n_nf["dense"]["recall_100"], 3) == 0.298 and round(n_nf["hybrid_or"]["recall_100"], 3) == 0.309, "")
    check("prose: bge R@100 changed by 0.003 and 0.001", round(b_sf["hybrid_or"]["recall_100"] - b_sf["dense"]["recall_100"], 3) == 0.003 and round(b_nf["hybrid_or"]["recall_100"] - b_nf["dense"]["recall_100"], 3) == 0.001, "")
    check("prose: shared docs 0.02 -> 28.9 on SciFact (bge)", round(b_sf["hybrid_and"]["multi_leg_docs_mean"], 2) == 0.02 and round(b_sf["hybrid_or"]["multi_leg_docs_mean"], 1) == 28.9, "")
    # The abstract's "within one percentage point".
    worst = max(abs(cond(e, c, h)["at_ceiling_rate"] - cond(e, c, h)["keyword_empty_rate"]) for e in ENC for c in COLL for h in ("hybrid_and", "hybrid_or"))
    check("abstract: ceiling rate within one percentage point of empty rate", worst < 0.01, f"worst {100*worst:.2f} pp")


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
    bge = {coll: sweeps[f"{COLL[coll]}__{ENC['bge']}.sweep.json"] for coll in COLL}
    rows = {r[0]: r for r in table_rows("\\label{tab:sweep}") if r[0].strip().isdigit()}
    for coll_i, coll in enumerate(COLL):
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
    nat = json.loads((ROOT / "results" / "natural_lengths.json").read_text())["buckets"]
    short = [b for b in nat if b["n_keyword"] in ("1", "2-3")]
    long_ = [b for b in nat if b["n_keyword"] not in ("1", "2-3")]
    fs, ts = sum(b["fired"] for b in short), sum(b["total"] for b in short)
    fl, tl = sum(b["fired"] for b in long_), sum(b["total"] for b in long_)
    check("prose: natural lengths: 11 of 232 legs with 1-3 docs fired (4.7%), 0 of 1,294 with 4+", fs == 11 and ts == 232 and round(100 * fs / ts, 1) == 4.7 and fl == 0 and tl == 1294, f"{fs}/{ts}, {fl}/{tl}")
    nom = {coll: sweeps[f"{COLL[coll]}__{ENC['nomic']}.sweep.json"] for coll in COLL}
    d1 = max(abs(a["fired_rate"] - b["fired_rate"]) for coll in COLL for a in bge[coll]["cells"] for b in nom[coll]["cells"] if a["n"] == b["n"] == 1 and a["K"] == b["K"])
    d3 = max(abs(a["fired_rate"] - b["fired_rate"]) for coll in COLL for a in bge[coll]["cells"] for b in nom[coll]["cells"] if a["n"] == b["n"] >= 3 and a["K"] == b["K"])
    check("caption: nomic within 4.4 points at n=1 and 1.0 point from n=3", d1 <= 0.044 and d3 <= 0.010, f"{100*d1:.1f} {100*d3:.1f}")


def check_prose_round2():
    b_sf, b_nf = {c: cond("bge", "SciFact", c) for c in ("dense", "hybrid_and", "hybrid_or", "bm25_or", "bm25_or_raw")}, {c: cond("bge", "NFCorpus", c) for c in ("dense", "hybrid_and", "hybrid_or", "bm25_or", "bm25_or_raw")}
    n_sf, n_nf = {c: cond("nomic", "SciFact", c) for c in ("dense", "hybrid_and", "hybrid_or")}, {c: cond("nomic", "NFCorpus", c) for c in ("dense", "hybrid_and", "hybrid_or")}
    check("prose: shared docs 4.0 -> 21.3 on NFCorpus (bge)", round(b_nf["hybrid_and"]["multi_leg_docs_mean"], 1) == 4.0 and round(b_nf["hybrid_or"]["multi_leg_docs_mean"], 1) == 21.3, "")
    check("prose: and->or R@100 nomic 0.303 -> 0.309 (NFCorpus)", round(n_nf["hybrid_and"]["recall_100"], 3) == 0.303 and round(n_nf["hybrid_or"]["recall_100"], 3) == 0.309, "")
    check("prose: and->or R@100 bge +0.003 (SciFact) and -0.004 (NFCorpus)", round(b_sf["hybrid_or"]["recall_100"] - b_sf["hybrid_and"]["recall_100"], 3) == 0.003 and round(b_nf["hybrid_or"]["recall_100"] - b_nf["hybrid_and"]["recall_100"], 3) == -0.004, "")
    check("prose: nomic repaired hybrid within 0.005 of dense at nDCG@10 either way", abs(n_sf["hybrid_or"]["ndcg_cut_10"] - n_sf["dense"]["ndcg_cut_10"]) <= 0.005 and abs(n_nf["hybrid_or"]["ndcg_cut_10"] - n_nf["dense"]["ndcg_cut_10"]) <= 0.005, "")
    check("prose: nomic R@100 over dense +0.030 and +0.011", round(n_sf["hybrid_or"]["recall_100"] - n_sf["dense"]["recall_100"], 3) == 0.030 and round(n_nf["hybrid_or"]["recall_100"] - n_nf["dense"]["recall_100"], 3) == 0.011, "")
    check("prose: raw OR R@100 within 0.004 of OR either way", abs(b_sf["bm25_or_raw"]["recall_100"] - b_sf["bm25_or"]["recall_100"]) <= 0.004 and abs(b_nf["bm25_or_raw"]["recall_100"] - b_nf["bm25_or"]["recall_100"]) <= 0.004, "")


def main():
    check_sweep()
    check_prose_round2()
    check_beir_table("\\label{tab:beir}", "bge")
    check_beir_table("\\label{tab:nomic}", "nomic")
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
