# Round 5 review (Fable 5.1, fresh subagent, read only the inline brief)

Verdict: stars, counts and the Holm arithmetic all check out against the inline JSON; the paper is not yet submittable because of one citation that will print as "[?]", one sentence that contradicts the protocol, and a rounding convention under which several stated differences do not match the result files.

Required: (1) missing `smucker2007comparison` entry; (2) Appendix B contradicts Section 6 and Appendix C on timing machines; (3) SciDocs "at most 0.001" vs 0.00166 unrounded; (4) differences quoted as subtractions of three-decimal cells (ArguAna nomic 0.0331 vs 0.034, bge 0.0343 vs 0.035, SciFact nomic 0.0043 vs 0.005, FiQA 0.037-0.059, NFCorpus h-and 0.0075-0.0133); (5) "by 0.001, nomic" is 0.00016.

Significance: all 36 star positions agree with p_holm < 0.05; Holm arithmetic spot-checked in two families; counts in 7.5 reproduce. Test choice appropriate; +1 rule applied. Holm over all 108 rows (own computation): ranks 1 to 23 survive; all seven nDCG@10 h-or stars survive; lost: NFCorpus nomic and e5 h-and nDCG@10, TREC-COVID bge h-and nDCG@10, TREC-COVID nomic h-or Recall, FiQA bge h-or Recall. TREC-COVID bge h-and star rests on 13 queries at p_holm = 0.043.

Mechanism paragraph: follows from the tables; "The losses are largest on FiQA" false as a set (TREC-COVID nomic 0.0545 > FiQA e5 0.0371 and nomic 0.0468); NFCorpus "short exact-match lists" wrong (and_rows_4_plus = 86 of 159).

7.4: every count reproduces (137/726, 35/588, 4/6636; 0/18, 13/330, 18/141, 90/219, 16/18; 612 = 204 x 3; 176 = 164 + 12). Optional: the length trend holds inside each firing collection; SciFact's 0/18 is uninformative (P ~ 0.49 at NFCorpus's rate).

Abstract/title/conclusion: counts match. Optional: state K = 100 > k = 60 for the reproduction; "missed none of those empty legs" is the two-retriever theorem, add "as the derivation requires".

Other: FiQA "none reached a fused top 10" justifies nDCG@10 only, cite the rerun; thakur2021beir cited for the evaluator default which is in the BEIR code; "11 of 20 cells" scoped to K = 60 but counts K = 100 cells. Nothing requires a new experiment.
