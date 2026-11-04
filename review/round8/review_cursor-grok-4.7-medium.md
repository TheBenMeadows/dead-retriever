The round-2 edits hold against the tables and the JSON. One new sentence is wrong.

The abstract’s 174 runs are the nonempty ceilings with no shared document, across both builders, and the two deep-rank shares are the repaired-builder FiQA runs. “Mostly short lists on the larger corpora” matches the length buckets: 137 of 174 have one to three documents, and 161 of 174 sit on SciDocs, FiQA, and TREC-COVID. The rank-0 clause is right: a shared document at rank 0 has rank product 0, so it scores above 1/k at any depth, and r₁r₂ ≤ (K−1)² < k² whenever K ≤ k. “294 of SciFact’s 300,” the 12.8 / 41.1 / 88.9 percent rates (18/141, 90/219, 16/18 = 124/378), the shared-count citation (hybrid-and at most 4.0, hybrid-or from 19.0 to 43.7), the NFCorpus “where” clause (86 of 159), and the four bge/nomic CPU pairs all match. Nuray and Can, Kumaran and Allan, and Bendersky and Croft are narrowed to what those papers do.

The wrong sentence is in Related work: “Unweighted RRF treats a weak keyword list and a strong dense list alike, which is one reason Bruch et al. find a tuned convex combination competitive, and one reason Wang et al. on MS MARCO and Chen et al. on BEIR find that BM25 helps dense retrievers under weighted score interpolation.” The “which” governs both reasons. It fits Bruch et al. It does not fit Wang et al. or Chen et al.: their result is not explained by unweighted RRF treating the lists alike. End the “one reason” at Bruch, then state their finding on its own.

Lower impact: “This is an ordering, not a size effect: SciFact’s 0 of 18 is consistent with NFCorpus’s rate.” The three largest collections are also the three highest one-to-three rates, and the rates rise with corpus size (12.8%, 41.1%, 88.9% against 25,657, 57,638, and 171,332 documents). SciFact’s 0/18 against NFCorpus’s 13/330 only shows the two small collections agree. “Not a demonstrated size effect” is the claim that colon supports. Limitations already treat the ordering as uncontrolled.

The title promises what the paper delivers. It names the 1/k ceiling as a fact of reciprocal rank fusion and calls it a zero-overlap test for hybrid retrieval: the equivalence at K ≤ k, used on hybrid lists.

None. In the abstract and the introduction, the overlap claim is followed in the same paragraph by the K ≤ k bound.

Yes, post it. The Wang/Chen “one reason” clause misstates those two papers and leaves the theorem, the counts, and the tables alone; correct it if you touch the file.

A later version that ran the main hybrid table at K ≤ k would have made every ceiling an overlap verdict, and would have lost the only natural instances of r₁r₂ ≥ k², the two FiQA runs at K = 100. A version that stopped once overlap and the row counts were measured, leaving the 5-of-18 nDCG result to a follow-up, would have kept the test as the whole paper, and would have lost the demonstration, in the same runs, that raising overlap and raising nDCG@10 come apart.
