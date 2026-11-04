## 1. Readability

The paper reads like it was written by someone who audits numbers for a living — the failure mode now isn't opacity, it's double-anchoring: nearly every quantitative claim carries the printed value, the pre-rounding value, and a count, often in one clause. The audit belongs in the repo; the prose should trust it.

**Sentences that require a second read, with rewrites:**

> "When the keyword retriever's row counts were finally logged, on 2026-08-18, they were zero on every conversational query, and the maximum fused score, which had been $1/60$ on every one of those queries, had twice been written down as ``RRF scores are flat''." (§1)

"Twice" has no referent — §4.3 describes one prior note (2026-08-07). Name the second occasion or drop the count. Rewrite: "When I finally logged the keyword retriever's row counts, on 2026-08-18, they were zero on every conversational query. The maximum fused score on those queries had been $1/60$ — a flatness I had written down the week before as 'RRF scores are flat' (Section 4.3)."

> "In 8 of the 12 the buggy hybrid is not above \textsc{dense} at all: on seven of them its keyword list was empty on 74 to 94\% of queries, and on ArguAna with bge it returned the self-match on every query and a second document on four, with both aggregate metrics identical to every decimal with and without it." (§6.5)

"it" (the document? the metric?) and "with and without it" are unresolvable on first pass. Rewrite: "Eight of the twelve are not wins at all. In seven, the keyword list was empty on 74–94% of queries — the buggy hybrid is \textsc{dense} under another name. The eighth is ArguAna with bge, where the AND list returned the self-match on every query and a second document on four, leaving both metrics identical to every decimal."

> "Only on NFCorpus (all three encoders) and SciFact with bge is the buggy hybrid above \textsc{dense} as well, by 0.001 on SciFact and by 0.008 to 0.014 on NFCorpus (significant for nomic and e5), where the AND list was nonempty on half the queries and held exact-match lists of four or more documents on 86 of those 159." (§6.5)

Four numbers and a parenthetical in one sentence; the trailing "where" clause redefines scope mid-sentence. Split at "(significant for nomic and e5)."

> "at Recall@100 it is above in 9 (one significant; the ninth, NFCorpus with bge, by 0.0006, which the table rounds to a tie)" (§6.5)

"the ninth" implies an ordering that doesn't exist. "one of them, NFCorpus with bge, is above by 0.0006 — inside the table's rounding."

**Multi-number clauses:** "(0.0022 and 0.0000 before rounding)" and "(0.0017 before rounding)" (§6.5); "(124 of 378 pooled)" (§6.2); "612 of the 726 runs in the first bucket, at the ceiling on 132 of them, against 5 of 114" (§6.2 — "them" is the 612, but buried). Keep the printed value; drop the rest.

**Machine-written residue:** "That is close to arithmetic." (§6.1) — a hedge containing no claim; you mean "ordering by kept tokens reproduces the empty-rate ordering exactly." "whether or not the list was any good" (§6.2) — a pre-emptive tail answering an objection nobody raised; delete. The abstract's final third is a compressed results section; split "It also appeared over 174 nonempty keyword lists ... and twice over lists that shared one document deep in both, the case $K > k$ leaves open" into two sentences.

## 2. Correctness

One rule violation, and it's the worst kind to have in this paper: §6.1 quotes FiQA's \textsc{bm25-or-raw} advantage as "0.009 nDCG@10 and 0.012 Recall@100." The printed difference is 0.521 − 0.508 = **0.013**; the raw difference is 0.0125. Under your own stated rule (differences of printed three-decimal values, unless a fourth decimal is given) this must read 0.013 or 0.0125. As printed, it's a third convention — raw difference rounded to three decimals — used exactly once.

- §8: "The production measurements are on ten and fifteen queries" — Appendix A reports 7, 8, and 15. Write "ten for the incident and seven to fifteen for the appendix checks."
- "row counts" is used in §1 ¶4 before its §2 definition; harmless only because "were zero" makes it self-evident. Define at first use.
- Everything else I checked against the JSON holds: the 5/13 nDCG split (2/5 significant), 9/9 Recall split (1/3), 12/6 and-vs-or split (6/2), the 176/174/2 decomposition, Table 3's per-collection counts, the ArguAna facts (1298/1296/108/1), the sweep arithmetic ((n−1)(K−1) ≥ 3600 only at K=100, n∈{50,100}; 8 cells × 598 × 2 = 2,392 runs), and the abstract's claims.

## 3. Structure

Property-first works; the incident is not an afterthought — §2 already cites Table 1, so the two threads cross-refer. §4 is the right length. Keep "What to log" where it is, before Limitations: it's the only section a production engineer will bookmark, and folding it into Conclusion buries it under the effectiveness result. To get 20→16: merge Tables 4–6 into one long table (the six BM25-only rows repeat verbatim three times); cut Figure 1 — §6.2's text already reports every number it shows; move the 118-word stoplist to the repository; halve the batch-size/transformers paragraph in App C.

## 4. Title

Accurate but a clause too long; "Shows When Two Retrievers Agree on Nothing" earns its place only because the paper shows the ceiling is *about* overlap, not health — keep that sense. Alternatives: plain — "A Score Ceiling in Reciprocal Rank Fusion Detects Zero Retriever Overlap"; named — "The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval".

## 5. Prior art

(a) I know of no prior statement of max fused score = 1/k as a test; it's one line of algebra from Cormack et al. 2009, already cited — claiming it as an observation is fair. (b) Closest confident work: **Nuray & Can, "Automatic ranking of information retrieval systems using data fusion," *Information Processing & Management* 42(3), 2006** — estimates retriever quality from agreement among system outputs without judgments; that is per-retriever health estimation from fused output and belongs in §3. Add **Aslam & Montague, "Models for Metasearch," SIGIR 2001** for overlap-based combination analysis alongside the cited Lee 1997. Production monitoring of hybrid legs exists in vendor docs (Vespa, Elastic hybrid search) and observability tools (LangSmith, Arize Phoenix) — real practice, but I can't name a citeable canonical source; mark unsure. (c) No confident citation for a silently inert retriever; the paper plausibly holds that novelty.

## 6. Would you post it?

Yes. A cs.IR reader gets the property by page two, watches it fail gracefully on ArguAna, and leaves with a free diagnostic plus an honest account of where it lies. The one change that would most improve it: enforce one number per clause and strip the "(before rounding)" parentheticals — the paper's credibility is arithmetic discipline, and right now the prose reads like it doesn't trust the audit to live in the repository where it belongs.
