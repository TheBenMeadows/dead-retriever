## 1. Numbers that fail or can't be reproduced

- **"differ by at most 0.002 nDCG@10 … for each encoder" (§6, "What fusion did")**: e5 on SciFact is dense 0.7194289 vs hybrid-and 0.7216221, a gap of 0.0022; in the paper's own Table 2 the printed values are 0.719 and 0.722, i.e. 0.003. Fix to "at most 0.003" or recompute.
- **Sweep prose ranges (§6, "How short is too short")**: "a cap of three on 2.7 to 6.7%" — no cell at n=3 shows 6.7 (printed cells: 2.7, 1.0, 6.0, 3.4); "a cap of ten on 0.7 to 2.3%" — the printed K=60 cells at n=10 are 1.0 and 2.3, so 0.7 comes from a K=100 cell or from nomic. If the ranges pool both encoders, say so — and then "8.7 to 15.1%" at n=1 needs verifying, since the caption allows nomic to deviate up to 4.4 points, which permits a cell outside that interval. Also verify "under 1% in 11 of those 20 cells": bge contributes only 4 such cells, so nomic must supply ≥7 of its 10.
- **"2.6 to 18 times slower" (§6, "The leg")**: the smallest ratio in the files is e5 NFCorpus, 2.331/0.937 ≈ 2.5; the largest is ArguAna ≈ 17.8. Minor, but "2.5 to 18" is what the data carry.
- **"(0.1%)" for 4/6,636**: that's 0.06%. "Fewer than 0.1%" or 0.06.
- **"at most 4.0" both-leg**: NFCorpus-bge buggy is 4.006. Trivial; the appendix prints 4.0, so "about 4" or the exact figure is safer under "at most".
- **Cannot verify from the inline files** (quote them for the audit): "one document for 1,402 of the 1,406 queries and two for the other four" — keyword_facts shows all 1,406 in the 1–3 bucket but not the 1-vs-2 split; all nomic sweep cells; the production aggregates (admitted as unverifiable by design).

Everything else I recomputed checks out: empty counts (294/942/530/37/164), the content-token ordering (8.7/7.3/6.2/5.7/2.5 → 98.0/94.2/81.8/74.0/50.8), ArguAna (1,298/1,296/108/1), excess = 176 (buggy 164 = 8+18+115+23; fixed 12 = 5+3+4), the 1.3–61.5% ranges against live-leg denominators (159/58/118/13), the pooled buckets (137/726, 35/588, 4/6,636 — note 137+35+4=176, consistent), 22,362 = 3,727×6, the 8 leak-possible cells = 2,392 runs, 5/18 and 9/18, and 12/18 buggy>repaired.

## 2. Consistency problems between old and new sections

- §6 defines "bm25-or (the fix: OR over non-stopword tokens)"; §3 says the fix also drops tokens under three characters, and Table 3's column head "OR, stopwords dropped" is similarly incomplete. One definition, used everywhere.
- "Corpus size, document length and vocabulary differ along the same ordering" (§6, "The leg") reads as if size increases along the empty-rate ordering. It doesn't: ordered by empty rate the sizes are 3.6k, 171k, 58k, 26k, 5.2k — SciFact has the *highest* empty rate and the second-smallest corpus. Say "the collections also differ in corpus size, document length and vocabulary."
- The by-collection sentence under the pooled buckets lists NFCorpus, SciDocs, FiQA, TREC-COVID and omits SciFact (0/18 in the JSON) — the second-smallest corpus, and the one cell that doesn't follow the progression. With n=18 it can't hurt the claim, but a referee with the data files will find it; disclose.
- The pooled buckets mix both builders and all three encoders; the text says only "pooled over every collection except ArguAna". The 1–3 bucket is ~85% buggy-builder lists (about 612 of 726). State the pooling, and consider reporting the fired rate by builder — the two legs may not share a disjointness profile.

## 3. Interpretation width

- (a) Content-token ordering: hedged ("too few to call this a law") and verified. "Stopwords appear almost everywhere, and the content words are what run out" is asserted as mechanism on the same five points — soften to "consistent with".
- (b) Length gradient: supported. Corpus-size gradient: supported only over four points with SciFact omitted (see above); "on these collections" is doing real work and should stay.
- (c) ArguAna generalisation: correctly scoped — the fooling requires the *other* leg to also return the self-doc, which cosine self-similarity guarantees. One addition worth a sentence: on ArguAna a non-relevant document occupies a top slot of every dense list on every query, so the dense scores in Tables 2–3 are themselves depressed; the paper notes the construction but not this consequence.
- (d) "Different instruments": supported; the 5-vs-12-of-18 asymmetry is exactly the evidence.

## 4. IRRJ referee asks, ranked

1. **Paired significance tests on the effectiveness claims** — per-query files exist, so a bootstrap or Wilcoxon on dense vs h-or per pair (at least for the five gains and the FiQA losses) is cheap; without it "improves in 5 of 18" and "+0.059" are indistinguishable from noise on 50–300-query collections. **Require.**
2. **Conventional structure**: an Introduction stating the research questions and a Conclusion; "The incident" is a fine section title but the paper currently ends on the advice list. **Require** (low effort).
3. **One figure** — per-query max fused score vs 1/k, or fired rate vs leg length; the signature this paper is about is visual and the paper has zero figures. **Likely requested.**
4. **State the bucket pooling by builder** (above) — one clarifying sentence. **Require** if §6's analysis paragraph stays.
5. **Related work**: prior notes that ArguAna queries are contained in the corpus (a known BEIR quirk worth citing rather than rediscovering), and something newer than Cooper 1998 on search-system health monitoring. **Optional.**
6. **Uncertainty on the small-n rates** (TREC-COVID n=50, the 13/330-type cells): Wilson intervals in one parenthetical. **Optional.**

## 5. Abstract and title

The abstract's numbers all reproduce (50.8–98.0, the ordering, 174+2, 5/18). One imbalance: "improves nDCG@10 over the vector retriever alone in 5 of 18" states the gain count without the paper's own finding that the buggy hybrid beats the repaired one in 12 of 18 — the sentence is accurate but reads as a stronger endorsement than the body. Pair it ("…and is itself beaten by the unfused-but-buggy configuration in 12"). "The ceiling missed none of those empty legs" is the central claim and is correctly stated. Title: "Found a Dead Retriever" is loose — the incident leg returned rows on 4 of 10 queries and ArguAna's on all — but as a label for the incident it is defensible; keep only if the body keeps calling it "inert" rather than "dead".
