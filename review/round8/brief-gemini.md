# Review: dead-retriever paper, arXiv v2 — round 3 of 3 on the rewrite (confirmation)

You are reviewing the same short information-retrieval paper as in the last two rounds, after the author applied round 2's findings. This is the confirmation round: the unit under review is the diff since round 2 (attached, `diff-since-round7.patch`), read in the context of the full current `main.tex` (attached). The paper goes to arXiv (cs.IR) after this round, and the same file becomes a new Zenodo version. The title is now "The $1/k$ Ceiling in Reciprocal Rank Fusion: A Zero-Overlap Test for Hybrid Retrieval" (the author's choice after round 2 argued the title must name RRF).

Answer as a careful reader who knows rank fusion and hybrid retrieval. Formulas, section names and quoted sentences over adjectives. No compliments. Do not restate the paper. Do not re-raise anything in the settled list. Rank findings by expected impact. Under 700 words.

## Settled (rounds 1 to 7; do not re-raise)

- Experimental design, the 18 collection--encoder runs, result files, the paired sign-flip randomization test with Holm's correction within six families, the rounding rule (differences quoted in the text are differences of printed three-decimal values). Every number in the text is checked by `review/orrery-audit.py` (469 checks, all passing).
- The thesis (the 1/k ceiling proves zero overlap, not an empty retriever), the K > k failure mode (r1 r2 >= k^2), the ArguAna self-match blind spot, the history claim as an inference, "almost never relevant", FiQA's id rule as observed, Holm over all 108 in Limitations.
- Applied in round 2 (round 7 of the record): Wang et al. 2021 cited for MS MARCO, Chen et al. 2022 for BEIR; the §2 "two full lists" sentence replaced by "The row counts say whether each list was empty, short or full; at K <= k, the ceiling says the lists shared no document, whatever their lengths"; "a nonempty list at the ceiling has maximum exactly 1/k"; the abstract and conclusion state the guarantee "with two retrievers and a dense list that was never empty"; the conclusion's last sentence restricted to K <= k with the direct count at greater depth; the abstract's 174 + 2 runs sentence covers both builders and says the fused list was at the ceiling; the Results opener points at Tables 5 and 6 and the appendix correctly; the CPU-reproduction claim restricted to the four bge/nomic pairs; Nuray & Can and Kumaran/Bendersky sentences narrowed to what those papers say; two orphaned bib entries removed; the TREC-COVID sentence folded into the "12 wins" paragraph; the ArguAna paragraph no longer split by a `\sloppy` group; "flat near the top" quoted one way; the §2 "because" clause split into its two claims; several local antecedents and stops.
- Rejected with reasons in the record: cutting the sweep; folding "What to log" into the conclusion; a K <= k clause in the title (the abstract's third sentence carries it); the Table 3 header.

## Questions

1. **Did round 2's fixes hold, and did any introduce an error?** Read every hunk of the diff. For each, say whether the new sentence is right against the tables and the JSON below, and whether it still agrees with the sentences around it. Quote anything wrong.
2. **The title.** "The $1/k$ Ceiling in Reciprocal Rank Fusion: A Zero-Overlap Test for Hybrid Retrieval": does it promise exactly what the paper delivers? One sentence.
3. **Anything a reader would reject on page one.** Abstract and introduction only: a sentence that is false, that claims more than the body, or that stops a reader. Quote and rewrite, or say "none".
4. **Post it?** One paragraph. If yes, say so plainly. If no, name the one sentence that blocks it. Then, as this is the last round: in two or three sentences, what would a different approach to this paper have changed (what it would have gained, what it would have cost), so the author can decide whether a later version is worth it.




Read these files by absolute path before answering. Do not edit any files. Answer in your final message.

- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/review/round8/diff-since-round7.patch
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/main.tex
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/paper/refs.bib
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/significance.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/keyword_facts.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/natural_lengths.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_arguana__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_arguana__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_arguana__nomic-ai_nomic-embed-text-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_fiqa_test__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_fiqa_test__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_nfcorpus_test__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scidocs__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scidocs__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scidocs__nomic-ai_nomic-embed-text-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scifact_test__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scifact_test__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_trec-covid__BAAI_bge-base-en-v1.5.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_trec-covid__intfloat_e5-base-v2.json
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/results/beir_trec-covid__nomic-ai_nomic-embed-text-v1.5.json
