Every hunk was checked against the tables, the JSON and the neighbouring sentences.

**1. Did the fixes hold?** Yes, with three exceptions.

Agreement checks that pass: the ArguAna exclusion in §5.1 is required, since its 0.0\% would otherwise sit below the stated 50.8–98.0 range; the five rates run 50.8, 74.0, 81.8, 94.2, 98.0 against content tokens 2.5, 5.7, 6.2, 7.3, 8.7; 294 of 300 (and_empty) is right; 137/726 = 132+5 over 612+114; SciDocs, FiQA, TREC-COVID are both the top three (12.8, 41.1, 88.9) and the three largest collections, and all 39 short-list runs with four or more documents fall on them; Table~\ref{tab:shared}'s extremes are 4.0 and 19.0–43.7 and rise in every pair; NFCorpus's 159 nonempty / 86 with four or more matches and_empty; TREC-COVID's 13 nonempty matches the p = 0.043 (0.04290); 174+2=176=164+12, both shared-document runs under the repaired builder; the Appendix's four bge/nomic CPU pairs are right; Wang on MS MARCO and Chen on BEIR is the correct venue split; the significance counts are 2 gains (ArguAna e5, nomic) and 5 losses (FiQA ×3, SciDocs bge, ArguAna bge).

Problems, ranked:

(a) §5.5. "which is one reason \citet{bruch2023fusion} find a tuned convex combination competitive, and one reason \citet{wang2021interpolation} on MS MARCO and \citet{chen2022hybrid} on BEIR find that BM25 helps dense retrievers under weighted score interpolation." Neither paper studies unweighted RRF, so RRF's blindness cannot be a reason for their interpolation findings — interpolation is precisely where BM25's weight is tunable. The venue fix is right; the causal join is not. Rewrite: "…which is one reason \citet{bruch2023fusion} find a tuned convex combination competitive; \citet{wang2021interpolation} on MS MARCO and \citet{chen2022hybrid} on BEIR find that BM25 helps dense retrievers under weighted score interpolation, which RRF does not offer."

(b) §5.2. "This is an ordering, not a size effect." Six or eighteen queries per cell cannot exclude a size effect, and this contradicts the Limitations' "observations over five or six points, not controlled effects." Restore the hedge: "not a demonstrated size effect."

(c) §3.2. "Sections~\ref{sec:setup} and~\ref{sec:results} repeat the measurement on public collections." Section 4 is setup; only §5 measures. Drop the first reference.

**2. The title.** Yes — "The $1/k$ Ceiling in Reciprocal Rank Fusion: A Zero-Overlap Test for Hybrid Retrieval" promises an RRF ceiling, a zero-overlap test and hybrid retrieval, and delivers all three; the $K\le k$ condition is carried by §2 and the abstract rather than the title.

**3. Page one.** No blocking sentence. One over-claim: "fuses their ranked lists, usually with reciprocal rank fusion (RRF)." "Usually" is an uncited frequency claim, and the paper's own related work has Wang and Chen using weighted interpolation. Write "often with reciprocal rank fusion (RRF)."

**4. Post it.** Yes. The three items above are one-line edits needing no new analysis or reruns; after them the paper is sound at the level it claims.

A different approach — measure the main table at $K=k$, where the theorem is exact, and add a three-retriever arm — would turn the "no false negatives" guarantee and the untested multi-retriever qualification from derivation into experiment, making the central claim a result rather than a corollary. The cost is the realistic $K>k$ setting, the two FiQA hidden-overlap cases and much of the one-sided story, plus a rerun and rewrite of §5.2 and §5.4. Worth it only for a later version, not this one.
