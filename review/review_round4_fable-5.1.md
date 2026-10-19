## Review, round 4 (dead-retriever, IRRJ draft) — Fable 5.1 (fresh subagent, read only the inline brief)

### 1. Things that would get it rejected or embarrass the author

**R1. Sweep ranges in §6.6 text vs. Table 5 caption are not mutually consistent.** The text says "Three things hold in every cell for both encoders" and then "a cap of one document leaves the lists disjoint on 8.7 to 15.1% of queries". 8.7 and 15.1 are exactly the bge $K=60$, $n=1$ cells. The caption says nomic's figures are "within 4.4 points of these at $n=1$", so nomic's $n=1$ cells may lie outside 8.7–15.1. Either the range is bge-only (say so) or widen it. The $n=3$ range "2.7 to 6.7%" already includes a non-bge value (bge has 2.7 and 6.0), so the text pools encoders at $n=3$ but apparently not at $n=1$. Same for "a cap of twenty or more on at most 1.7%": bge's max is 1.7 and nomic may be up to 2.7 under the caption's tolerance. "Under 1% in 11 of those 20 cells": bge gives 4 of 10 (SciFact 0.3, 0.0, 0.0, 0.0); the nomic 7 are not inline, state them or drop the count.

**R2. §6.1: "within 0.008 nDCG@10 of bm25-or on five collections"** — ArguAna: 0.35989 − 0.35152 = 0.0084 (JSON). Say "within 0.009" or "0.0084".

**R3. Abstract: "two working retrievers can return disjoint lists, and in the incident four of ten queries did."** The four were the buggy AND builder returning 1–3 chunks (Table 1 caption). That is a live leg, not a working retriever. Write "two live lists" or "a live but nearly empty leg".

**R4. §1 and Table 1: "top 100 fused results" at $K = k = 60$ with a dead leg.** Two lists of ≤60 that share nothing give ≤63 fused results; "top 100" is a cap, not a count. One clause ("the fused list, capped at 100") fixes it.

**R5. Recall@100 count "9 of 18" cannot be reproduced from Table 4.** NFCorpus/bge prints 0.337 vs 0.337; the JSON (0.33731 vs 0.33672) decides it. A referee counting from the table gets 8 plus a tie. Either print four decimals for that row or footnote it.

**R6. Rounding in Appendix A:** SciDocs hybrid-and nomic both-leg prints 0.17; JSON is 0.165 (round-half-even gives 0.16). Trivial, but the audit script should be the one deciding.

### 2. Section 6 numbers (all recomputed from the inline JSON unless stated)

Verified: Table 2 every cell (docs, queries, token means, empty rates, ceiling ranges per encoder: NFCorpus 51.4/51.7/51.7, SciDocs 94.7/94.8/94.9, FiQA 87.2/87.5/88.4, TREC-COVID 88/90/90; OR: NFCorpus 7.7/8.4/8.7, FiQA 0/0.3/0.3). AND-empty 294/164/942/530/37. Content tokens 8.7/7.3/6.2/5.7/2.5 with rates 98.0/94.2/81.8/74.0/50.8. 25 NFCorpus OR-empties (0.0774×323). ArguAna 1406/1298/1296/108/1 relevant; the 1402/4 split is not in the summary JSON but `multi_leg_docs_mean` 1.0028 = (1402+8)/1406 confirms it. 22,362 = 6×(300+323+1406+1000+648+50). Excess ceilings: NFCorpus 3/2/3 (1.3–1.9%), SciDocs 7/5/6 (8.6–12.1%), FiQA 35/43/37 (29.7–36.4%), TREC-COVID 8/8/7 (53.8–61.5%) = 164; fixed builder 5+3+4 = 12; 176 total; pooled fired 137+35+4 = 176; live runs 726+588+6636 = 7950 = 13,926 − 5,976 empties. Per-collection 13/330, 18/141, 90/219, 16/18. 39 = 35+4 over four-plus legs, all FiQA/TREC-COVID/SciDocs. The 2 $K>k$ leaks sit inside FiQA's 4 fired in the 50–100 bucket, consistent with hybrid-or FiQA at-ceiling 2+2+0. Effectiveness: h-or > dense nDCG in 5 (SciFact nomic/e5, ArguAna nomic/e5, TREC-COVID e5), Recall in 9, h-and > h-or nDCG in 12. Gains +0.059/+0.027/+0.004/+0.007/+0.018; FiQA losses 0.037–0.059; BM25 0.360 beats nomic 0.356 and e5 0.329. §6.3: SciFact and SciDocs h-and vs dense ≤0.002 nDCG (e5 SciFact 0.0022, marginal), Recall 0.000; NFCorpus +0.008–0.013; TREC-COVID −0.027 to −0.039. Timings 2.6× (NFCorpus) to 18× (ArguAna), FiQA 5.8×, raw better on FiQA by 0.009/0.012. Both-leg means: max 4.0 (NFCorpus bge 4.006), 19.0–43.7 after fix. Sweep arithmetic: $(n-1)(K-1) \ge 3600$ holds only at $K=100$, $n \ge 38$; 8 cells × 299 = 2,392. Formula checks in §1–2 ($1/61 = 1.6\%$, $1/71 = 1.4\%$, $r_1 r_2 < k^2$, $2/150 < 1/60$) are correct.

Not reproducible from inline data (the audit script must carry them): the 1402/4 split, "dense leg returns that document in its top 100 on every query", "174 of 176 shared no document", and the nomic sweep cells.

### 3. Interpretation

(a) Content-token ordering: five points, confounded, and the paper says so; but the ordering of raw tokens already matched on four of five, so content tokens fix one inversion (TREC-COVID). State that it is one inversion repaired, not a new law.
(b) Corpus-size disjointness: the four rates (3.9, 12.8, 41.1, 88.9%) are monotone, but the TREC-COVID 16/18 is six distinct queries × three encoders. Write "six queries" in the sentence; the Limitations paragraph does not say it.
(c) ArguAna generalisation: "a search engine over a mailbox, a notes vault or a ticket tracker routinely receives the text of an indexed item as a query" is asserted, not measured; the mechanism needs the verbatim text. "Can receive" is what the evidence supports.
(d) "Different instruments": supported, but the 12-of-18 count includes differences of 0.003 (SciDocs nomic, e5) with no paired test; without (4.1) the count is a tally of signs.

### 4. Journal fit, ranked

1. **Required.** Paired significance (bootstrap or Wilcoxon over queries, per-query rows exist) on Tables 3–4; the "5/9/12 of 18" counts and the FiQA losses need it, and the caption already concedes the gap.
2. **Required.** Conventional structure: an Introduction that states contributions, Related Work before §6 rather than after it; IRRJ referees expect it and will say so.
3. **Likely asked.** One sentence placing `bm25-or` against the published BEIR BM25 baselines per collection, so the referee can see FTS5's BM25 is in the normal range rather than a weak straw leg.
4. **Optional.** One figure: the $1/60, 1/61, \ldots$ staircase from the incident, or ceiling rate against keyword row count pooled across collections.
5. **Optional.** Confidence intervals or per-encoder values in Table 2's ceiling ranges instead of ranges.

### 5. Abstract and title

Title matches the body. Abstract: fix R3; "mostly short lists on large corpora" is supported (137 of 176 are 1–3 documents; 163 of 176 on the three corpora ≥25k). "Improves nDCG@10 ... in 5 of 18" reads as a positive; add "and is below it in 13" so the abstract claims what Table 3 shows. "Agrees to the third decimal" (§6.2) understates: the ArguAna hybrid-and and dense figures are identical in the JSON; say "identical".
