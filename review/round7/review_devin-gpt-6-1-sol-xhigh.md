**Findings, Ranked**

1. Section 2 introduces an unsupported inference: “a ceiling over a full list means two full lists that share nothing.” Even at $K=k=60$, a full keyword list and a disjoint one-document dense list produce the ceiling. Fullness of one list establishes nothing about the other’s length. Rewrite: “The row counts say whether each list was empty, short or full; at $K\le k$, the ceiling says the lists shared no document.”

2. Section 7 misidentifies the relationship to Nuray and Can: “the ceiling is a degenerate case of that idea, read at the point where agreement is zero.” Their system-ranking problem concerns agreement with a fusion-derived reference; this paper tests overlap between fusion inputs. Disjoint inputs do not imply zero agreement between an input and the fused output. Rewrite: “Nuray and Can (2006) use data fusion to rank retrieval systems without relevance judgements; the ceiling instead tests whether the input lists share any document.”

3. Section 7 attaches an overly specific premise to the verbose-query citations: “That a conjunctive keyword query fails on verbose, natural-language input is an old observation”. Query reduction and key-concept selection do not establish the particular failure demonstrated here: implicit AND returning no rows. Rewrite: “Kumaran and Allan (2007) study query reduction, and Bendersky and Croft (2008) identify key concepts in verbose queries. The stopword and short-token removal here is a simpler query-reduction rule.” Keep the FTS5 conjunctive mechanism supported by its documentation and these experiments.

4. Section 5 retains a pointer that the appendix consolidation invalidated: “Every condition for every collection--encoder pair is in Appendix A”. Appendix A now contains keyword-only effectiveness and hybrid overlap; dense and hybrid effectiveness are in Tables 5 and 6. Rewrite: “Tables 5 and 6 report dense and hybrid effectiveness; Appendix A supplies keyword-only effectiveness, keyword timings and hybrid overlap.” No figures were lost, but their stated location is wrong.

5. Appendix B broadens the CPU reproduction claim: “The SciFact and NFCorpus runs were first made on CPU, and the GPU runs reproduced them to every digit the result files carry for nDCG@10 and Recall@100”. The previous wording explicitly restricted that comparison to four pairs, bge and nomic; the replacement reads as including e5. Unless that additional comparison exists, rewrite: “For the four SciFact and NFCorpus pairs originally run on CPU, using bge and nomic, the GPU runs reproduced nDCG@10 and Recall@100 to every stored digit.”

**Did The Fixes Hold?**
- Health overclaim: yes. The abstract now says, “This paper shows that the fused scores reveal when the two lists did not overlap.” The introduction adds, “It does not say that either list is empty.” The conclusion separates the questions: “The scores can say whether two retrievers agreed on anything, the row counts can say what that means, and whether fusing a retriever helps is a question for relevance judgements.” Read with the stated depth restriction, these no longer diagnose health from scores.
- Rounding: yes. “It is worse at nDCG@10 by 0.001 to 0.011 on five collections.” ArguAna’s printed values give $0.484-0.473=0.011$. “The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.013 Recall@100, at 5.6 times the cost.” The printed recall values give $0.521-0.508=0.013$.
- Runs, not lists: yes. “In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus.” The unit now accommodates repeated queries across encoders and conditions.
- Nonempty counterpart: yes. “If one of two lists is empty and the other is not, every fused document is a singleton and the list is at the ceiling.” The following guarantee explicitly repeats “as long as the other retriever returned something”; the contribution list and Limitations preserve that condition.

**Other Checks**
- All table and section labels resolve to the intended subjects. Table numbers are now 1 production, 2 collections/ceilings, 3 nonempty and short lists, 4 sweep, 5 nDCG, 6 recall, 7 BM25, 8 shared documents. The defect is the prose pointer identified above, not a dangling label.
- Row counts, zero-based ranks and content tokens are defined before their substantive use. Apart from the CPU comparison’s widened scope, the compression does not leave a numerical claim without its table or stated result-file source.
- Aslam and Montague fits metasearch modelling. Chen and Wang fit BM25/dense combination at the thematic level; their primary texts are not supplied, so I cannot independently certify the specific BEIR attribution from BibTeX alone.
- One further readability stop: “The ceiling sits upstream of that choice”. Rewrite: “The ceiling applies to unweighted RRF scores; it does not determine which fusion function to choose.”

**Title**

The title promises the conditional RRF test Section 2 delivers; unweighted fusion, rank convention and $K\le k$ need to remain explicit in the abstract, not necessarily in the title.

**Post It?**

A cs.IR reader would finish this version; I would post after these sentence-level corrections, without another structural rewrite. The highest-value remaining change is replacing Section 2’s “two full lists” inference with separate statements about what row counts establish and what the ceiling establishes.
