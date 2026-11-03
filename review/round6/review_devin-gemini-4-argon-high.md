### 1. Readability, with evidence (ranked by impact)

1. **Unreadable number-dense paragraph (Section~\ref{sec:effect}, paragraph 3).** This paragraph asks the reader to hold three pairwise comparisons (`hybrid-and` vs. `hybrid-or`, `hybrid-and` vs. `dense`, `hybrid-or` vs. `dense`) across six collections while parsing printed-versus-unrounded fourth-decimal disclaimers:
   - *Quote:* ``Over the whole of SciFact, \textsc{hybrid-and} and \textsc{dense} differ by at most 0.003 nDCG@10 and 0.000 Recall@100 as printed (0.0022 and 0.0000 before rounding), all of it from the six queries with a nonempty keyword list, and on SciDocs, with 942 empty lists, by at most 0.001 in each (0.0017 before rounding). Two collections moved more, in opposite directions, and the number of nonempty lists does not predict which: on NFCorpus (159 nonempty of 323) \textsc{hybrid-and} is above \textsc{dense} by 0.008 to 0.014 nDCG@10, and on TREC-COVID (13 nonempty of 50) it is below by 0.027 to 0.039, significant for bge after correction ($p = 0.043$) on a difference those 13 queries carry.'' (16 numbers in two sentences.)
   - *Rewrite (replacing the whole paragraph):* ``The buggy hybrid beats the repaired one at nDCG@10 in 12 of 18 pairs mainly by abstaining. Whenever the keyword list is empty, \textsc{hybrid-and} reduces to \textsc{dense}; when unweighted RRF with the repaired OR list dilutes a stronger dense ranking, doing nothing wins. In 8 of those 12 pairs \textsc{hybrid-and} never exceeds \textsc{dense} (it is identical to \textsc{dense} on ArguAna and within 0.002 on SciDocs, where 94.2\% of keyword lists are empty, and below \textsc{dense} on FiQA and TREC-COVID). \textsc{hybrid-and} beats \textsc{dense} significantly only on NFCorpus with nomic (+0.014) and e5 (+0.013), where half the keyword lists are nonempty and short exact-match queries help.''

2. **Narrating unprinted table cells in prose (Section~\ref{sec:sweep}, paragraph 2).** Thirteen numbers in one sentence, mixing `bge` numbers from Table~\ref{tab:sweep} with unprinted `nomic` numbers (`6.7\%`, `0.7\%`, `11 of the 20 cells`):
   - *Quote:* ``Pooling the two encoders' cells (Table~\ref{tab:sweep} prints bge's) at $K = 60$: a cap of one document leaves the lists disjoint on 8.7 to 15.1\% of queries, a cap of three on 2.7 to 6.7\%, a cap of ten on 0.7 to 2.3\%, and a cap of twenty or more on at most 1.7\%, under 1\% in 11 of the 20 cells at $n \ge 20$ over both depths and both encoders.''
   - *Rewrite:* ``At $K = 60$, the disjoint rate drops from 8.7--15.1\% at $n = 1$ to at most 1.7\% at $n \ge 20$ across both encoders (Table~\ref{tab:sweep}).''

