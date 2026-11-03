# Review: dead-retriever paper, rewritten for arXiv (cs.IR) — round 1 of 3 on the rewrite

You are reviewing a short information-retrieval paper that was desk-rejected by a journal editor last week with this verdict, quoted in full: "The submission is hard to understand, as if it was AI-generated based on some personal experiences with SQLite FTS5." The experiments, numbers and statistics were not disputed; they had passed five earlier review rounds and a script that checks every number in the text against the result files. The author then withdrew the earlier, shorter version from arXiv and rewrote the paper from the top: the general property first, the incident demoted to one section, shorter sentences, terms defined once, the finest-grained counts moved into tables. The rewritten paper is what you are reading. It will go to arXiv as a new submission, so the readers are IR researchers and practitioners, not a journal's referees.

Answer as a careful reader who knows rank fusion and hybrid retrieval and who has desk-rejected papers for being unreadable. Formulas, section names and quoted sentences over adjectives. No compliments. Do not restate the paper. Rank findings by expected impact. Under 1200 words.

## Settled and NOT under review

- The experimental design, the 18 collection--encoder runs, the result files, the paired sign-flip randomization test with Holm's correction within six families, and the rounding rule (differences quoted in the text are differences of printed three-decimal values). These were decided in earlier rounds.
- The thesis as reframed in round 1: the 1/k ceiling proves zero overlap, not an empty retriever. The K > k failure mode (r1 r2 >= k^2). The ArguAna self-match blind spot. The history claim stated as an inference ("keeps no query log"). "Almost never relevant" for ArguAna's AND list. FiQA's id rule stated as observed. The Holm-over-all-108 sentence in Limitations.
- No new experiments. Every number in the text is checked by `review/orrery-audit.py` (646 checks, all passing); if you think a number is wrong, say which and why, but assume the result files are the ground truth.

## What changed in this rewrite

Article class instead of the journal style. New title. Abstract cut from 330 to about 300 words and reordered: property, then incident, then experiments. Introduction now opens with hybrid search and the fusion property, and reaches the incident in paragraph four. The ceiling section states the derivation and then three bounded qualifications under their own headings. The incident is one section with four short subsections. Results are organised as questions ("How often does the buggy builder return nothing?", "Does the ceiling catch an empty keyword list?", "Does repairing the keyword retriever improve retrieval?"). A new table (Table 3) holds the per-collection counts of ceilings over a nonempty keyword list that were previously a sentence of parenthesised ranges. Vocabulary: "keyword list", "dense list", "nonempty", "at the ceiling", "shared document", "row count", "singleton", "self-match", each defined at first use; the words "leg", "live", "fired", "excess" and "instrument" are gone. A fresh model that had never seen the work paraphrased the paper correctly section by section before this round, and the three terms it had to guess are now defined.

## Questions

1. **Readability, with evidence.** Which paragraphs would a reader of cs.IR still have to read twice? Quote the sentence that stops them and give a rewrite. Which sentences carry more than one number per clause where one would do? Which passages still read as machine-written, and what specifically (hedging stacked on hedging, a parenthetical inside a parenthetical, every claim with three qualifications, a sentence that exists only to pre-empt an objection nobody raised)? Be concrete: a list of quoted sentences and rewrites is worth more than a paragraph of advice.
2. **Correctness after the rewrite.** A rewrite moves sentences and can break what they referred to. Is any sentence now false against the tables or the JSON below? Does the abstract, the introduction's contribution list, the "What to log" section and the conclusion each claim exactly what the body shows, no more? Is any term used before it is defined, or defined twice differently? Do any two sections contradict each other?
3. **Structure.** Does leading with the property and demoting the incident work for an arXiv reader, or does the incident now read as an afterthought that the title and the production table still lean on? Is Section 4 (the incident) the right length? Should the "What to log" section come before "Limitations" or be folded into the conclusion? Say what you would cut entirely; the paper is 20 pages in article class and would be better at 16.
4. **Title.** The current title is "A Score Ceiling in Reciprocal Rank Fusion Shows When Two Retrievers Agree on Nothing". Judge it against what the paper shows, and offer two alternatives, one plain and one that names the finding.
5. **Prior art.** Who did this before? Name systems, papers or blog posts that (a) observed that RRF scores bound at 1/k when retrievers do not overlap, (b) used fused scores or per-retriever counts to monitor a hybrid retriever in production, or (c) reported a silently inert retriever in a hybrid system. Name only work you are confident exists, with authors and year; mark anything you are unsure of as unsure. If the paper already cites the right thing, say so.
6. **Would you post it?** One paragraph: is this now a paper an IR reader would finish, and what is the one change that would most improve that?




Read these files by absolute path before answering (the paper, its bibliography, the significance tests, the keyword facts, the natural row counts, and the 18 summary result files). Do not edit any files. Answer in your final message.

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
