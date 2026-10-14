The biconditional in Section 2 is intact, and Sections 1–5 do not repeat the two retired claims. The new prose has four sentences a referee can falsify from your own tables, plus one imported production detail.

**Fix before submission**

- Section 6, “What fusion did with an empty list”: “at most 0.002 nDCG@10” on SciFact is false of the printed table. e5 dense is 0.719 and hybrid-and is 0.722. Raw values are 0.719429 and 0.721622, difference 0.002193. The same paragraph’s “0.000 Recall@100” on SciDocs fights Table 7: bge dense Recall@100 is 0.496 and hybrid-and is 0.495 (raw 0.495683 vs 0.495483).
- The named SciFact gain “+0.004” is the raw gap 0.707600 − 0.703265 = 0.004335. Table 2 prints 0.708 and 0.703. NFCorpus “0.008 to 0.013” is the same habit: bge’s raw gap is 0.007543, and nomic’s printed gap is 0.361 − 0.347 = 0.014 (raw 0.013274). Quote one rounding rule and make the prose match the tables.
- “within 0.008 nDCG@10 of bm25-or on five collections” fails on ArguAna: 0.359889 − 0.351521 = 0.008368. Four collections are inside 0.008; ArguAna is not.
- “Where the buggy leg was live on more queries the hybrid did move” is then illustrated with TREC-COVID, 13 live queries. SciDocs has 58 live queries and moves by at most 0.002. TREC is the large move with the smaller live set.
- “one 1,400-character chunk or one abstract” puts the production chunk size onto BEIR. Appendix B indexes title and text of the BEIR document. NFCorpus and FiQA are not 1,400-character chunks.
- Subsection title and abstract, “never useful”: `and_any_relevant_hit` is 1. The body already says so. “Never” is the false word.

**Section 6 figures that match the JSON**

Empty counts 294, 164, 942, 530, 37 and rates 98.0, 50.8, 94.2, 81.8, 74.0. Content-token means 8.73, 7.29, 6.18, 5.68, 2.51, in the same order as those rates. Legs-table ceiling ranges. 3,727 queries × 6 hybrid conditions = 22,362. Excess 176 = 164 (AND) + 12 (OR), and the per-collection excess fractions (2–3/159, 5–7/58, 35–43/118, 7–8/13). Pooled 137/726, 35/588, 4/6,636, the four short-list counts, and 39 firings on legs of four or more. ArguAna: 1,298 and 1,296 and 108; `multi_leg_docs_mean` × 1,406 = 1,410, which is 1,402 singles and 4 doubles if every AND hit is shared. Both-leg means from ≤4.0 to 19.0–43.7. The 5, 9 and 12 pair counts. Named gaps +0.059, +0.027, +0.007, +0.018, and FiQA losses 0.037 to 0.059. FiQA raw-OR +0.009 nDCG@10 and +0.012 Recall@100. The 25/323 NFCorpus remainder.

Not in the summary files, so not checked: the split “174 shared nothing, 2 shared one”; which two of the four FiQA `hybrid-or` excess runs (bge 2, e5 2) are those two; the whole of Table 4, including “11 of those 20 cells” and “within 4.4 points.” The 2,392 figure does follow from 300 + 298 queries, two encoders, and \(n \in \{50, 100\}\).

**Interpretation**

(a) On these five collections the AND-empty rate is strictly ordered by `kept_tokens_mean`. “Corpus size, document length and vocabulary differ along the same ordering” is not true of corpus size: 5,183, 25,657, 57,638, 171,332, 3,633. Keep the five-point order; delete the collinearity claim.

(b) The four quoted short-list rates rise with corpus size. SciFact, omitted there, is 0/18 at 5,183 documents, below NFCorpus’s 13/330 at 3,633. Denominators are encoder runs of one shared keyword list: TREC-COVID 16/18 is six queries, not 18. “Growing with corpus size” is a four-point description, and “Expect more such queries on a large corpus” in the operator section drops the hedge Section 6 and the limitations actually use.

(c) The mechanism is: a query string that is itself an indexed document satisfies its own quoted AND. That can happen in a mailbox or a ticket index. Nothing here measures those systems. “Routinely” is not a result. ArguAna also does not pass a row-count alarm only because 1,402/1,406 legs have length 1; say that, and stop.

(d) Holds for these 18 pairs. Overlap goes to 19–44 shared documents while nDCG@10 rises in 5 of 18, and hybrid-and beats hybrid-or in 12 of 18. The Recall@100 “9” includes NFCorpus bge, raw gap 0.0006. The sentence is a reading of these tables, not a theorem.

**What a referee would still ask for**

1. Required. Paired tests, or intervals, on the existing per-query scores. The 5, 9 and 12 treat +0.004 and +0.0006 as wins, and TREC-COVID has 50 queries. Not a new run.
2. Required. Name the tokenizer and the stopword list in the paper. The 7.7% remainder and the content-token order are defined by them; the PDF currently points at a script.
3. Required. One small table of excess runs by collection, builder and encoder, with the two deep-overlap queries identified. The 174/2 claim is otherwise invisible in the summaries.
4. Optional. A contribution paragraph that states the result as the \(K \le k\) biconditional and the measured error rate at \(K = 100\), \(k = 60\). As written, a 20-page journal slot is being asked to hold a bug report with a half-page derivation.
5. Optional. Cut or appendix Section 5. Those A/Bs are not evidence about the ceiling.
6. Optional. A plot. The monotone five-point order is already a sentence.

**Title and abstract**

The abstract’s \(K \le k\) statement, the 50.8–98.0% range, the miss rate on empty legs, 174 and 2, ArguAna, and 5 of 18 match the body, except “never useful.” “Mostly short lists on large corpora” is looser than the four-point, SciFact-omitted count.

The title has no \(K \le k\) condition. The journal runs use \(K = 100 > k = 60\), where \(\max s(d) \le 1/k\) does not mean zero overlap, and it failed twice. “Found a Dead Retriever” is the production incident, in which the leg was empty. It is not what happened on ArguAna, where the useless leg shares a document and the ceiling never fires.
