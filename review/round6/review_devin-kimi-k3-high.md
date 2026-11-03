## Round 1 review

### Highest impact: two sentences break the paper's own rounding rule

Your stated rule (Section 5, settled): "differences quoted in the text are differences of the printed three-decimal values unless a fourth decimal is given." Two quoted differences violate it:

1. Section 6.1: "where OR over every token is better by 0.009 nDCG@10 and 0.012 Recall@100". Printed values: 0.521 − 0.508 = 0.013 (raw 0.01249 rounds to 0.012; the difference of prints is 0.013). Under your rule this must read 0.013.
2. Section 6.1: "worse at nDCG@10 by 0.001 to 0.010 on five collections". The ArguAna endpoint prints as 0.473 vs 0.484, a printed difference of 0.011 (raw 0.0103). Either the range reads 0.001–0.011 and FiQA reads 0.013, or the rounding-rule sentence needs a clause that ranges over raw differences are computed before rounding. Quietly violating a rule you stated in the setup section is exactly what a number-checking reader will find. (If `orrery-audit.py` passes these, its implementation of the rule is wrong in the same way — worth checking the checker.)

### Correctness after the rewrite (other checks)

I recomputed every aggregate I could against the JSONs. The 176 = 164 + 12 split, the 174/2 split, Table 3's ranges (NFCorpus 2–3, SciDocs 5–7, FiQA 35–43, TREC-COVID 7–8), the bucket counts (137/726, 35/588, 4/6636; SciFact 0/18 … TREC-COVID 16/18), 124 of 378, the 2,392 sweep runs, the 8-of-12 recap, the ArguAna figures (1,298/1296/108/99.7%), the 31-significant count, and the "at most 4.0 → 19.0 to 43.7" shared-documents claim all check out. Abstract, contribution list, "What to log", and conclusion each claim what the body shows. The r1 r2 < k² step is right. No terms used before definition except one: "the ceiling" appears in the intro's item 3 ("whether the ceiling catches it") before Section 2 defines it; name it in intro paragraph 3 where you already state the property.

One vocabulary regression: the changelog says "instrument" is gone, but Section 6.6 ends "are different instruments". Also Appendix A: "both verdicts stand on their own terms".

### Readability

These still stop a reader:

- Abstract: "It also appeared over 174 nonempty keyword lists that shared nothing with the dense list, mostly short lists on large corpora, and twice over lists that shared one document deep in both, the case K > k leaves open." Three counts, two appositives, trailing qualifier. → "In 174 more runs the lists were nonempty but disjoint, mostly short keyword lists on the larger corpora; in two runs at K > k the lists shared one document at deep ranks, the case the test leaves open."
- Abstract: "the repaired hybrid beats the dense retriever alone in 5 of 18 pairs (2 of them significant under a paired randomization test with Holm's correction) and loses to it in 13 (5 significant)" — parenthetical inside parenthetical accounting. → "…in 5 of 18 pairs and loses in 13; two of the gains and five of the losses are significant under a paired randomization test with Holm's correction."
- Section 6.6: "At Recall@100 it is above in 9 (one significant; the ninth, NFCorpus with bge, by 0.0006, which the table rounds to a tie) and below in 9 (three significant)." The sentence is carrying six numbers and an aside. Split: state the 9/9, then one sentence for the bge rounding tie.
- Section 6.6: "In 8 of the 12 the buggy hybrid is not above dense at all: on seven of them its keyword list was empty on 74 to 94% of queries, and on ArguAna with bge it returned the self-match on every query and a second document on four, with both aggregate metrics identical to every decimal with and without it." Four clauses, three counts. The ArguAna half repeats Section 6.3 almost verbatim; cut it to "and on ArguAna with bge, which Section 6.3 covers".
- Section 6.2: "SciFact's 0 of 18 is too few runs to place (at NFCorpus's rate, 0 of 18 would occur about half the time), so this is a pattern across four collections that differ in more than size, not a demonstrated size effect." Hedging stacked on hedging inside a parenthetical. → "SciFact's 0 of 18 is consistent with NFCorpus's rate, so this is an ordering across four collections, not a demonstrated size effect." Same claim, half the length. The passage already ends with "the pooled row-count rates mix the two builders" in Limitations; you are disclaiming the same point three times.
- Section 6.2: "Read as a zero-overlap test, the ceiling was right on every one of them; read as an empty-list alarm, it was wrong; and the row count tells the two readings apart." Balanced-antithesis cadence; the third clause restates what the first two imply. Cut the last clause.
- Incident: "That it had behaved this way on prose queries throughout is an inference from the unchanged code and the replay, since the system keeps no query log." Fine as is — keep; this is where stated inference belongs and it appears again in Limitations almost word-for-word. Keep one, cut the other.

