# Review: dead-retriever paper, arXiv v2 — round 2 of 3 on the rewrite

You are reviewing the same short information-retrieval paper as last round, after the author applied that round's findings. Last round's verdict from eleven seats: the rewrite works, post it after fixing (a) three sentences that let the fused scores diagnose retriever health, (b) two numbers that broke the paper's stated rounding rule, (c) "174 nonempty keyword lists" where the unit is query runs, (d) the missing "other list nonempty" condition on the no-false-negative guarantee, and after cutting Appendix A, collapsing the three appendix tables, and stopping the prose from reciting tables. All of that was applied; the record is in the earlier-rounds section below. The paper's title is now "The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval" (the author's choice among last round's proposals).

Answer as a careful reader who knows rank fusion and hybrid retrieval. Formulas, section names and quoted sentences over adjectives. No compliments. Do not restate the paper. Do not re-propose anything in the settled list. Rank findings by expected impact. Under 900 words.

## Settled (from rounds 1 to 6; do not re-raise)

- Experimental design, the 18 collection--encoder runs, result files, the paired sign-flip randomization test with Holm's correction within six families, the rounding rule (differences quoted in the text are differences of printed three-decimal values). Every number in the text is checked by `review/orrery-audit.py` (469 checks, all passing).
- The thesis: the 1/k ceiling proves zero overlap, not an empty retriever. The K > k failure mode (r1 r2 >= k^2). The ArguAna self-match blind spot. The history claim as an inference ("keeps no query log"). "Almost never relevant". FiQA's id rule stated as observed. Holm over all 108 in Limitations.
- Decided last round and applied: zero-based ranks stated at the first formula; "at the ceiling" = max <= 1/k with the clause that a nonempty list makes it exactly 1/k; the two-retriever guarantee needs a nonempty counterpart; row counts say empty, short or full (not disjoint); the cost-and-placement argument (fusion already computes the maximum; it survives in a scores-only log) is in the introduction; "twice" removed (one earlier note, eleven days before); Appendix A cut, its two negative results reduced to one pointer sentence in Appendix B; the three per-encoder appendix tables replaced by a BM25-only table with query times and a shared-documents table; Table 2 gained a content-tokens column; Table 3 holds the per-collection counts of ceilings over nonempty lists and the short-list counts; the sweep prose cut to the trend; the "12 wins" paragraph halved; "What to log" kept before Limitations with the K <= k and K > k rules in separate sentences; Related work moved after "What to log"; six references added (Kumaran & Allan 2007, Bendersky & Croft 2008, Nuray & Can 2006, Aslam & Montague 2001, Chen et al. 2022, Wang et al. 2021), each verified against Crossref or the ACL Anthology; the AI-tools section cut to roles and responsibility; the title changed.
- Rejected last round, with reasons in the record: cutting the sweep (kept, shortened); folding "What to log" into the conclusion; Sculley 2015, Shokouhi & Si 2011, Beitzel 2004, Carmel & Yom-Tov 2010 as citations.

## What is under review

The diff since last round (attached, `diff-since-round6.patch`, plus `diff-refs.patch` for the bibliography) is the unit under review. The full current `main.tex` is attached so you can read any changed passage in context. The results JSON files are attached as before.

## Questions

1. **Did the fixes hold?** For each of the four correctness fixes named at the top (health overclaim, rounding rule, runs-not-lists, nonempty counterpart), find the new sentence and say whether it is now right, by quoting it. If any fix introduced a new error, say where.
2. **What did the edits break?** A rewrite moves sentences and orphans what referred to them. Check: every "Table~N" and "Section~N" reference still points at the right thing; no number in the prose lost the table or sentence that justified it; no term is now used before its definition (the definitions moved); the abstract, contribution list, "What to log" and conclusion still claim exactly what the body shows; the new Related work paragraph cites each of the six new references for something the cited work actually says.
3. **Remaining readability stops.** Quote the sentence, give the rewrite. Only sentences in or next to the diff, or ones you flagged last round that were not fixed. Do not re-flag what the settled list covers.
4. **The title against the content.** Does "The $1/k$ Ceiling: A Zero-Overlap Test for Hybrid Retrieval" promise anything the paper does not deliver, or omit a condition a reader would need before clicking? One sentence.
5. **Post it?** One paragraph: would a cs.IR reader finish this version, and what is the single remaining change with the highest value? If the answer is "post it as is", say so.




Read these files by absolute path before answering. Do not edit any files. Answer in your final message.

- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/review/round7/diff-since-round6.patch
- /Users/bemeadows/Projects/dead-retriever/.claude/worktrees/rewrite/review/round7/diff-refs.patch
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
