## 1. Readability

The main readability problem is no longer sentence length in isolation; it is that several sentences make the reader track a result, its exception, and a methodological caveat at once.

- Section 3, paragraph 2: “Counting only the tokens the fixed builder would keep orders all five (\texttt{results/keyword\_facts.json}): 8.7 content tokens per query on SciFact, 7.3 on SciDocs, 6.2 on FiQA, 5.7 on TREC-COVID and 2.5 on NFCorpus, against empty rates of 98.0, 94.2, 81.8, 74.0 and 50.8\%.”  
  Rewrite: “Across these five collections, the mean number of retained content tokens ranks the empty-list rates in the same order. SciFact averages 8.7 retained tokens and has a 98.0\% empty rate; NFCorpus averages 2.5 and has a 50.8\% empty rate. The other three collections fall between them.”  
  The next sentence already supplies the caution about confounds.

- Section 5, paragraph 6: “The buggy hybrid's 12 wins over the repaired one are mostly abstention, not retrieval.” The paragraph then continues through several nested comparisons and exceptions in one sentence: “In 8 of the 12 the buggy hybrid is not above \textsc{dense} at all: on seven of them its keyword list was empty on 74 to 94\% of queries, and on ArguAna with bge it returned the self-match on every query and a second document on four, with both aggregate metrics identical to every decimal with and without it.”  
  Rewrite as separate claims: “In eight of the twelve comparisons, the buggy hybrid does not beat \textsc{dense}. In seven, its keyword list is empty on 74–94\% of queries. The eighth is ArguAna with bge: the list returns the self-match on every query and a second document on four, while both aggregate metrics are unchanged.”  
  The paragraph’s last sentence adds another three-condition exception; split it too.

- Section 8, the first paragraph is overloaded: “If the maximum sits at $1/k$ ... then ...; and at greater depth ...” It combines a diagnostic, a depth-dependent rank condition, and a recommendation. Give the $K\le k$ rule and the $K>k$ rule separate sentences. More importantly, “Read the row counts to learn whether one retriever is empty, nearly empty, or retrieving from a different part of the corpus” overstates what counts establish: counts show activity and list size, not where the documents come from.

- Section 9 is one long limitations paragraph with several stacked qualifications. Split it into private-production evidence, benchmark scope/statistical dependence, and limits of the ceiling. It reads machine-written less through hedging than through serial caveats and exhaustive accounting. The contribution list also repeats the abstract and the conclusion; shorten it.

The definitions are mostly placed sensibly. “FTS5” and “BEIR” are not expanded, but are familiar enough for this audience; the paper should still make clear that the claim is about returned top-$K$ lists, not unrestricted retriever agreement.

## 2. Correctness after the rewrite

One conclusion sentence is false against the paper’s own argument: “Whether a retriever is alive and whether fusing it helps are separate questions, and only the first can be answered from the scores.” Scores alone cannot establish that a retriever is alive: a ceiling is compatible with an empty list or a nonempty disjoint list, and ArguAna shows that a nonempty, useless list can overlap. Rewrite: “Scores can flag zero overlap. Row counts, and at greater depth direct overlap counts, help diagnose retriever activity. Relevance judgments are needed to assess whether fusion helps.”

There is also an edge condition missing in a few summaries. Section 6 says “Always, with two retrievers,” and the introduction’s contribution list says “with two retrievers an empty list can never be missed.” That requires the other list to return at least one document; if both lists are empty, there is no fused maximum to test. State this condition wherever the guarantee is summarized.

The sentence in Section 4, paragraph 1 that row counts “say whether that is because a list is empty, nearly empty, or nonempty and disjoint” is not generally true. Counts alone do not identify disjointness, especially at $K>k$. Replace it with: “Counts distinguish empty and short lists from larger ones; at $K>k$, count shared documents directly.”

Otherwise, the abstract and results appear aligned on the supplied tables and JSON. The 174 zero-overlap cases and two hidden-overlap cases are correctly distinguished in the body; the abstract should say explicitly that the two overlap cases occurred under the fixed builder, since its current phrasing can suggest all 176 were buggy-builder cases. “The fixed builder raised overlap in every collection--encoder pair” and the nDCG counts match the body. The history claim remains appropriately framed as inference.

I found no term defined twice differently. “Singleton” is defined before its technical use. I do not see a substantive contradiction between the introduction, logging section, and limitations once the false conclusion sentence and empty-fused-list edge case are corrected.

## 3. Structure

Leading with the property works for an IR reader, but the paper still gives the incident substantial weight: it occupies a full main section, appears in the abstract, and is reinforced by a production table. That is defensible because it motivates the diagnostic; it does not read as an afterthought. The risk is that the contribution can look like a production anecdote plus a straightforward algebraic observation. Keep the incident, but make the paper’s scope explicit: a score-based zero-overlap diagnostic, with a production motivation and benchmark characterization.

Section 4 is about the right length. Keep “What to log” before Limitations; it is the practical consequence of the results, not a conclusion addendum. Cut the two negative production experiments in Appendix A entirely: they do not support the paper’s central claim. For page reduction, the largest clean cut is the repeated appendix tables: the BM25-only rows are duplicated across all three encoder tables. Consolidate those rows, and compress the run-details prose into a reproducibility summary. Remove the catalog of AI products and reviewers; it distracts from the paper and does not improve reproducibility.

## 4. Title

The current title overstates the diagnostic. It does not show that two retrievers “agree on nothing” in general; at $K\le k$ it shows zero overlap in the returned lists. At $K>k$, overlap can remain hidden.

- Plain: **Detecting Zero Overlap in Reciprocal Rank Fusion from the Maximum Score**
- Names the finding: **The $1/k$ Ceiling in Reciprocal Rank Fusion Detects Zero Top-$K$ List Overlap**

## 5. Prior art

The supplied `main.tex` cites the RRF formula but does not include the bibliography file, so I cannot verify the full references or establish a comprehensive priority claim. Web access is unavailable for this review.

The clearly relevant cited work is Cormack, Clarke, and Buettcher (2009), which introduces RRF; its formula entails the $1/k$ bound for a singleton and the paper should describe the ceiling as a deduction from that formula, not imply the formula itself is new. Webber, Moffat, and Zobel (2010) give rank-biased overlap, a related list-agreement measure, not this fused-score monitor. The manuscript’s other citations on fusion, hybrid retrieval, query-performance prediction, and retrieval monitoring are context, but the text does not show that they used this particular ceiling or per-retriever production counts.

I cannot confidently name a paper or system that previously reported either this exact ceiling as a production monitor or a silently inert retriever in a hybrid system. That is not evidence that none exists. The related-work section needs a targeted literature and systems-documentation check before submission; do not claim novelty for production monitoring without it.

## 6. Would you post it?

I would not post this version unchanged, but an IR reader can now follow the central argument. The main theorem is clear, the qualifications are mostly bounded, and the experiments are organized around diagnostic questions. The conclusion currently reverses the paper’s central limitation by saying the scores answer whether a retriever is alive. Correct that claim first. The next highest-value change is trimming repeated qualifications and result summaries, especially in the long results and limitations paragraphs.