The abstract as a whole still reads machine-compressed: it answers "what happens on SciFact, NFCorpus, … plus ArguAna" in prose instead of one table line, and every clause carries a bound or qualifier. It is within word count but not within attention budget; moving the 50.8–98.0 sentence after the ArguAna sentence would restore the property→incident→experiments order you announced.

### Structure

Leading with the property works for arXiv; the incident does not read as an afterthought, because Section 4.3 ("what the scores had already said") is the paper's best paragraph and repays the framing. Section 4 is the right length except Table 1's caption, which re-explains two things the text says once already.

To get from 20 pages toward 16:
- Fold "What to log" into a subsection of the conclusion. Its first paragraph duplicates Section 2's qualifications ("if the maximum sits at 1/k … then with K ≤ k …") and its last paragraph duplicates Section 6.6's last two sentences. Keep the actionable middle (test the builder with a conversational sentence; compute 1/(k+r+1) before calling fusion flat) — that is the part a practitioner will paste into a runbook.
- Limitations repeats body caveats verbatim (non-independent encoders, family-within correction, sweep coverage). Cut each repeated caveat to one clause.
- Appendix A's recency-decay result is incident bookkeeping; its machinery (floor 0.85, 180 days, 0.956–1.000) is more detail than a negative result on 7+8 queries earns. Two sentences each.
- The three `sloppy`-wrapped paragraphs in Section 5 are a tell of fighting the formatter, not of content problems, but the stoplist belongs in a file, not in italics in the appendix — one line pointing at the repository does it.

### Title

Current title judges fine against the paper: the ceiling is the object, and "Agree on Nothing" is accurate (overlap, not emptiness). Two alternatives:

- Plain: "Reciprocal Rank Fusion Scores Reveal When Two Retrievers Share No Documents"
- Finding: "The 1/k Ceiling: Detecting Dead and Disjoint Retrievers from Fused Scores"

Either beats the current one on scannability; the current one's double line-break in article class makes it look like a talk abstract.

### Prior art

- (a) The 1/k bound is a direct consequence of the sum in Cormack et al. 2009, but I cannot name a paper that states it as a diagnostic, and I won't invent one. The paper's framing as novel use of a known quantity is defensible as cited; you might add one sentence in Related Work acknowledging the bound is arithmetic on Cormack's formula, which you effectively already do in Section 3's first sentence.
- (b) Monitoring a hybrid via per-retriever counts: nothing I am confident exists in the literature. Operations-side write-ups (vendor hybrid-search docs from Elastic, Vespa, OpenSearch) discuss score normalization but I am unsure any discusses monitoring via fused scores — left unmarked because the paper doesn't claim novelty there beyond Cooper 1998's instrumentation argument, which is correctly cited.
- (c) Silently inert retriever: no incident report I can name with author and year. The FTS5 implicit-AND gotcha has been written about in practitioner posts (Simon Willison has written about FTS5 query construction and quoting — unsure whether the AND-semantics trap specifically); if citable, a footnote in Section 4.2 grounds the bug class. Not required.

The existing citation set (CombMNZ for explicit agreement reward, QPP for per-query health, RBO for overlap measurement, Bruch et al. for the fusion-function framing) is the right neighborhood; nothing missing that I am confident about.

### Would you post it?

Yes — a cs.IR reader would finish this version, which I would not say of the shape the desk rejection implies. The derivation is checkable in five lines, the incident section carries the narrative, and Tables 2–3 plus the appendix tables let a practitioner map the finding onto their own system. The single change that would most improve it: fix the rounding-rule violations in Section 6.1 (and audit the audit script), because a paper whose pitch is "read the numbers your system already computes" cannot have the text's numbers disagree with its tables under a rule the text itself states. After that, the 20→16-page cut above is worth more than any further prose polish.
