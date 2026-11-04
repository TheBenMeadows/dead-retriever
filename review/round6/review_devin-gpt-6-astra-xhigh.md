1. **The opening and closing claims still contradict the stated diagnostic.** The abstract says, “This paper shows that the fused scores reveal the problem.” The Introduction says, “The fused scores can make that distinction,” referring to legitimate absence versus a broken retriever. Neither follows from the theorem. Replace these with: “At \(K\le k\), the maximum fused score identifies zero overlap. Per-retriever counts identify empty inputs; their cause requires investigation.”

   The Conclusion repeats the problem: “Whether a retriever is alive and whether fusing it helps are separate questions, and only the first can be answered from the scores.” Replace with: “Scores identify overlap under the stated depth condition. Counts identify empty inputs; relevance judgements establish effectiveness.”

   Also narrow “blind by construction to a retriever that returns a document the other retriever also returns” to ArguAna’s self-match. As written, it contradicts the two FiQA cases where overlap and the ceiling coexist. The contribution list otherwise matches the body’s scope.

2. **Correct the implementation rationale and make the measurement stage explicit.** Related work says, “A direct overlap count needs both id lists kept past fusion.” It does not: fusion can accumulate the count while merging identifiers. Rewrite: “Overlap can be counted during fusion. The maximum fused score can also be inspected afterward when only scores were logged.” The latter is the actual distinction.

   Reconcile Section 2’s “before any later filtering” with Section 4.3’s “fewer after per-file deduplication.” Specify whether the reported maximum precedes deduplication. A maximum measured afterward cannot establish that the original inputs were disjoint.

   In “What to log,” delete “on more than a few queries”: the paper establishes a per-query implication, not an alert threshold. In the abstract, add “with ranks starting at zero” when introducing \(1/(k+r)\).

3. **The remaining rereading burden is concentrated in Results.** Section 6.2 contains this sentence:

   > “The short-list rate differs by collection: 0 of 18 on SciFact (5.2k documents), 13 of 330 on NFCorpus (3.6k), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k; six distinct queries, each run under three encoders).”

   Each collection carries a numerator, denominator and corpus size; the final parenthesis adds the replication explanation. Rewrite: “Among keyword lists containing one to three documents, the at-ceiling rate was highest on the three largest collections.” Put the counts and corpus sizes in a table beside Figure 1, retaining the existing qualification about confounding.

   Section 6.5’s paragraph beginning “The buggy hybrid’s 12 wins over the repaired one are mostly abstention, not retrieval” becomes another numerical inventory. Replace most of it with: “On queries with empty keyword lists, hybrid-and equals dense. Across collection–encoder pairs, hybrid-and exceeded the repaired hybrid in 12 cases, but exceeded dense in only four.” The tables carry the collection-specific differences.

   “How often a nonempty keyword list shares nothing with the dense top \(K\) depends mostly on how short it is” also overstates the descriptive comparison. Rewrite: “The at-ceiling rate was higher among shorter keyword lists.”

   The machine-written impression comes from repeated editorial reassurance: “That is close to arithmetic”; “Two in 22,362 is rare, but it is not zero”; “The fix has two parts, and the second is not cosmetic.” Delete all three. Their surrounding evidence already makes the point.

4. **Keep the property first, and cut material that competes with it.** Section 4 supplies the mechanism and explains why the failure escaped spot checks. It does not need expansion. Reduce it by roughly a third: retain the query-builder example, implicit AND semantics, discovery through counts, Table 1 and the fix. Compress the dated recency chronology and sibling-engine history.

   To target sixteen pages, cut Appendix A entirely, including its introductory and limitations references. Its two experiments do not test this diagnostic. Remove prose inventories already represented in tables, and print the encoder-independent BM25 rows once in the appendix. Shorten “Use of AI tools” by removing the reviewer-model roster while retaining authorship responsibility and disclosure.

   Keep “What to log” before “Limitations,” as a short operational section. Folding it into the Conclusion would encourage another repetition of the theorem and results.

5. **Two numerical statements violate the declared printed-value rule.** In Section 6.1, the raw-OR nDCG disadvantage is stated as “0.001 to 0.010.” ArguAna’s printed values give \(0.484-0.473=0.011\), so the upper endpoint should be **0.011**. FiQA’s raw-OR Recall@100 advantage is stated as **0.012**, but \(0.521-0.508=0.013\). These are prose inconsistencies, not challenges to the result files. The headline nDCG win/loss counts and significance counts agree with the supplied tables and tests.

6. **The references establish context, but do not establish priority for this diagnostic.** Cormack, Clarke and Büttcher (2009), already cited, supply the RRF formula; I do not recall an explicit statement there of the depth-conditioned zero-overlap equivalence. Cooper (1998), also cited, addresses retrieval-system instrumentation, but is not evidence of this diagnostic operating in a lexical–dense production system.

   A relevant omission is Microsoft’s Azure AI Search documentation, “Relevance scoring in hybrid search using Reciprocal Rank Fusion (RRF)” (corporate author Microsoft; publication year unsure). It describes approximately \(1/k\) contribution bounds and debugging individual subscores. Discuss that proximity without attributing the paper’s equivalence or a production-monitoring deployment to it.

   I cannot confidently name an earlier published report of a matching silently inert hybrid retriever, or documented production monitoring using this exact threshold. That uncertainty cannot establish novelty.

7. **The title’s “agree on nothing” is conversational and can suggest semantic disagreement.** The finding concerns shared document identifiers, with a depth condition. Two alternatives:

   Plain: **Monitoring Hybrid Retrieval with Reciprocal Rank Fusion Scores**

   Naming the finding: **A Score Ceiling for Detecting Zero Overlap in Reciprocal Rank Fusion**

I would post it after these corrections, without further experiments. An IR reader can follow the derivation and incident, but twenty pages still asks them to reread the same distinctions through several numerical inventories. The single change most likely to improve completion is to remove those inventories and repeated interpretations from Results: state each finding once, leave its counts in the corresponding table, and preserve the qualifications where they change the interpretation.
