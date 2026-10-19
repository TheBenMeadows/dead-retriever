## Major corrections before submission

1. **“Never useful” is false for ArguAna.** `keyword_facts.json` reports `and_any_relevant_hit: 1` of 1,406; the BM25-AND scores are nonzero (`nDCG@10 = 0.000449`, `Recall@100 = 0.000711`), although they round to 0.000 and 0.001 in Appendix A. Replace “never useful” in the subsection heading and abstract with a qualified claim such as “negligible effectiveness” or “almost never retrieves a relevant document.” The self-match result does not erase the one relevant hit.

2. **Clarify the population behind the natural-length rates.** The `natural_lengths.json` bucket totals pool nonempty legs from both keyword builders across three encoders: for example, TREC-COVID’s 189 rows comprise 39 live AND legs plus 150 live OR legs. As written, “live-leg query runs” could be read as referring only to the buggy leg. State explicitly that the length buckets combine both builders and the three encoders; the quoted counts and rates themselves reproduce.

3. **The “short-list disjointness” passage needs a narrower interpretation.** The collection-specific rates reproduce, but the figures pool both builders and query populations with very different characteristics. They show an association in these collections, not that corpus size causes disjointness or that a short exact-match list is generally likely to miss the dense top 100. Keep the observation, make the conditions explicit, and avoid presenting the explanation as a general result.

4. **Effectiveness language must remain descriptive.** Tables 2–3 support the stated counts: repaired hybrid nDCG@10 is higher than dense in 5/18 pairs; Recall@100 is higher in 9/18; and buggy hybrid nDCG@10 is higher than repaired hybrid in 12/18. The named gains and losses also match the rounded tables. But these are single-run aggregates with no paired uncertainty; say “higher in the observed means” in the abstract and conclusions, not “improves” without qualification.

## Section 6 numerical audit

The legs-table empty rates, token means, and content-token ordering match `keyword_facts.json`: SciFact, SciDocs, FiQA, TREC-COVID, NFCorpus order by kept tokens (8.7, 7.3, 6.2, 5.7, 2.5) and by empty rate (98.0%, 94.2%, 81.8%, 74.0%, 50.8%). The AND-empty counts, the 25 NFCorpus OR-empty queries, and the ArguAna counts also match. The ceiling ranges in the legs table agree with the 18 summaries.

The excess-ceiling totals reproduce: 176 total, 164 buggy-builder and 12 fixed-builder; 174 have no shared document and two have one shared document. The reported percentages by live-list size also match `natural_lengths.json`. The aggregate rates pool both builders, as noted above. Named nDCG gains/losses and the 5/18, 9/18, and 12/18 comparisons are consistent with Tables 2–3.

I cannot independently verify the per-query ArguAna rank details, the two deep-overlap cases, or the truncation-sweep claims from the inline summaries; those require the omitted per-query and sweep files. The bge sweep table’s displayed rates are internally plausible, but the caption’s nomic comparisons are not checkable from the supplied material.

## Scope of interpretation

- **(a) Empty rate versus content tokens:** The five-collection ordering is accurately described as an observation, and the text acknowledges confounding; retain that limitation wherever the ordering is summarized.
- **(b) Short-list disjointness versus corpus size:** The observed rates rise across the cited collections, but size is confounded with collection and query properties. Do not state this as a causal or general corpus-size effect.
- **(c) ArguAna self-match:** The dataset establishes the failure mode for this collection. Mailboxes, notes, and ticket systems are plausible analogies, not evidence of generalization; present them as systems to test, not as a demonstrated result.
- **(d) Monitor versus effectiveness verdict:** The distinction is sound. The ceiling measures overlap, not relevance; row counts expose emptiness or suspiciously short lists, but neither instrument establishes that a leg is semantically useful. ArguAna is the counterexample that makes this caveat necessary.

## Journal fit, ranked

1. **Require:** Add paired query-level uncertainty for effectiveness comparisons, with a stated test or confidence interval and multiplicity handling; otherwise keep every effectiveness conclusion explicitly descriptive.
2. **Require:** Separate a concise methods/protocol section from results, specifying query/document preprocessing, tokenization and stopword rules, ranking cutoffs, evaluation split, and how the pooled natural-length denominators are formed.
3. **Likely required:** Deepen related work around retrieval-system monitoring and fusion diagnostics; the current section cites general fusion and QPP work but does not establish how this diagnostic differs from prior operational failure detection.
4. **Optional:** Add a figure plotting maximum fused score against direct overlap and leg row count; it would make the distinction between zero overlap, empty legs, and deep shared documents immediately auditable.

## Abstract and title

The title’s ceiling claim matches the theorem, and the production incident supports “found a dead retriever.” The abstract otherwise tracks the new evidence, but “never useful” overstates the ArguAna result, and “improves nDCG@10” should be qualified as an observed aggregate difference. “In the order of their content words per query” is supported only for the five non-ArguAna collections; preserve that scope in any shortened version.
