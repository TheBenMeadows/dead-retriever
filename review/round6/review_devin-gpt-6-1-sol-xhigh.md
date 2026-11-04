## Findings, Ranked By Impact

1. **The opening and conclusion still claim that scores diagnose retriever health.** In the Introduction, “The fused scores can make that distinction” refers to legitimate non-retrieval versus a broken retriever. They cannot distinguish those cases. The abstract’s “This paper shows that the fused scores reveal the problem” makes the same promise. The conclusion reinstates it explicitly:

   “Whether a retriever is alive and whether fusing it helps are separate questions, and only the first can be answered from the scores.”

   Replace that conclusion with: “Fused scores can reveal overlap. Per-retriever row counts distinguish empty from nonempty inputs. Neither establishes retrieval effectiveness.” In the Introduction, write: “The fused scores can reveal an absence of overlap, but cannot explain why it occurred.” These changes enforce the distinction already established in Section 2; they do not change the thesis.

2. **Related work gives the ceiling an implementation advantage that it does not necessarily have.**

   “A direct overlap count needs both id lists kept past fusion.”

   It does not. During fusion, count a document when it receives its second contribution. Neither input list needs to survive afterward. Row counts can likewise be obtained from the input lists without adding counters to individual retriever wrappers.

   Replace the paragraph’s cost argument with: “Row counts and overlap counts can be recorded during fusion. The score ceiling remains usable retrospectively when only raw fused scores have been retained.” That is the defensible distinction: retained information, not an inherent storage requirement.

3. **State the rank convention before the first formula.**

   “RRF gives a document \(1/(k+r)\) from each retriever that ranks it at position \(r\).”

   An IR reader can reasonably read “position” as one-based. The abstract never corrects that interpretation, although its exact \(1/k\) maximum depends on zero-based ranks.

   Rewrite: “Using ranks starting at zero, RRF contributes \(1/(k+r)\) for each retriever that returns the document.” Make the same change at the Introduction’s first formula.

4. **Two numerical differences violate the stated printed-value rule.** These are wording corrections, not objections to the results:

   - Section 6.1: raw OR is worse by “0.001 to 0.010.” ArguAna’s printed values give \(0.484-0.473=0.011\), so the upper endpoint should be **0.011**.
   - The same paragraph gives FiQA’s Recall@100 advantage as **0.012**. Its printed values give \(0.521-0.508=0.013\).

   The abstract’s and conclusion’s 5/13 effectiveness split and 2/5 significant counts agree with the supplied tables and JSON.

5. **The remaining readability problem is numerical recitation and repeated self-defense.** Specific examples:

   Section 6.2:
   > “The short-list rate differs by collection: 0 of 18 on SciFact (5.2k documents), 13 of 330 on NFCorpus (3.6k), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k; six distinct queries, each run under three encoders).”

   This combines numerators, denominators, corpus sizes and replication qualifications in one sentence. Rewrite: “Among keyword lists of one to three documents, ceiling rates were highest on the three largest collections. This comparison does not isolate a corpus-size effect.” Put the counts in a table or the figure.

   Section 6.4’s sentence beginning “Pooling the two encoders’ cells” makes the reader reconstruct the sweep from ranges, caps, depths and cell counts. Replace the numerical recital with: “Increasing the keyword cap reduced the ceiling rate. Increasing dense depth never raised it. No ceiling hid overlap in this sweep.” Keep the arithmetic condition and the FiQA counterexample separately.

   Section 4.4:
   > “They can be checked by nobody but the operator, which is why the public reproduction in the next two sections exists.”

   Rewrite: “The production measurements are available only as aggregates; the following experiments use public collections.” The original sounds defensive because the same qualification appears again in Limitations.

   Delete “That is close to arithmetic.” It adds a rhetorical assertion between a descriptive ordering and its qualifications.

## Structure

Keep the property-first order. The title no longer depends on the incident, and Table 1 can serve as an example rather than the paper’s foundation. Section 4 is too long for that role: halve it, retaining the builder, FTS5 semantics, production table and one paragraph distinguishing absolute score scale from relative flatness.

For a shorter paper:

- Cut Appendix A entirely. Its two unrelated negative results expand precisely the personal-experience narrative the rewrite is trying to subordinate.
- Cut the count recital opening Section 6.1 and most of the long “12 wins” paragraph in Section 6.5. Retain the abstention explanation and the four comparisons that also beat dense.
- Print the encoder-independent BM25 rows once, rather than three times.
- Reduce the AI disclosure to tools’ roles and author responsibility; remove the model roster and review-history defense.
- Shorten the abstract by removing the detailed ArguAna construction and the 174/two breakdown.

Keep “What to log” before Limitations as a short checklist, not inside the conclusion. Delete “on more than a few queries”: the deduction is per query, and no alarm-frequency threshold was evaluated. The contribution list otherwise corresponds to the body.

## Title

The current title invites an unconditional reading of “shows when,” although the main experimental setting includes two ceilings with overlap. “Agree on nothing” also obscures that agreement means document identity within truncated lists.

- Plain: “Monitoring Retriever Overlap with Reciprocal Rank Fusion Scores”
- Naming the finding: “The Singleton Score Ceiling in Reciprocal Rank Fusion”

## Prior Art

I cannot confidently name a prior explicit report of this zero-overlap diagnostic, production hybrid monitoring through these signals, or this particular silent-retriever failure. That is not evidence of priority.

Cormack, Clarke and Büttcher (2009), already cited, supply the formula from which the singleton bound follows immediately; I would not attribute the explicit monitoring application to them without checking. Fox and Shaw (1994) and Lee (1997), also cited, establish agreement as a fusion concern, not this diagnostic. Michael D. Cooper (1998) supports the general monitoring motivation, not specifically fused-score or per-retriever-count monitoring of hybrid retrieval. None establishes a “first” claim for this paper.

## Would I Post It?

After correcting the summary-level health claims, yes. An IR reader is more likely to abandon this version during the repeated numerical narration than during the derivation. The single revision most likely to keep that reader is deletion: stop translating tables back into dense paragraphs, especially in Sections 6.2, 6.4 and 6.5. Preserve the distinctions and counterexamples; remove repeated inventories of the evidence supporting them.
