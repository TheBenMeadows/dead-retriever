## 1. What would get it rejected or embarrass the author

**The abstract's effectiveness sentence is wider than the body.** "Repairing the leg … improves nDCG@10 over the vector retriever alone in 5 of 18 collection–encoder pairs" contradicts §6.6's own caption ("Single runs; no paired uncertainty is reported, so differences are read as observed magnitudes, not as significant") and suppresses the fact §6.6 records: the buggy hybrid is above the repaired one in 12 of 18. The modal outcome is the reverse of the headline. Write it as "is above dense in 5 and below in 13".

**A figure that does not follow.** §6.6: "The two largest gains are on ArguAna, the one collection where BM25 (0.360) beats two of the encoders at nDCG@10 (e5 +0.059 and nomic +0.027)". The +0.059/+0.027 are the hybrid-or-over-dense gains from the preceding clause, re-used where a reader must read them as BM25's margins. The margins are +0.031 (0.360 vs 0.329) and +0.004 (0.360 vs 0.356). The clause "beats two of the encoders" is true; the parentheses attached to it are not.

**Title.** "and Found a Dead Retriever" is not the discovery path §1 describes: the leg was found by logging row counts on 2026-08-18, after the 1.4% flatness had been "misread twice"; the scores "had said so from the start" only in retrospect. The ceiling did not find it. "Detects Zero Overlap" also omits K ≤ k, which §2 bounds in a full paragraph and which §6's K = 100 breaches in one direction (two runs).

**Unreproducible from the attachments.** The sweep JSON is not inline, and §6.5's prose mixes encoders while Table 4 shows only bge:
- "a cap of three on 2.7 to 6.7%" — Table 4's n = 3 row is 2.7, 1.0, 6.0, 3.4. 6.7 appears nowhere; if it is nomic, say so.
- "under 1% in those … 20 cells" — from Table 4 (bge) I count 4 of the 10 cells at n ≥ 20 under 1% (0.3% at SciFact n = 50, K = 60; 0.0% ×3, K = 100). The other 7 would have to be nomic's, which the paper does not print. Print both encoders or state the split.
- "4 of 6,636 with 50 or more (0.1%)" — 4/6,636 = 0.06%.
- 1/60 is given as 0.0166 in §1 and 0.0167 in Table 2.

Also: `nogueira2019doc2query` is cited as "the cheapest form of document expansion"; doc2query is the learned, expensive form, and the sentence's antecedent is a heading prefix.

## 2. Numbers that do reproduce

Everything else I checked holds, including the ones most exposed: Tables 1–4 against `beir_*.json` (all 18 pairs, both metrics, all ceiling rates); the empty counts 294/940/…/164 and 25; content tokens 8.7/7.3/6.2/5.7/2.5 against empty 98.0/94.2/81.8/74.0/50.8; ArguAna's 1,402/1,406, 1,298/1,296/108, one relevant hit; the excess 176 = 164 + 12; the per-collection rates 2–3/159, 5–7/58, 35–43/118, 7–8/13 and their percentages; the pooled buckets 137/726, 35/588, 4/6,636, 13/330, 18/141, 90/219, 16/18; the 39 four-or-more runs; 5/9/12; "22,362" (= 6 × 3,727) and "2,392 query runs" (= 4 × (300+298)); the timing ratios; the 4.4-point and (n−1)(K−1) ≥ k² arithmetic in §2 and §6.5. The identity 137 + 35 + 4 = 176 closes exactly, so the natural-lengths file and the excess counts are mutually consistent — the disagreement is only in what the prose quotes from them.

## 3. Interpretation

(a) The body hedges ("Five collections are too few to call this a law…"); the abstract does not. More seriously, the predictor is nearly the mechanism: the AND leg requires *every* quoted token present, so content-token count *is* conjunct count, and the ordering is close to arithmetic rather than a finding about collections. Say that; a referee will otherwise call it a tautology presented as an observation.

(b) Four points (3.9/12.8/41.1/88.9%), monotone, confounded with query style and document length. §8 hedges; §9's "Expect more such queries on a large corpus" is an imperative prediction from four points. Soften §9.

(c) Not supported as stated. "a search engine over a mailbox, a notes vault or a ticket tracker routinely receives the text of an indexed item as a query" is an assertion about systems you did not measure, and the mechanism requires the whole query text to be an indexed document verbatim — true on ArguAna by construction, accidental elsewhere. Downgrade to "can".

(d) Supported: the diagnostic was exact while the fused-metric verdict ran both ways. But add the sentence a referee will demand — what the operator should do with a leg that is healthy and a hybrid that is worse in 12 of 18.

## 4. Journal fit, ranked

1. **Require:** paired significance (bootstrap or t) on every dense/h-and/h-or comparison. Per-query rows exist; this decides acceptance.
2. **Require:** related work as its own section before the experiments. One paragraph placed after the results is thin for IRRJ, and the most relevant prior work (monitoring retrieval systems) is one citation.
3. **Require:** contributions list, and a methods subsection in the body rather than split between §6 and Appendix B.
4. Optional, cheap: both encoders in the sweep table.
5. Optional, near-always asked: one figure (score histogram from the incident, or empty rate vs content tokens).
6. Optional: a second keyword engine (Lucene/Anserini) to show the failure is the builder, not FTS5.
7. Optional: trim §4; it is already correctly disclaimed.

## 5. Abstract and title

The abstract's derivation matches the body exactly, with K ≤ k carried. Two claims must change: "in the order of their content words per query" (see 3a) and "improves nDCG@10 … in 5 of 18" (see 1). Also "repairing the leg restores overlap on every collection" — on ArguAna the AND leg already shared a document (both-leg 1.003) and the fused list equalled dense's; overlap was never zero there, so "increases overlap" is the accurate verb. The title should drop "Found" and either carry K ≤ k or leave it to the abstract.