3. **Inline tables in prose (Section~\ref{sec:rowcount}, paragraphs 4--5, and Section~\ref{sec:leg}, paragraph 2).**
   - *Quote (Section~\ref{sec:rowcount}):* ``Pooled over every collection except ArguAna, where the keyword list is never disjoint, and over both builders, the fused list was at the ceiling on 137 of the 726 runs in which the keyword list held one to three documents (18.9\%), on 35 of 588 with four to 49 (6.0\%), and on 4 of 6\,636 with 50 or more (0.06\%; those four are two zero-overlap runs and the two FiQA runs above).''
   - *Rewrite:* ``Excluding ArguAna, the ceiling rate falls sharply with keyword list length: 18.9\% for 1--3 documents (137/726 runs), 6.0\% for 4--49 (35/588), and 0.06\% for 50--100 (4/6\,636: two disjoint lists and the two deep-overlap FiQA runs).''
   - *Quote (Section~\ref{sec:leg}):* ``\textsc{bm25-or-raw} is 2.2 to 18 times slower (13.6 against 4.1\,ms on SciFact, 2.6 against 1.2 on NFCorpus, 905 against 52 on ArguAna, whose queries average 195 tokens) and worse at nDCG@10 by 0.001 to 0.010 on five collections.''
   - *Rewrite:* ``\textsc{bm25-or-raw} is 2.2 to 18 times slower (up to 905 vs.\ 52\,ms on ArguAna's 195-token queries) and 0.001 to 0.010 lower in nDCG@10 on five of the six collections.''

4. **Defensive review-scar sentences (machine-written tells).** Several passages exist only to pre-empt audit objections and repeat across sections:
   - *No-query-log inference* appears three times: Section~\ref{sec:found} (``That it had behaved this way on prose queries throughout is an inference from the unchanged code and the replay, since the system keeps no query log''), Section~\ref{sec:limits}, and Section~\ref{sec:conclusion}. Keep it in Section~\ref{sec:found}; cut the other two.
   - *Not-a-controlled-comparison* appears four times: Section~\ref{sec:setup} (``contrasts between them are observations, not controlled comparisons''), Section~\ref{sec:leg} (``too few to call this a law...''), Section~\ref{sec:rowcount} (``not a demonstrated size effect''), and Section~\ref{sec:limits}. Keep it in Section~\ref{sec:limits} and drop the rest.
   - *Rounding rule disclaimer* in Section~\ref{sec:setup} (``Differences quoted in the text are differences of the printed three-decimal values unless a fourth decimal is given'') and the `(0.0022 and 0.0000 before rounding)` parentheticals in Section~\ref{sec:effect}. Cut both.
   - *Batch-size floating-point apology* in Appendix~\ref{app:run} (``Batch size reaches the vectors only through padding...''). Cut.

---

### 2. Correctness after the rewrite

1. **Missing detail in Section~\ref{sec:setup} makes Section~\ref{sec:leg} look contradictory.** Section~\ref{sec:setup} says: ``The buggy builder quotes every token and joins with spaces (implicit AND). The fixed builder drops the 118 stopwords... then joins the rest with \verb|OR|.'' It never states that the OR builders *also* quote each token (`"t1" OR "t2"`). Then Section~\ref{sec:leg} says: ``25 title queries (7.7\%), on which no quoted token matches any document, since the raw OR is empty on the same 25.'' State in Section~\ref{sec:setup} that all three builders quote each token.
2. **``Ten and fifteen queries'' in Section~\ref{sec:limits}.** Section~\ref{sec:limits} opens: ``The production measurements are on ten and fifteen queries over private corpora...'' The main text only ever mentions ten queries; the 7+8=15 and 15-query runs do not appear until Appendix~\ref{app:negative}.
3. **Equality vs.\ inequality in Section~\ref{sec:ceiling}.** The display claim writes $\max_d s(d) \le 1/k$, the next sentence defines *at the ceiling* as ``maximum fused score is $1/k$'', and the next writes $\max_d s(d) \le 1/k + 10^{-12}$. Add one clause noting that any nonempty retriever contributes a rank-0 document with score $\ge 1/k$, so for any nonempty fused list $\max_d s(d) \le 1/k$ and $\max_d s(d) = 1/k$ are equivalent.
4. **Terms used before definition or left undefined.**
   - *``row counts''* is used in the Abstract and twice in Section~\ref{sec:intro} before its definition in Section~\ref{sec:ceiling}.
   - *``shared document''* is used in Sections~\ref{sec:ceiling}, \ref{sec:related}, and~\ref{sec:log} and defined only in Appendix~\ref{app:full}'s caption.
   - *``The short-list rate''* in Section~\ref{sec:rowcount} (paragraph 5) refers to the 1--3 document bucket from paragraph 4 without naming `1--3 documents`.
   - The word *``instruments''* remains in the final sentence of Section~\ref{sec:effect}.
5. **Unexplained FTS5 syntax error (Section~\ref{sec:bug}).** If tokens match `[\w$#.@-]+` and are wrapped in double quotes, none contains a double quote, so FTS5 syntax errors only occur on an empty token list (`""`). State what input caused a syntax error or cut the sentence.
6. **Forward table reference.** Section~\ref{sec:ceiling} references `Table~\ref{tab:prod}` two sections before Section~\ref{sec:incident}.
7. **Numbers.** Every number in the text and tables matches the JSON files.

---

### 3. Structure and cutting from 20 to 16 pages

Leading with the RRF bound and demoting the incident to Section~\ref{sec:incident} works: the paper now reads as an IR diagnostic note motivated by a postmortem rather than an SQLite war story. Section~\ref{sec:incident} is the right length (~1.5 pages). However, placing `Related work` (Section~\ref{sec:related}) between `The ceiling` (Section~\ref{sec:ceiling}) and `The incident` (Section~\ref{sec:incident}) breaks the transition from the theorem to the production example already cited in Section~\ref{sec:ceiling}. Move `Related work` after `What to log` (or before `Limitations`).

Sections~\ref{sec:log} (`What to log`), \ref{sec:limits} (`Limitations`), and~\ref{sec:conclusion} (`Conclusion`) repeat the same four points three times across two pages. Keep `What to log` before `Limitations`, cut its third paragraph (which repeats Section~\ref{sec:effect}), and trim `Conclusion` to one short paragraph.

**How to cut 4 pages (20 $\to$ 16):**
1. **Cut Appendix~\ref{app:negative} (~0.8 pages).** Section~\ref{sec:intro} already admits these two negative results are ``not evidence about the ceiling''. They read like a personal lab notebook and invite the exact criticism the journal editor made.
2. **Collapse Appendix~\ref{app:full}'s three full-page `[p]` tables (Tables~\ref{tab:full-bge}--\ref{tab:full-e5}, 3.0 pages) into one half-page table (~2.5 pages saved).** In Tables~\ref{tab:full-bge}--\ref{tab:full-e5}, the 18 BM25 rows are identical across all three tables, and `nDCG@10`, `R@100`, `kw empty`, and `at ceiling` for `dense`, `hybrid-and`, and `hybrid-or` already appear in Tables~\ref{tab:legs}, \ref{tab:ndcg}, and~\ref{tab:recall}. One compact table with the 3 encoder-independent BM25 conditions plus the `shared` column across the three encoders preserves every unique number in 0.5 pages.
3. **Cut the repeated disclaimers and compress Section~\ref{sec:effect} paragraph 3 and Section~\ref{sec:conclusion} (~0.7 pages saved).**

---

### 4. Title

``A Score Ceiling in Reciprocal Rank Fusion Shows When Two Retrievers Agree on Nothing'' is honest about what the bound proves, but ``Agree on Nothing'' is colloquial and the title states only the algebraic truism ($s_{\max} = 1/k \iff$ disjoint lists at $K \le k$), omitting the diagnostic application to hybrid retrieval.
- **Plain:** *Detecting Disjoint Lists and Silent Retriever Failures in Reciprocal Rank Fusion*
- **Naming the finding:** *The $1/k$ Score Ceiling in Reciprocal Rank Fusion: Diagnosing Zero Overlap and Silently Empty Retrievers*

---

### 5. Prior art

The paper already cites the core fusion and hybrid literature (`cormack2009rrf`, `fox1994combination`, `lee1997analyses`, `webber2010rbo`, `bruch2023fusion`, `kamphuis2020bm25`, `cooper1998monitoring`).
- **(a) $1/k$ bound in RRF:** The singleton maximum $1/(k+1)$ (or $1/k$) is immediate from \citet{cormack2009rrf} and is routinely noted in search-engine documentation (Elasticsearch, Vespa, Azure AI Search, Qdrant) when rescaling RRF scores against the theoretical maximum $L/(k+1)$, though I know of no prior paper analysing the $K \le k$ separation condition and $r_1 r_2 < k^2$ leak as a zero-overlap detector.
- **(b) Monitoring per-retriever counts and overlap:** \citet{fox1994combination} and \citet{lee1997analyses} use explicit per-document overlap counts in `CombMNZ`; logging per-source zero-result rates is standard search practice \citep[e.g.,][]{cooper1998monitoring}.
- **(c) Conjunctive lexical failure on verbose queries:** The failure of all-terms-required lexical matching on natural-language queries is well established in IR; consider citing **Kumaran and Allan (SIGIR 2007, ``A Case for Shorter Queries, and Helping Users Create Them'')** or **Bendersky and Croft (SIGIR 2008, ``Discovering Key Concepts in Verbose Queries'')** alongside **Turnbull and Berryman (2016, *Relevant Search*, Manning)** on the `AND` / `minimum_should_match` failure mode in production query parsers.

---

### 6. Would you post it?

Yes, after trimming. An IR reader will finish Sections~\ref{sec:intro}--\ref{sec:incident} and~\ref{sec:log} because the $K \le k$ vs.\ $r_1 r_2 < k^2$ observation is crisp, the $1/(k+r+1)$ relative-step explanation of ``flat RRF scores'' in Section~\ref{sec:found} is genuinely useful to practitioners, and the ArguAna self-match blind spot (Section~\ref{sec:arguana}) is a sharp counterexample. Where a reader will currently stall is the middle of Section~\ref{sec:results} (especially Section~\ref{sec:effect} paragraph 3) and the four pages of appendix padding. **The single change that will most improve completion rate:** cut Appendix~\ref{app:negative}, collapse Appendix~\ref{app:full}'s three `[p]` tables into one compact table of the unprinted BM25 and `shared` columns, and rewrite Section~\ref{sec:effect} paragraph 3 without the unrounded-decimal parentheticals.
