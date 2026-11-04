## 1. Round-2 hunks

Every hunk checks out against the tables and JSON. Details:

- **Abstract.** "the ceiling missed none of those empty lists, as the derivation requires with two retrievers and a dense list that was never empty" — correct: every corpus is far bigger than K, so dense lists are full throughout; the condition the derivation needs is the one that held. "at the ceiling in 174 query runs where the keyword list was nonempty but shared nothing… and in two runs under the repaired builder where the lists shared one document at deep ranks" — 174 + 2 = 176 = the bucketing totals (137 + 35 + 4), and the two overlap-present ceilings are the two full-list FiQA runs. Consistent with the body.
- **Intro.** "whether the two lists overlapped at all" — accurate, and narrower than the old "something narrower, and useful". The "flat near the top" quote now matches the incident section.
- **§2.** "a nonempty list at the ceiling has maximum exactly 1/k" — right. The new "because that document's rank product is 0" clause is correct arithmetic and completes the split of the old compound "because". "The row counts say whether each list was empty, short or full; at K ≤ k, the ceiling says the lists shared no document, whatever their lengths" — right.
- **Incident.** "Two details made things worse than 'every token present' suggests" — both details (adjacency from retokenised phrases, swallowed syntax errors) are failure modes beyond the AND constraint; fine. "The fused scores had shown zero overlap on every replayed query" — at K = k = 60 this is what the ceiling means there; right. The reordered fix paragraph preserves the 161 ms / 2–4 ms / 3,500-chunk figures.
- **§4 (leg).** "Outside ArguAna" correctly scopes the 50.8–98.0% range (164/323 and 294/300). The bm25-or-raw comparisons check: raw is worse by 0.001–0.011 on five collections (0.153−0.152 up to 0.484−0.473, differences of printed values), FiQA the exception at 0.009 nDCG and 0.013 R@100, 103.6/18.6 = 5.6×.
- **§5.2.** "With two retrievers it must, whenever the other list is nonempty" — the right qualification. "294 of SciFact's 300" matches keyword_facts. "Two such runs in 22,362" — right.
- **Length paragraph.** "highest on SciDocs, FiQA and TREC-COVID, the three largest collections" — 12.8, 41.1, 88.9% are indeed the three highest 1–3-document ceiling rates and the three largest corpora of the five; 124 of 378 pooled is exact. "This is an ordering, not a size effect" with the SciFact 0-of-18 caveat is properly hedged. "four or more documents on 39 runs, all on FiQA, TREC-COVID and SciDocs" — 25+7+3+4 = 39, NFCorpus and SciFact contribute zero; exact.
- **§5.5.** The `\sloppy` group now wraps the whole passage through "not significant on 50 queries" — the mid-paragraph split is gone. The folded TREC-COVID sentence checks: 0.027–0.039 below (−0.035, −0.039, −0.027), bge's p_holm = 0.043, 13 nonempty lists. "86 of those 159" matches and_rows_4_plus over 323−164. "(Table~\ref{tab:shared})" resolves to the appendix table where that number now lives.
- **Appendix.** CPU claim now correctly restricted to the four SciFact/NFCorpus bge/nomic pairs.

No introduced errors found.

## 2. Title

"The 1/k Ceiling in Reciprocal Rank Fusion: A Zero-Overlap Test for Hybrid Retrieval" promises exactly the arithmetic fact and the diagnostic use the paper delivers, and no more; the K ≤ k scoping stays where round 2 put it, in the abstract's third sentence.

## 3. Page one

None.

## 4. Post it

Yes — post it. Every round-2 rewrite is right against the result files, the new sentences agree with their neighbours, and nothing on page one overclaims. Ship v2 and the Zenodo version.

On a different approach: leading with the measurement instead of the incident — derivation first, then 22,362 runs framed as "a free signal already in every RRF system" — would have gained a more reusable results framing and lost the thing that makes the paper memorable, which is the forensic trail of a bug the scores had been announcing for eleven days. Going the other way, a two-page system note (derivation + incident + logging advice, no BEIR) would have been faster and would have cost the evidence that the failure mode is not one private corpus's accident and — more unexpectedly — that repairing the retriever does not reliably pay off. The version you have carries both benefits; a later version built around the measurements would only be worth it if you had a second, independent production sighting to pair it with.
