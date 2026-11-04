The introduction claims a test the theorem does not give. That is the defect that still makes the paper hard to finish. Everything else is downstream of it.

## 1. The scores do not make the distinction the opening promises

Introduction, paragraph 3:

> "The fused scores can make that distinction."

The distinction just named is "found nothing relevant" versus "the keyword retriever is broken." Section 2 says the opposite, under **It is a statement about overlap, not about either retriever**: the same ceiling from two full disjoint lists, from a list of one or two documents, and from an empty list. The abstract already has the repair ("The test measures overlap, not health… row counts tell the two cases apart"). The contribution list and Section 6 do too. A reader who takes the third paragraph as the claim has the wrong theorem, and Related work restates it: "This paper is about a failure upstream of that choice, where one of the lists is empty." ArguAna is the section where the list is never empty.

Rewrite the introduction sentence: "At \(K \le k\), a maximum of \(1/k\) means the two lists share no document. It does not mean either list is empty. The per-retriever row counts separate an empty list, a short list, and two full disjoint lists."

Replace the Related work sentence with: "The property sits upstream of the choice of fusion function: it is a fact about the scores RRF has already assigned, whether or not either list is empty."

Same split in the definition, one paragraph later. The displayed equivalence is \(\max_d s(d) \le 1/k\). The next sentence names "at the ceiling" as a maximum that **is** \(1/k\), then defines it as \(\max_d s(d) \le 1/k + 10^{-12}\). Use the inequality everywhere. Equality is the typical case (a rank-0 singleton), not the statement.

## 2. Sentences a reader measures twice

**The \(K > k\) condition** (Section 2, second qualification) packs an example, a boundary case, and the actual predicate into one sentence:

> "With \(K > k\), a document ranked deep in both lists scores below \(1/k\) (rank 90 in both at \(k = 60\) gives \(2/150\)), and one ranked exactly \(k\) in both scores exactly \(1/k\); two ranks \(r_1, r_2\) combine to more than \(1/k\) exactly when \(r_1 r_2 < k^2\)."

"Rank 90" and "exactly \(k\)" fight the constant \(k\). The product is right for the paper's 0-based ranks: \(1/(k+r_1)+1/(k+r_2) > 1/k \iff r_1 r_2 < k^2\). Lead with it.

Rewrite: "A document at 0-based ranks \(r_1\) and \(r_2\) scores above \(1/k\) if and only if \(r_1 r_2 < k^2\). Ranks 60 and 60 score exactly \(1/60\); ranks 90 and 90 score \(2/150\). A maximum of \(1/k\) therefore rules out a shared top document at any depth, and when \(K > k\) it leaves open any pair of ranks whose product is at least \(k^2\)."

**The relative step** (Section 4.3) is the same shape, and it is the sentence that earns its place in the incident:

> "Between consecutive singleton scores, the relative step of the formula is \(\bigl(1/(k+r) - 1/(k+r+1)\bigr) / \bigl(1/(k+r)\bigr) = 1/(k+r+1)\): 1.6% at the top of the list and 1.4% around rank 10."

The algebra checks. Split it. "Consecutive singleton scores fall by a relative step \(1/(k+r+1)\): \(1/61\) at rank 0 and \(1/71\) near rank 10. Two identical lists would show the same steps at twice the score. What marked the ten queries was the scale: every score was one term \(1/(k+r)\)."

**Section 5.5, the abstention paragraph**, is where the results become unread:

> "In 8 of the 12 the buggy hybrid is not above \textsc{dense} at all: on seven of them its keyword list was empty on 74 to 94% of queries, and on ArguAna with bge it returned the self-match on every query and a second document on four, with both aggregate metrics identical to every decimal with and without it."

Rewrite: "On 8 of those 12 pairs the buggy hybrid does not beat the dense retriever. On seven, the keyword list was empty for 74–94% of queries, so the hybrid is the dense list on most queries. The eighth is ArguAna with bge: the keyword list is the self-match, and both metrics match the dense retriever exactly."

**One number would do**, in the abstract's experimental sentence (50.8–98.0%, 22,362, 174, and the two deep shares in a single "It also…") and in Section 5.4:

> "Pooling the two encoders' cells (Table~\ref{tab:sweep} prints bge's) at \(K = 60\): a cap of one document leaves the lists disjoint on 8.7 to 15.1% of queries, a cap of three on 2.7 to 6.7%, a cap of ten on 0.7 to 2.3%, and a cap of twenty or more on at most 1.7%, under 1% in 11 of the 20 cells at \(n \ge 20\) over both depths and both encoders."

Rewrite: "At \(K = 60\), a cap of one document leaves the lists disjoint on 8.7–15.1% of these queries, and a cap of twenty or more on at most 1.7%. Raising the dense depth to 100 never raises the rate."

**Still machine-written**, by the specific tic:

