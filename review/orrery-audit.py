#!/opt/homebrew/bin/python3
"""Deterministic audit of the paper's machine-checkable claims. Log-only.

Checks, each PASS or FAIL with the evidence:
  1. Every number in Tables 2 and 3 of paper/main.tex equals the value in
     results/*.json at the rounding the table shows.
  2. The ceiling inequality 2/(k+K-1) > 1/k holds iff K <= k, numerically over a grid.
  3. hybrid.ceiling_report flags a synthetic dead leg and clears a live one.
  4. The prose figures for the BEIR section (98.0%, 50.8%, 51.7%, 7.7%, 8.4%,
     "three queries", "two queries", "within 0.008", "identical Recall@100")
     follow from the result files.
Writes review/orrery-audit.md and exits 1 on any FAIL.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dead_retriever import RRF_K, ceiling_report, rrf_fuse  # noqa: E402

TEX = (ROOT / "paper" / "main.tex").read_text()
RES = {p.name: json.loads(p.read_text()) for p in (ROOT / "results").glob("*.json")}
OUT = []


def check(name, ok, evidence):
    OUT.append((name, ok, evidence))


def table_rows(tex, label):
    """Rows of the tabular whose \\label follows it: list of cell lists."""
    i = tex.index(label)
    start = tex.rfind("\\begin{tabular}", 0, i)
    end = tex.index("\\end{tabular}", start)
    rows = []
    for line in tex[start:end].split("\n"):
        line = line.strip()
        if "&" in line and not line.startswith(("\\toprule", "\\midrule", "\\bottomrule")):
            rows.append([c.strip().rstrip("\\").strip() for c in line.split("&")])
    return rows


def pct(s):
    return float(s.replace("\\%", "").replace("%", "")) / 100.0


def check_table(label, encoder_file_part):
    rows = table_rows(TEX, label)
    coll_map = {"SciFact": "beir_scifact_test", "NFCorpus": "beir_nfcorpus_test"}
    for cells in rows:
        if cells[0] not in coll_map:
            continue
        coll, cond = cells[0], cells[1].replace("-", "_")
        fname = f"{coll_map[coll]}__{encoder_file_part}.json"
        r = RES[fname]["conditions"][cond]
        got = {"ndcg": r["ndcg_cut_10"], "r100": r["recall_100"]}
        exp_ndcg, exp_r100 = float(cells[2]), float(cells[3])
        check(f"{label} {coll} {cond} nDCG@10", round(got["ndcg"], 3) == exp_ndcg, f"json {got['ndcg']:.4f} vs tex {exp_ndcg}")
        check(f"{label} {coll} {cond} R@100", round(got["r100"], 3) == exp_r100, f"json {got['r100']:.4f} vs tex {exp_r100}")
        if cells[4] != "--":
            key = "empty_rate" if "empty_rate" in r else "keyword_empty_rate"
            check(f"{label} {coll} {cond} kw empty", round(r[key], 3) == round(pct(cells[4]), 3), f"json {r[key]:.4f} vs tex {cells[4]}")
        if cells[5] != "--":
            check(f"{label} {coll} {cond} at ceiling", round(r["at_ceiling_rate"], 3) == round(pct(cells[5]), 3), f"json {r['at_ceiling_rate']:.4f} vs tex {cells[5]}")
        if cells[6] != "--":
            # Compared at the precision the cell shows (0.02 has two decimals, 28.4 has one).
            dec = len(cells[6].split(".")[1]) if "." in cells[6] else 0
            check(f"{label} {coll} {cond} both-leg", round(r["multi_leg_docs_mean"], dec) == float(cells[6]), f"json {r['multi_leg_docs_mean']:.3f} vs tex {cells[6]}")


def check_inequality():
    bad = []
    for k in range(1, 201):
        for K in range(1, 301):
            holds = 2.0 / (k + K - 1) > 1.0 / k
            if holds != (K <= k):
                bad.append((k, K))
    check("ceiling inequality 2/(k+K-1) > 1/k iff K <= k, k,K in [1,200]x[1,300]", not bad, f"{len(bad)} exceptions" + (f", first {bad[:3]}" if bad else ""))


def check_diagnostic():
    s, r = rrf_fuse({"dense": ["a", "b", "c"], "keyword": []})
    rep = ceiling_report(s, r)
    check("ceiling_report flags an empty leg", rep.at_ceiling and rep.empty_legs == ["keyword"] and abs(rep.max_score - 1 / RRF_K) < 1e-12,
          f"max {rep.max_score:.6f} ceiling {rep.ceiling:.6f} empty {rep.empty_legs}")
    s, r = rrf_fuse({"dense": ["a", "b"], "keyword": ["b", "z"]})
    rep = ceiling_report(s, r)
    check("ceiling_report clears a live two-leg list", not rep.at_ceiling and rep.multi_leg_docs == 1, f"max {rep.max_score:.6f} multi {rep.multi_leg_docs}")
    # Depth K = k: two last-place hits still beat one first-place hit.
    k = RRF_K
    s2, _ = rrf_fuse({"a": [f"d{i}" for i in range(k)], "b": [f"e{i}" for i in range(k - 1)] + [f"d{k-1}"]})
    check("K=k: a document last in both legs outscores a document first in one", s2[f"d{k-1}"] > s2["d0"], f"{s2[f'd{k-1}']:.6f} > {s2['d0']:.6f}")


def check_prose():
    bge_sf = RES["beir_scifact_test__BAAI_bge-base-en-v1.5.json"]["conditions"]
    bge_nf = RES["beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json"]["conditions"]
    nq_nf = RES["beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json"]["n_queries"]
    check("prose: SciFact AND empty 98.0%", round(bge_sf["bm25_and"]["empty_rate"], 3) == 0.980, f"{bge_sf['bm25_and']['empty_rate']:.4f}")
    check("prose: NFCorpus AND empty 50.8%", round(bge_nf["bm25_and"]["empty_rate"], 3) == 0.508, f"{bge_nf['bm25_and']['empty_rate']:.4f}")
    diff_and = round((bge_nf["hybrid_and"]["at_ceiling_rate"] - bge_nf["hybrid_and"]["keyword_empty_rate"]) * nq_nf)
    diff_or = round((bge_nf["hybrid_or"]["at_ceiling_rate"] - bge_nf["hybrid_or"]["keyword_empty_rate"]) * nq_nf)
    check("prose: NFCorpus ceiling minus empty = three queries (hybrid-and)", diff_and == 3, f"{diff_and} of {nq_nf}")
    check("prose: NFCorpus ceiling minus empty = two queries (hybrid-or)", diff_or == 2, f"{diff_or} of {nq_nf}")
    same = abs(bge_sf["hybrid_and"]["recall_100"] - bge_sf["dense"]["recall_100"]) < 1e-9
    check("prose: SciFact hybrid-and R@100 identical to dense", same, f"{bge_sf['hybrid_and']['recall_100']:.6f} vs {bge_sf['dense']['recall_100']:.6f}")
    d = abs(bge_sf["hybrid_and"]["ndcg_cut_10"] - bge_sf["dense"]["ndcg_cut_10"])
    check("prose: SciFact hybrid-and nDCG within 0.002 of dense", d <= 0.002, f"diff {d:.4f}")
    dr = abs(bge_nf["hybrid_and"]["recall_100"] - bge_nf["dense"]["recall_100"])
    dn = abs(bge_nf["hybrid_and"]["ndcg_cut_10"] - bge_nf["dense"]["ndcg_cut_10"])
    check("prose: NFCorpus hybrid-and differs from dense by under 0.005 R@100 and under 0.008 nDCG", 0 < dr < 0.005 and 0 < dn < 0.008, f"R@100 diff {dr:.4f}, nDCG diff {dn:.4f}")
    nom_sf = RES["beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json"]["conditions"]
    gain = nom_sf["hybrid_or"]["recall_100"] - nom_sf["dense"]["recall_100"]
    check("prose: nomic SciFact hybrid-or gains ~3 points R@100 over dense", 0.025 <= gain <= 0.035, f"gain {gain:.4f}")
    # The sentence "ceiling rate ... to within one percentage point" over all four hybrid rows.
    worst = 0.0
    for r in RES.values():
        for cond in ("hybrid_and", "hybrid_or"):
            c = r["conditions"][cond]
            worst = max(worst, abs(c["at_ceiling_rate"] - c["keyword_empty_rate"]))
    check("prose: ceiling rate within one percentage point of empty rate, all hybrid rows", worst < 0.01, f"worst gap {worst*100:.2f} pp")


def main():
    check_table("\\label{tab:beir}", "BAAI_bge-base-en-v1.5")
    check_table("\\label{tab:nomic}", "nomic-ai_nomic-embed-text-v1.5")
    check_inequality()
    check_diagnostic()
    check_prose()
    fails = [o for o in OUT if not o[1]]
    lines = ["# Orrery audit of paper/main.tex against results/ and dead_retriever/ (log-only)", "",
             f"{len(OUT) - len(fails)} PASS, {len(fails)} FAIL", ""]
    for name, ok, ev in OUT:
        lines.append(f"- {'PASS' if ok else 'FAIL'}  {name}  ({ev})")
    (ROOT / "review" / "orrery-audit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:3] + [l for l in lines[4:] if l.startswith("- FAIL")]))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
