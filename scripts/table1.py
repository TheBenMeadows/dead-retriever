#!/opt/homebrew/bin/python3
"""Print the rows of the paper's Table 1 from results/production-aggregates.json."""
import json
from pathlib import Path

A = json.loads((Path(__file__).resolve().parents[1] / "results" / "production-aggregates.json").read_text())
k = A["keyword_leg_2026-08-18"]
rows = [
    ("Queries on which the keyword leg returned any row", f"{k['queries_keyword_returned_rows_before']} / {k['queries']}", f"{k['queries_keyword_returned_rows_after']} / {k['queries']}"),
    ("Queries with a document found by both legs", f"{k['queries_with_document_in_both_legs_before']} / {k['queries']}", f"{k['queries_with_document_in_both_legs_after']} / {k['queries']}"),
    ("Maximum fused score over the top 100 results", f"$1/60 = {k['max_fused_score_top100_before']:.4f}$", f"{k['max_fused_score_top100_after_range'][0]} -- {k['max_fused_score_top100_after_range'][1]}"),
    ("Keyword leg latency, conversational queries", "--", f"{k['keyword_latency_ms_after_range'][0]} -- {k['keyword_latency_ms_after_range'][1]}\\,ms"),
]
for r in rows:
    print(" & ".join(r) + r" \\")
