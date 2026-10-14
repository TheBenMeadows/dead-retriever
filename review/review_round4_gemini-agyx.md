# Review: Information Retrieval Research Journal (IRRJ)

## 1. Critical Errors, Inconsistencies, and Rejection Risks

1. **Top-100 list size with $K=60$ (Section 1 and Table 1):** Section 1 states, *"Over the top 100 fused results of those ten queries, the maximum score was exactly $1/60$"*, and Table 1 rows are labeled *"Maximum fused score over the top 100 results"*. With per-retriever cut depth $K=60$, when the keyword leg returns zero documents (5 of 10 queries), the fused list contains at most 60 documents; on the other 4 queries it contains at most 63 documents. A list of 60 items cannot have a "top 100". Clarify whether depth was truncated to $\min(100, |L|)$ or if candidate depth differed from fuse depth.
2. **Relative vs. absolute step arithmetic (Section 1):** In Section 1, the step is defined as the relative difference: $\bigl(1/(k+r) - 1/(k+r+1)\bigr) / \bigl(1/(k+r)\bigr) = 1/(k+r+1)$. The text then claims: *"two live lists that agreed on every document would show the same step at twice the scale"*. This is false. If two lists agree at every rank, $s(r) = 2/(k+r)$ and the relative step is $\frac{2/(k+r) - 2/(k+r+1)}{2/(k+r)} = \frac{1}{k+r+1}$—identically 1.6% and 1.4%. The *absolute* step doubles, but the *relative* step is scale-invariant.
3. **Token count mismatch (Section 3 and Section 9):** Section 3 presents the example query `how do I fix the empty feed` (7 tokens) and its 7 quoted terms (`"how" "do" "i" "fix" "the" "empty" "feed"`), but immediately asserts *"so a six-token conversational query almost never matched"*. Section 9 repeats *"treat zero rows for a six-word query as something to explain"*. Change "six-token" / "six-word" to seven.
4. **Residue from 2-encoder draft (Appendix B):** Appendix B states: *"The GPU runs of the four original SciFact and NFCorpus pairs reproduced the CPU results to every digit"*. With three encoders, SciFact and NFCorpus have six pairs. The phrase *"four original... pairs"* is an unedited holdover from the 2-encoder version.
5. **Misattributed citations (Section 5 and Section 7):**
   - Section 5 cites \citet{nogueira2019doc2query} for prepending `kind: title`: *"This is a heading prefix, the cheapest form of document expansion \citep{nogueira2019doc2query}"*. Doc2query is neural query prediction appended to text; metadata/heading prepending is not doc2query.
   - Section 7 asserts: *"CombSUM and CombMNZ \citep{fox1994combination} reward documents returned by several systems"*. CombSUM simply sums scores; CombMNZ is the specific formulation that scales by the number of non-zero systems to reward multi-system agreement.
6. **Flawed explanation for 12/18 nDCG@10 wins (Section 6.5):** Section 6.5 speculates: *"A plausible mechanism... is that where the AND builder fired at all it returned a short list of exact matches that ranked well at depth 10, while the OR list adds candidates that... dilute depth 10"*. On SciDocs and SciFact, `hybrid-and` was empty on 94.2% and 98.0% of queries; `hybrid-and` outperformed `hybrid-or` not because exact matches were superior, but because the leg was completely dead on 95–98% of queries, leaving the strong dense ranking undiluted.

---

## 2. Section 6 Numbers Spot-Check

- **Table 1 (`tab:legs`), AND-empty counts, and content-token ordering:** Verified against `keyword_facts.json` and result summaries. Monotonic content-token means (8.7, 7.3, 6.2, 5.7, 2.5) match empty rates (98.0%, 94.2%, 81.8%, 74.0%, 50.8%).
- **ArguAna counts (Section 6.2):** 1,402 queries with 1 document and 4 queries with 2 documents yield $\frac{1402 \times 1 + 4 \times 2}{1406} = 1.002845$, reproducing `multi_leg_docs_mean` of 1.0028. Identifier counts (1,298 self, 1,296 rank-1, 108 other) match `keyword_facts.json`.
- **Excess ceiling counts (Section 6.4):** Verified. Buggy excess totals 164 across NFCorpus (8), SciDocs (18), FiQA (115), TREC-COVID (23). Fixed excess totals 12 across SciDocs (3), FiQA (4), NFCorpus (5). Total is 176.
- **Natural row-count rates (Section 6.4):** Verified against `natural_lengths.json` for 1–3 (137/726 = 18.9%), 4–49 (35/588 = 6.0%), 50–100 (4/6636 = 0.1%), and collection breakdowns.
- **Effectiveness counts (Section 6.5):**
  - `hybrid-or` > `dense` at nDCG@10 in 5 of 18 pairs: SciFact (nomic, e5), ArguAna (nomic, e5), TREC-COVID (e5).
  - `hybrid-and` > `hybrid-or` at nDCG@10 in 12 of 18 pairs.
  - `hybrid-or` > `dense` at Recall@100 in 9 of 18 pairs. **Warning:** In Table 3, NFCorpus under bge shows `0.337` for dense and `0.337` for `hybrid-or`. The raw values are 0.33672 vs 0.33731 (+0.00059). A referee checking Table 3 will count only 8 gains unless Table 3 displays a fourth decimal or the text notes the rounded tie.