- Objection nobody raised, then repeated. Setup: "so contrasts between them are observations, not controlled comparisons." Section 5.1: "Five collections are too few to call this a law, and the collections also differ in corpus size, document length and vocabulary." Section 7 says it again. Keep the limitations sentence. Cut the other two.
- "That is close to arithmetic."
- "Two in 22,362 is rare, but it is not zero, and it is why a system that runs at \(K > k\) should count shared documents directly." Section 2 already said why.
- "A monitor for overlap and activity and a verdict on retrieval effectiveness are different instruments." "Instruments" is back, and Section 6's first result sentence repeats the point ("None of these signals is a verdict on effectiveness") without naming nDCG@10. The 5-and-13 split is nDCG@10. At Recall@100 the split is 9 and 9. As written, Section 6 states a metric-specific result as a general one.
- "Two questions run through this section and are kept apart." Cut.
- The AI-tools paragraph is a credit roll. Three lines suffice: who directed the work, that a script checks the numbers, that the records are in the repository.

## 3. Correctness after the moves

The product condition, the \(K \le k\) separation, the one-based shift \(K \le k+1\), the empty-list direction for two retrievers, and the ArguAna counts (1,298 own-id, 108 other-id, 1,296 at rank 0, one relevant hit) agree with Section 2 and `keyword_facts.json`. The 5/13 and 2/5 nDCG claims agree with `significance.json` and Tables 4–5. The 137/726, 35/588, and 4/6,636 rates agree with `natural_lengths.json`. The abstract, the contribution list, and the conclusion stay inside those results. Section 6 does not, on the metric, as above.

Two sentences disagree with the printed appendix under the paper's own rule (differences of printed three-decimal values):

- "worse at nDCG@10 by 0.001 to 0.010 on five collections." Printed `bm25-or` minus `bm25-or-raw` on ArguAna is \(0.484 - 0.473 = 0.011\). The five differences run from 0.001 to 0.011.
- "better by 0.009 nDCG@10 and 0.012 Recall@100" on FiQA. nDCG \(0.233 - 0.224 = 0.009\). Recall \(0.521 - 0.508 = 0.013\).

"2.2 to 18 times slower" with the pair "905 against 52": \(905/52 = 17.4\).

"Read twice" is not in the incident. Section 4.3 records one misreading, on 2026-08-07. The introduction ("had twice been written down") and the conclusion ("it was read twice as a property of fusion") have no second episode.

"Row count" is used in the introduction and defined in Section 2. "At the ceiling" is named twice, as above. No other term is defined two ways. Appendix A does not contradict Section 4.3; it repeats it.

## 4. Structure

Leading with the property is the right order for an arXiv reader. Section 4 is the right length. It reads as the motive, not as an afterthought. The title does not lean on the outage. The abstract's middle and Table 1 do, which is where they belong.

Section 4.3 should lose the dates and the recency-decay story; Appendix A already has that story, and Appendix A is not about the ceiling. Cut Appendix A entirely. Fold Section 6 into the conclusion: the logging paragraph is the conclusion's last sentence expanded, and the effectiveness sentence is Section 5.5 again. Keep Limitations after that, so the prescriptions are not restated and then withdrawn.

That, plus collapsing the three appendix condition tables (the BM25 rows are copied three times) and deleting the batch-size paragraph in the run appendix, is the path from 20 pages to about 16. Do not cut Section 5.3 or the sweep. Those are what keep the ceiling from being read as an empty-list alarm. Do cut the second half of Section 5.5 once the 8-of-12 sentence is the rewrite above.

## 5. Title

"Agree on nothing" matches the overlap theorem and avoids the empty-retriever misreading. It hides \(K \le k\), and "agree" is Lee's word for agreement on relevant documents, which this paper is not measuring.

Plain: "Reciprocal Rank Fusion Scores and Disjoint Ranked Lists."

Names the finding: "When \(K \le k\), an RRF Maximum of \(1/k\) Means the Two Lists Share No Document."

## 6. Prior art

The paper already cites the work that bounds this result. Cormack, Clarke, and Büttcher (2009) give the sum and \(k = 60\). Fox and Shaw (1994) make the agreement count an explicit factor (CombMNZ); Lee (1997) is the relevance-agreement result, and the paper is right not to pretend the ceiling is that. Bruch, Gai, and Ingber (2024) is the right hybrid-fusion citation. The FTS5 documentation (Hipp) is the right citation for implicit AND. I cannot name, with confidence, a paper or system note that states the \(1/k\) maximum as an overlap test, or that reports a hybrid whose lexical list was silently empty. Cooper (1998) is general web-log design, not this signal. Unsure, and not claiming them: Elasticsearch's RRF documentation states the formula; I am not confident it states the test.

## 7. Would you post it?

Yes, after one change. An IR reader can finish this version: the theorem is in Section 2, the tables answer the questions in their titles, and the abstract matches the tables. The change is to make the third paragraph of the introduction say what Section 2 says. While that paragraph stands, the paper still opens by overclaiming, which is the failure the desk rejection was pointing at, and the careful qualifications underneath read as a walk-back rather than as the result.
