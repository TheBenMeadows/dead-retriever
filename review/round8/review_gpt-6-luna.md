## 1. Diff audit

**Page-one scope issue (highest impact).** The abstract says, “This paper shows that the fused scores reveal when the two lists did not overlap.” The introduction similarly says, “The fused scores show something narrower than health: whether the two lists overlapped at all.” Both are too broad without the depth condition: at \(K>k\), a shared document at deep ranks can remain at or below \(1/k\), as the abstract and Results later report. Rewrite them to state the condition explicitly: “At per-retriever depth \(K\le k\), the maximum fused score reveals whether the two lists shared a document.” The sentences that follow do supply that condition, but they do not make these opening claims accurate as written.

**Other changed text:** the substantive changes agree with the current paper and the supplied summaries; I found no introduced numerical or contextual error.

- **Title and rest of abstract:** The title now identifies RRF. The added \(K>k\) qualification for empty-list misses is consistent with the nonempty dense list; the 174 disjoint-list ceilings and two shared-document ceilings match the stated counts. The ArguAna description and effectiveness totals agree with the paper’s tables and the supplied facts.
- **Introduction and ceiling section:** The row-count sentence, exact-maximum wording, and rank-zero explanation are correct. “At \(K\le k\)” properly scopes the zero-overlap conclusion, and the adjacent \(K>k\) explanation remains consistent.
- **Incident and setup:** The FTS5 explanation, revised description of the fix, diagnostics sentence, and Results lead agree with their surrounding text. The revised Results lead points to the effectiveness tables and appendix that contain the referenced material.
- **Results:** The SciFact count is 294 of 300; the 174/2 split and the “two such runs in 22,362” phrasing are consistent. The short-list ranking (SciDocs, FiQA, TREC-COVID) matches Table 3’s counts. “Saves time on every collection” agrees with the latency table; “costs little effectiveness” is qualified by the FiQA exception and its reported values.
- **Effectiveness discussion:** The table reference for shared-document means is correct. The `\sloppy` group still encloses the intended paragraph. The revised clauses on the buggy hybrid’s wins and losses preserve the cited counts and metrics.
- **Related work, limitations, conclusion, appendix:** The narrowed attributions match the cited works as described in the bibliography. The limitations edit is harmless; the conclusion’s direct-count recommendation at \(K>k\) is consistent with the theory and the two observed cases. The CPU-reproduction statement correctly limits itself to four pairs. Removed blank lines have no effect.

## 2. Title

Yes: the abstract scopes the zero-overlap test to \(K\le k\), and the paper distinguishes the one-sided result at \(K>k\).

## 3. Abstract and introduction

The two quoted opening claims in Section 1 overstate the result. Use the rewrite given there in both places, or otherwise put \(K\le k\) directly in each claim.

## 4. Post it?

No, not until those unqualified page-one claims are scoped. The sentence that blocks posting is: “This paper shows that the fused scores reveal when the two lists did not overlap.” A different approach could have tested the diagnostic across several fusion rules and depth regimes, gaining evidence about how broadly the result transfers. It would have cost the paper’s compact focus on one exact RRF property and required a substantially larger experimental design.