- **Table 7 and Section 6.6 prose discrepancies:**
  - Prose states: *"a cap of three on 2.7 to 6.7%"* and *"a cap of ten on 0.7 to 2.3%"*. In Table 7 (bge), $n=3$ at $K=60$ shows 2.7% and 6.0% (not 6.7%); $n=10$ at $K=60$ shows 1.0% and 2.3% (0.7% occurs at $K=100$).
  - Prose states: *"under 1% in 11 of those 20 cells"*. Table 7 contains only 10 cells for $n \ge 20$.
  - *Cause:* The text incorporates unprinted `nomic` sweep runs without stating so. Clarify that the text quotes the envelope across both bge and nomic, or include nomic in Table 7.

---

## 3. Interpretation Audit

- **(a) Empty rate ordered by content tokens:** Stated fairly. The text explicitly cautions: *"Five collections are too few to call this a law, and corpus size, document length and vocabulary differ along the same ordering."*
- **(b) Short-list disjointness growing with corpus size:** **Overstated.** Section 6.4 lists NFCorpus (3.6k), SciDocs (26k), FiQA (58k), and TREC-COVID (171k) as an increasing sequence. However, SciFact has 5.2k documents (larger than NFCorpus) and had 0 disjoint lists in 18 runs (0.0%); ArguAna (8.7k docs) had 0 disjoint lists in 4,218 runs. Selecting four collections while omitting SciFact and ArguAna creates a false appearance of monotonicity.
- **(c) ArguAna self-match generalizing to mailboxes/notes:** **Overstated.** ArguAna queries are 195-token arguments matching entire corpus documents. Real queries against personal archives are short phrases; they do not trigger the 195-token exact-AND pathology where a query matches only its identical source document.
- **(d) "A monitor for leg health and a verdict on retrieval effectiveness are different instruments":** **Sound.** Supported directly by the data: fixing the AND bug restored lexical overlap everywhere, but reduced nDCG@10 compared to dense alone in 13 of 18 pairs.

---

## 4. Journal Fit (IRRJ)

1. **Significance testing (Required):** The paper reports effectiveness gains and losses across 18 pairs with single point estimates and disclaims paired uncertainty; IRRJ reviewers will require paired t-tests or Wilcoxon signed-rank tests with multiple-testing correction to substantiate whether hybrid differences are meaningful.
2. **Score distribution visualization (Required):** The submission lacks a figure; a plot showing the score distribution across ranks, the $1/k$ ceiling line, and the hyperbolic boundary $r_1 r_2 = k^2$ is needed to make the mathematical mechanics accessible.
3. **Related work scope (Optional):** Expand Section 7 beyond basic fusion citations to include modern reciprocal rank and score-combination analyses (e.g., CombMNZ variations, RBO diagnostics, and recent hybrid search benchmarking).
4. **Benchmark hardware consistency (Optional):** Address the confounding of reporting CPU query latencies for SciFact/NFCorpus alongside GPU/T4 host latencies for the other four collections by providing standardized hardware timings.

---

## 5. Abstract and Title Audit

- **Title:** *"A Score Ceiling in Reciprocal Rank Fusion Detects Zero Overlap, and Found a Dead Retriever"* is acceptable for an incident-driven paper, but note that for $K > k$, the ceiling only detects zero overlap near the top ranks, and as shown on ArguAna, it cannot detect a dead retriever that returns the query text.
- **Abstract line 7:** *"two working retrievers can return disjoint lists, and in the incident four of ten queries did."* In the incident, the keyword retriever was **not** a working retriever; it was the broken quoted-AND implementation that returned 1–3 chunks on short queries. Revise to: *"two retrievers can return disjoint lists, and in the incident the buggy builder and the vector retriever did on four of ten queries."*
- **Abstract line 4:** *"A result list whose maximum fused score is $1/k$ therefore contains no document that both retrievers returned."* Add the condition *"with $K \le k$"*; Section 6.4 demonstrates that at $K=100 > k=60$, this deduction fails (the two FiQA runs).
