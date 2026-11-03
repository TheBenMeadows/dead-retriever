**1. Did the fixes hold?**

Health: held. Abstract: "the fused scores reveal when the two lists did not overlap." Body, intro: "It does not say that either list is empty." Section 2: "It is a statement about overlap, not about either retriever." The three sentences that read fused scores as a health verdict are gone.

Rounding: held. "It is worse at nDCG@10 by 0.001 to 0.011 on five collections" — from Table 2 the printed differences are 0.006, 0.002, 0.011, 0.001, 0.006; range correct (the old 0.010 was wrong, now 0.011). "better by 0.009 nDCG@10 and 0.013 Recall@100" on FiQA — 0.233−0.224 and 0.521−0.508, correct. "0.037 to 0.058 below" also matches printed values.

Runs-not-lists: held. Abstract: "In 174 further query runs the keyword list was nonempty but shared nothing"; body: "There were 176 such query runs, 164 under the buggy builder and 12 under the fixed one", then "In 174 of the 176 the two retrievers shared no document." Units are runs throughout, and "137 of 726 runs" matches `natural_lengths.json`.

Nonempty counterpart: held in Section 2 — "as long as the other retriever returned something, the test has no false negatives for an empty list" — and in the contribution list and Limitations. Residual, low: the abstract still says "as the derivation requires with two retrievers," naming one of the two conditions; true of these runs (dense always returns 100), but the derivation needs the nonempty counterpart too. Add four words or drop "as the derivation requires."

**2. What the edits broke**, ranked.

(i) Section 2, new sentence: "The row counts say whether the keyword list was empty, short or full, and a ceiling over a full list means two full lists that share nothing." False at $K > k$, and the paper's own two FiQA runs refute it: both lists held 100 documents, one was shared deep, the fused list was at the ceiling. This is the highest-impact break — a claim two pages later contradicted by the paper's own data. Fix: "…two full lists that share nothing, unless $K > k$, where a shared document can sit below the ceiling"; or delete the clause, since the next paragraph makes the point properly.

(ii) Section 2, new sentence: "A nonempty fused list always contains some retriever's rank-0 document, which scores at least $1/k$, so on a nonempty list the maximum is then exactly $1/k$." The premise gives max $\ge 1/k$; the equality follows only under the ceiling hypothesis. As written it asserts every nonempty fused list has maximum exactly $1/k$. Rewrite: "…scores at least $1/k$; so a nonempty list *at the ceiling* has maximum exactly $1/k$."

(iii) Citation accuracy: `wang2021interpolation` is MS MARCO passage retrieval, not BEIR. Related work ("measure what BM25 adds to dense retrievers on BEIR") and Section 5.5 ("the BEIR hybrids of \citet{chen2022hybrid} and \citet{wang2021interpolation}") both give it BEIR. Split the clause: Chen for BEIR, Wang for "interpolating BM25 into dense scores improves passage retrieval." The other five new citations check out (`nuray2006ranking`'s system-ranking use is accurately described, as is its degenerate-case comparison).

(iv) Limitations now reads "The production measurements are on ten queries over a private corpus," while Appendix B says the negative results were "rejected on seven to fifteen queries." The trim cut "and fifteen" but kept the pointer that reintroduces fifteen.

(v) References and orphans: every `Table~N`/`Section~N` resolves; the `tab:full-*` labels are gone with no dangling `\ref`; the removed "two questions" roadmap is not referred to; the deleted Hardware paragraph's timing claim survived in the appendix in the narrowed keyword-only form, and no prose now depends on dense timing. Abstract, contributions, "What to log" and conclusion claim what the body shows; 176 = 174 + 2, and the 5/13 split with 2 and 5 significant reproduces from `significance.json`.

**3. Readability stops.**

"It is one, but it was the wrong thing to look at." → "Flatness is a real property of RRF; it was the wrong thing to look at."
"The fused scores can show something narrower, and useful." → "The fused scores can show something narrower, and that is enough."
"In 8 of the 12 the buggy hybrid is not above \textsc{dense}. In seven, its keyword list was empty on 74 to 94\% of queries" → "In eight of the twelve the buggy hybrid is not above \textsc{dense} at all; in seven of those its keyword list was empty on 74 to 94\% of queries."
"and that dilution is what the ``win'' records" → "and that dilution is all the win shows."

**4. The title.** "A Zero-Overlap Test" promises exactness the body conditions on $K \le k$ and its own headline runs ($K = 100 > k = 60$) break twice, so a subtitle "…for Hybrid Retrieval at $K \le k$" (or "A One-Sided Zero-Overlap Signal") is the condition a reader needs before clicking.

**5. Post it?** Yes, after one change: the "ceiling over a full list" sentence in Section 2 (finding i), because it is the only place where the paper states something its own results contradict. Everything else on this list is a clause. A cs.IR reader will finish this version: the derivation is now stated once and honestly, the ArguAna blind spot is the most interesting part and is argued rather than asserted, and the effectiveness section no longer over-claims. Fix (i), optionally (ii) and (iii), and it is ready.
