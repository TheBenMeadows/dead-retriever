# Review: dead-retriever paper, journal draft — round 5 (confirmation)

You are reviewing the submission candidate for the Information Retrieval Research Journal (single-blind, normal paper, about 20 pages). Round 4 (ten reviewers) found one experimental defect and fifteen text defects; all were applied. The experimental defect: the evaluator did not drop a document whose id equals the query's id (BEIR's default), so every ArguAna effectiveness figure counted the query's own document. All 18 collection--encoder pairs were rerun with that rule; the ArguAna figures changed (bge dense 0.456 to 0.641), nothing else did. Paired sign-flip randomization tests with Holm's correction were added (per-query scores now exist), the paper was restructured (introduction with contributions, related work before the experiments, a protocol section, a conclusion, the two production negative results moved to Appendix A), a figure was added, and the title was qualified. Answer as the one careful reviewer whose job is to stop the author from submitting something wrong. Formulas, section names and quoted phrases over adjectives; no compliments; do not restate the paper. Under 1000 words.

## What to do

1. **Read the whole paper once as a journal referee would** and name anything that would get it rejected or embarrass the author: a false sentence, a number that does not follow from the tables or the JSON below, a claim wider than the evidence, a citation that does not say what it is cited for, an inconsistency between sections. Sections 1 to 5 were edited lightly; Sections 6 to 10 and the abstract were rewritten.
2. **The significance test (Section 6, "Effectiveness", and Section 7.5).** `results/significance.json` is inline: 108 rows, one per (pair, metric, comparison), each with the mean paired difference, the randomization p-value and the Holm-adjusted p-value. Check that the stars in Tables 3 and 4 and every "significant" or "not significant" in the prose follow from it at alpha = 0.05 on `p_holm`. Say whether the test and correction are the right ones for this design (three encoders rerun the same queries; six families of 18).
3. **The rewritten mechanism paragraph (Section 7.5, "The buggy hybrid's 12 wins")** and the ArguAna paragraph that now says BM25 alone (0.484) is above two encoders: do they follow from the tables?
4. **Section 7.4 and Figure 1**: does the prose claim no more than the pooled and per-collection counts support, now that SciFact is included and the pooling of both builders is stated?
5. **Abstract, title and conclusion.** Do they claim exactly what the body shows, no more?
6. Anything a referee would still require before acceptance: one sentence each, required or optional. No new experiments unless one is essential.

## Attached (inline below; do not use any tool: do not read files, run commands, or fetch URLs; answer in your final message)

- `paper/main.tex` — the paper (IRRJ LaTeX style).
- `paper/refs.bib` — the bibliography (every entry was checked against Crossref, arXiv or the publisher listing; flag only if you know one to be wrong).
- `results/significance.json` — the paired tests.
- `results/keyword_facts.json`, `results/natural_lengths.json` — encoder-free keyword facts and the ceiling rate by keyword-leg length.
- `results/beir_<collection>__<encoder>.json` — the 18 summary files.


=== paper/main.tex ===

\documentclass[twoside,a4paper,11pt]{article}
\usepackage{irrj2e}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{lastpage}
\newcommand{\todo}[1]{\textcolor{red}{[#1]}}

\irrjheading{-}{2026}{1-\pageref{LastPage}}{10/26}{-}{-}
\ShortHeadings{A Score Ceiling in Reciprocal Rank Fusion Detects Zero Overlap at Depth $K \le k$}{Meadows}
\firstpageno{1}

\begin{document}

\title{A Score Ceiling in Reciprocal Rank Fusion Detects\\Zero Overlap at Depth $K \le k$:\\an Incident and Six BEIR Collections}

\author{\name Benjamin Meadows \email ben@benjaminmeadows.com \\
       \addr Independent Researcher\\
       ORCID 0009-0007-9698-0910}

\editor{-}

\maketitle

\begin{abstract}%
A hybrid search system fuses a keyword retriever and a vector retriever with reciprocal rank fusion (RRF). In the system described here, the keyword query builder was unchanged from the system's first version until 2026-08-18; replayed on ten real queries, it returned nothing for every conversational one, and the result lists had never looked empty because the vector retriever always filled them. The failure was visible in the fused scores. RRF credits a document $1/(k+r)$ from each retriever that ranks it at position $r$, so with per-retriever depth $K \le k$ a document found by two retrievers scores above $1/k$ and a document found by one scores at most $1/k$. A result list whose maximum fused score is $1/k$ therefore contains no document that both retrievers returned. That is a statement about overlap, not about either retriever: two nonempty lists can be disjoint, and in the incident four of ten queries had a one- to three-document keyword list that shared nothing with the vector list. I give the derivation and its limits, the bug (quoting every token of an SQLite FTS5 query, which FTS5 reads as an implicit AND), before-and-after aggregates from the production system, and a reproduction on six BEIR collections with three encoders, 22\,362 hybrid query runs. The buggy builder returns nothing for 50.8 to 98.0\% of queries on five collections, in the order of their content words per query, and the ceiling missed none of those empty legs. Where the two instruments disagree, the ceiling fired over a nonempty leg that shared nothing with the vector leg in 174 runs, mostly short lists on large corpora, and in two runs over lists that shared one document deep in both, the case depth $K > k$ leaves open. On the sixth collection, whose queries are themselves corpus documents, the buggy leg is never empty and almost never relevant: it returns the query's own text, the vector leg agrees, and the ceiling never fires. Repairing the leg raises overlap in every collection--encoder pair; at nDCG@10 the repaired hybrid is above the vector retriever alone in 5 of 18 pairs (2 of them significant under a paired randomization test with Holm's correction) and below it in 13 (5 significant). Code, results, per-query diagnostics and this paper's source are at \url{https://github.com/TheBenMeadows/dead-retriever}.
\end{abstract}

\begin{keywords}
  reciprocal rank fusion, hybrid retrieval, rank fusion diagnostics, SQLite FTS5, BM25, dense retrieval
\end{keywords}

\section{Introduction}
\label{sec:intro}

The system is a personal search engine over about 30\,000 to 217\,000 text chunks per corpus, split across five SQLite databases that share one retrieval module. Each query runs two retrievers over the same chunks: an SQLite FTS5 index ranked by BM25 \citep{robertson2009bm25,sqlite_fts5}, and a 768-dimensional embedding index searched by exact cosine. The two ranked lists, each cut at depth $K=60$, are fused with reciprocal rank fusion at $k=60$ \citep{cormack2009rrf}.

On 2026-08-07 a recency-decay feature was evaluated and rejected because RRF scores were ``flat near the top'': adjacent ranks differed by about 1.4\%, so even a 5\% age multiplier acted as a strong reranker rather than a tie-break. That flatness was recorded as a property of fusion. On 2026-08-18, while investigating why the keyword side rarely seemed to matter, I logged the keyword retriever's row counts for ten real queries. Five of five conversational queries matched zero chunks, as did a two-word place-name query. Only queries of two or three technical tokens matched anything. The query builder had been the same line of code since the system was built, and all four sibling engines carried it; that it had behaved this way on prose queries throughout is an inference from the unchanged code and the replay, since the system keeps no query log.

The fused scores had said so from the start. Over the fused lists of those ten queries (at most 120 documents each at $K = 60$, fewer after per-file deduplication), the maximum score was exactly $1/60 = 0.01\overline{6}$. The values were $1/60, 1/61, 1/62, \ldots$ with gaps where deduplication removed a chunk: every fused score was a single term $1/(k+r)$, so no document had been credited by both retrievers. The ``1.4\% flatness'' was misread twice. Between consecutive singleton scores it is the relative step of the formula, $\bigl(1/(k+r) - 1/(k+r+1)\bigr) / \bigl(1/(k+r)\bigr) = 1/(k+r+1)$, 1.6\% at the top of the list and 1.4\% around rank 10, and two live lists that agreed on every document would show the same relative step at twice the absolute scale. What marked the incident was not the step but the scale: nothing scored above $1/60$.

This paper makes four contributions.
\begin{enumerate}
\item A derivation (Section~\ref{sec:ceiling}): with per-retriever depth $K \le k$, the maximum RRF score over a result list is at most $1/k$ if and only if no document in the list was returned by more than one retriever; one direction survives at any depth, the other needs $K \le k$, and the failure mode at $K > k$ is characterised ($r_1 r_2 \ge k^2$).
\item The incident (Sections~\ref{sec:bug} and~\ref{sec:prod}): the query builder that produced an implicit FTS5 AND, the fix, and aggregate before-and-after measurements from the production system.
\item A reproduction on six BEIR collections and three encoders, 22\,362 hybrid query runs (Sections~\ref{sec:protocol} and~\ref{sec:results}): how often the buggy builder returns nothing, how the ceiling rate tracks the empty-leg rate, where the two disagree and why, one collection on which the test is blind by construction, and what repairing the leg did to effectiveness, with paired significance tests.
\item Operator guidance (Section~\ref{sec:discussion}) on what to log and how to read it, bounded by Section~\ref{sec:limits}.
\end{enumerate}
Section~\ref{sec:related} places the ceiling among the fusion and monitoring literature. Two negative results measured on the production system beside the dead leg are in Appendix~\ref{app:negative}; they are part of the incident's record, not evidence about the ceiling.

\section{Background and related work}
\label{sec:related}

Reciprocal rank fusion was proposed by \citet{cormack2009rrf}, who set $k=60$ by experiment; the system here used that constant unchanged, which is what made the $1/60$ ceiling recognisable on sight. The older fusion literature studied overlap between the lists being fused: CombSUM sums the scores a document receives and CombMNZ additionally multiplies by the number of systems that returned it \citep{fox1994combination}, so that CombMNZ rewards multi-system agreement explicitly; \citet{lee1997analyses} showed that fusion helps when the systems agree on relevant documents more than on non-relevant ones, and \citet{montague2001normalization} treated the score-scale problem that rank fusion sidesteps. Rank-biased overlap \citep{webber2010rbo} is the principled measure of agreement between two indefinite rankings; the both-leg count in Section~\ref{sec:results} is its crudest relative, measured where it had gone to zero. On hybrid lexical and dense retrieval, \citet{luan2021sparse} and \citet{gao2021clear} establish the complementarity the hybrid relies on, and \citet{bruch2023fusion} analyse fusion functions and show when RRF is and is not competitive with a tuned convex combination; this paper is about a failure upstream of that choice, where one of the lists is empty. Query performance prediction \citep{cronentownsend2002qpp} asks, per query, whether a retriever did well; the ceiling asks a cruder question of the fusion, whether its inputs agreed on anything, and the instrumentation it calls for is the kind \citet{cooper1998monitoring} argued retrieval systems should carry. \citet{kamphuis2020bm25} show how much BM25 scores vary across implementations of the same formula; the FTS5 variant here is one more, and its query grammar, not its scoring, is what failed.

What the ceiling adds to the two obvious instruments is cost and placement, not information. Per-retriever row counts need a counter in each retriever's wrapper, and a direct overlap count needs both id lists retained past fusion; the maximum fused score is one number the fusion already computes, available wherever the fused list is, including in a log that recorded only scores. The reproduction measures how far that one number can be trusted as a stand-in for the other two. ArguAna \citep{wachsmuth2018arguana}, one of the six collections, is built so that each query is itself a corpus document; BEIR's evaluator removes a document whose id equals the query's id before scoring for that reason \citep{thakur2021beir}, and Section~\ref{sec:results} shows what the construction does to a keyword leg that requires every query token.

\section{The ceiling, and what it does and does not say}
\label{sec:ceiling}

Let $L$ retrievers each return a ranked list cut at depth $K$ in which every document appears once, let $k$ be a positive integer, and let $r_\ell(d) \in \{0,\ldots,K-1\}$ be document $d$'s 0-based rank in retriever $\ell$'s list when present. Reciprocal rank fusion scores
\[
  s(d) \;=\; \sum_{\ell : d \in \text{list}_\ell} \frac{1}{k + r_\ell(d)} .
\]
A document present in exactly one list scores at most $1/k$ (rank 0). A document present in two lists scores at least $2/(k+K-1)$ (last place in both). The second bound exceeds the first whenever
\[
  \frac{2}{k+K-1} > \frac{1}{k} \iff K \le k ,
\]
so with $K \le k$ (here $K = k = 60$), every document found by two or more retrievers outscores every document found by one. Under that setting the following holds exactly, in both directions, for any list with at least one result:

\begin{quote}
$\max_d s(d) \le 1/k$ if and only if no document in the list was returned by more than one retriever.
\end{quote}

Three qualifications bound what that means in practice. First, it is a statement about overlap. Two retrievers that both return $K$ documents and share none of them produce the same ceiling as one retriever and one empty list, and so does a keyword leg that returns one or two documents the vector leg did not; with more retrievers, any number of pairwise-disjoint live lists do too. In the incident, the keyword leg returned rows on four of the ten queries and the ceiling held on all ten (Table~\ref{tab:prod}); those four were lists of one to three chunks, with nothing in common with the vector top 60. The ceiling says no document was reinforced by agreement; the per-retriever row counts say whether that is because a leg is empty, nearly empty, or live and disjoint, and a system that fuses should log both. Second, the equivalence needs $K \le k$. One direction survives at any depth: a maximum above $1/k$ proves that some document was returned by two retrievers, since a singleton scores at most $1/k$ for every $K$. The other does not. With $K > k$, a document ranked deep in both lists scores below $1/k$ (rank 90 in both at $k=60$ gives $2/150$), and one ranked exactly $k$ in both scores exactly $1/k$; two ranks $r_1, r_2$ combine to more than $1/k$ exactly when $r_1 r_2 < k^2$. So at $K > k$ a maximum of $1/k$ shows that every retriever's rank-0 document is exclusive and leaves deeper overlap open, and a system that keeps per-retriever ranks should count shared documents directly. Section~\ref{sec:results}, which uses $K = 100 > k$, reports both and measures how often the two disagree. Third, with two retrievers an empty leg always produces the ceiling when the other leg returned anything, so the test cannot miss one and everything it gets wrong is in the other direction; with three or more, an empty leg can hide behind two live legs that overlap. The equivalence itself holds for any $L$. The one-based RRF of \citet{cormack2009rrf} shifts every figure by one: the singleton ceiling is $1/(k+1)$, and strict separation holds for $K \le k+1$. Throughout, the scores compared are the unweighted RRF sums before any downstream filtering or rescaling, and ``at the ceiling'' means $\max_d s(d) \le 1/k + 10^{-12}$.

\section{The bug}
\label{sec:bug}

The keyword query builder was
\begin{verbatim}
fq = " ".join(f'"{t}"' for t in tokens)
\end{verbatim}
which, for the query \emph{how do I fix the empty feed}, produced
\begin{verbatim}
"how" "do" "i" "fix" "the" "empty" "feed"
\end{verbatim}
FTS5 reads a sequence of phrases separated by whitespace as an implicit AND \citep[\S 3]{sqlite_fts5}: every phrase must occur in the same row. Rows here were 1\,400-character chunks, so a conversational query of six or seven tokens almost never matched. Two further details made the constraint stricter than ``every token present''. The tokeniser kept hyphens, dots and some punctuation inside a token, and FTS5's own tokeniser splits on them, so a token such as \texttt{il-6} became a two-word phrase, an adjacency constraint. And an FTS5 syntax error was caught and ignored, so a malformed query also returned nothing without a trace. Two- or three-token technical queries did match, which is why spot checks during development passed, and the vector retriever returns $K$ documents whenever the corpus has that many, so result lists were always full.

The fix has two parts, and the second is not cosmetic. Tokens are joined with \verb|OR| and ranked by BM25; a raw OR over all tokens matched about 100\,000 chunks and cost 161\,ms per query, so stopwords and tokens shorter than three characters are dropped first, after which a typical query matches about 3\,500 chunks in 2 to 4\,ms. If a query is all stopwords, the raw tokens are used. Section~\ref{sec:results} measures both variants on public data.

\section{Measurements on the production corpus}
\label{sec:prod}

The corpus is private. This section reports counts, timings and overlaps recorded at the time, with no query or document text; the figures are in \path{results/production-aggregates.json} in the released repository and are checkable by nobody but the operator, which is the reason the public reproduction exists. Ten real queries were replayed before and after the fix on the same shard (Table~\ref{tab:prod}).

\begin{table}[h]
\centering
\small
\begin{tabular}{lrr}
\toprule
 & implicit AND & OR + stopword drop \\
\midrule
Queries on which the keyword leg returned any row & 4 / 10 & 10 / 10 \\
Queries with a document found by both legs & 0 / 10 & 10 / 10 \\
Maximum fused score over the fused list & $1/60 = 0.0167$ & 0.025 -- 0.033 \\
Keyword leg latency, conversational queries & -- & 2 -- 4\,ms \\
\bottomrule
\end{tabular}
\caption{The keyword leg before and after the fix, ten real queries, one production shard, $K = k = 60$. The fused list holds at most 120 documents at this depth. The ``before'' latency is omitted because a query that matches nothing is fast; a raw OR without the stopword drop took 161\,ms. On the four ``before'' queries where the leg returned rows, it returned one to three chunks, none shared with the vector top 60.}
\label{tab:prod}
\end{table}

The same builder was present at a different line number in four sibling engines over four other corpora, each inert on prose queries in the same way; the five have since been merged into one module.

\section{Experimental protocol}
\label{sec:protocol}

To check that the effect is a property of the query builder and not of one private corpus, six retrieval conditions were run on six BEIR collections \citep{thakur2021beir} with three encoders.

\paragraph{Collections.} SciFact \citep{wadden2020scifact} (claim sentences against scientific abstracts), NFCorpus \citep{boteva2016nfcorpus} (short nutrition titles against medical documents), ArguAna \citep{wachsmuth2018arguana} (whole arguments against counter-arguments), SciDocs \citep{cohan2020specter} (paper titles against abstracts), FiQA \citep{maia2018fiqa} (finance questions against forum posts) and TREC-COVID \citep{voorhees2020treccovid} (COVID-19 questions against CORD-19 abstracts); Table~\ref{tab:legs} gives their sizes. Data came through \texttt{ir\_datasets} \citep{macavaney2021irdatasets}; only queries with relevance judgements are run. The collections differ in domain, corpus size, document length and relevance style as well as in query length, so contrasts between them are observations, not controlled comparisons.

\paragraph{Encoders.} \texttt{nomic-embed-text-v1.5} \citep{nussbaum2024nomic}, the public release of the production encoder, \texttt{bge-base-en-v1.5} \citep{xiao2023cpack} and \texttt{e5-base-v2} \citep{wang2022e5}, all 768-dimensional, each with the query and document prefixes its model card prescribes (Appendix~\ref{app:run}). Documents are embedded as title and text joined by a space; vectors are normalised and searched by exact cosine.

\paragraph{Keyword leg.} The builder's tokeniser is the regular expression \verb|[\w$#.@-]+| over the lower-cased query. The buggy builder quotes every token and joins with spaces (implicit AND). The fixed builder drops the 118 stopwords listed in Appendix~\ref{app:run} and every token under three characters, then joins the rest with \verb|OR|, falling back to the raw tokens when nothing survives; a third condition joins every raw token with \verb|OR|. The FTS5 index holds title and text columns with default BM25 weights.

{\sloppy
\paragraph{Conditions.} \textsc{bm25-and} (the buggy builder), \textsc{bm25-or-raw} (OR over every token), \textsc{bm25-or} (the fix), \textsc{dense}, \textsc{hybrid-and} (dense + buggy keyword, RRF) and \textsc{hybrid-or} (dense + fixed keyword, RRF). Depth $K = 100$ for every retriever and $k = 60$ for fusion, so the ceiling is read in its one-sided form and overlap is also counted directly from the ranks. The 18 collection--encoder pairs give $3\,727 \times 3 \times 2 = 22\,362$ hybrid query runs. The three encoders rerun the same queries, so they are not independent replications.\par}

\paragraph{Diagnostics.} For each hybrid condition the runner records, per query, whether the keyword leg returned nothing, how many documents it returned, whether the maximum fused score sat at $1/k$, the maximum itself, and how many documents both legs credited. These see the lists as fused.

\paragraph{Effectiveness.} nDCG@10 and Recall@100 through \texttt{pytrec\_eval} \citep{vangysel2018pytrec}. Before scoring, a document whose id equals the query's id is removed, the default of BEIR's evaluator; this touches 1\,298 of ArguAna's 1\,406 queries and 55 of FiQA's 648, and no query elsewhere; on FiQA none of the 55 same-id documents reached a fused top 10 or was relevant, so its figures are the same with and without the rule. The 108 ArguAna queries whose text is a corpus document under another id are not touched. Differences between conditions are tested per pair with a two-sided paired randomization test over queries (sign flips, $10^5$ trials; \citealp{smucker2007comparison}) and Holm's correction within each family of 18 pairs; a difference is called significant at $\alpha = 0.05$ after correction. Per-query scores and the test's output are in \texttt{results/}.

\paragraph{Hardware.} Every run reported here was made in one Kaggle kernel on an NVIDIA T4 (Appendix~\ref{app:run}). Query times are mean wall-clock per query for the dense search, the keyword search and the fusion, with query encoding excluded; the keyword search and the fusion run on the host's CPU, which is shared, so times compare conditions within a collection and only loosely across collections.

\section{Results}
\label{sec:results}

Whether the keyword leg is alive and overlapping with the dense leg, and whether the hybrid retrieves better than its parts, are different questions, and the subsections below keep them apart: Table~\ref{tab:legs} and Figure~\ref{fig:length} are about the leg and the ceiling, Tables~\ref{tab:ndcg} and~\ref{tab:recall} about effectiveness, and every condition for every pair is in Appendix~\ref{app:full}.

\begin{table}[h]
\centering
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrrrrr}
\toprule
 & & & & \multicolumn{2}{c}{quoted AND} & \multicolumn{2}{c}{OR after the drop} \\
\cmidrule(lr){5-6}\cmidrule(lr){7-8}
Collection & docs & queries & tokens & kw empty & at ceiling & kw empty & at ceiling \\
\midrule
SciFact & 5\,183 & 300 & 12.6 & 98.0\% & 98.0\% & 0.0\% & 0.0\% \\
NFCorpus & 3\,633 & 323 & 3.3 & 50.8\% & 51.4--51.7\% & 7.7\% & 7.7--8.7\% \\
ArguAna & 8\,674 & 1\,406 & 195.1 & 0.0\% & 0.0\% & 0.0\% & 0.0\% \\
SciDocs & 25\,657 & 1\,000 & 9.4 & 94.2\% & 94.7--94.9\% & 0.0\% & 0.1\% \\
FiQA & 57\,638 & 648 & 11.1 & 81.8\% & 87.2--88.4\% & 0.0\% & 0.0--0.3\% \\
TREC-COVID & 171\,332 & 50 & 10.6 & 74.0\% & 88.0--90.0\% & 0.0\% & 0.0\% \\
\bottomrule
\end{tabular}
\caption{The keyword leg and the ceiling on six BEIR collections. ``tokens'' is the mean query length in the builder's own tokens. ``kw empty'' is the fraction of queries on which the keyword leg returned no document; it does not depend on the encoder. ``at ceiling'' is the fraction on which the maximum fused score of the hybrid was $1/k$, given as the range over the three encoders where they differ.}
\label{tab:legs}
\end{table}

\subsection{The leg}
\label{sec:leg}

The quoted-AND builder matched nothing on 294 of SciFact's 300 claim-length queries, 942 of SciDocs's 1\,000 titles, 530 of FiQA's 648 questions, 37 of TREC-COVID's 50 questions and 164 of NFCorpus's 323 titles. Mean query length alone does not order these: NFCorpus has the shortest queries and the lowest rate, but TREC-COVID's questions are about as long as FiQA's and SciDocs's and come out lower. Counting only the tokens the fixed builder would keep orders all five, in \texttt{results/keyword\_facts.json}: 8.7 content tokens per query on SciFact, 7.3 on SciDocs, 6.2 on FiQA, 5.7 on TREC-COVID and 2.5 on NFCorpus, against empty rates of 98.0, 94.2, 81.8, 74.0 and 50.8\%. This is close to arithmetic rather than a finding about the collections: every quoted token is one more condition a single document must meet, stopwords are met almost everywhere, and the content words are the conditions that fail. Ordering by raw token count puts SciDocs fourth of the five; counting content words moves it to second, where its empty rate sits. Five collections are too few to call it a law, and the collections also differ in corpus size, document length and vocabulary.

BM25 with the fixed builder is a usable retriever on every collection (Appendix~\ref{app:full}), and after the fix only NFCorpus has queries that match nothing: 25 title queries (7.7\%), none of whose tokens occur in the corpus at all, since the raw OR is empty on the same 25. The stopword drop that made the fix cheap in production is cheaper everywhere and costs little effectiveness: \textsc{bm25-or-raw} is 2.2 to 18 times slower (13.6 against 4.1\,ms on SciFact, 2.6 against 1.2 on NFCorpus, 905 against 52 on ArguAna, whose queries average 195 tokens) and worse at nDCG@10 by 0.001 to 0.010 on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.012 Recall@100, at 5.6 times the cost.

\subsection{A leg that is never empty and almost never relevant}
\label{sec:arguana}

ArguAna's queries are whole arguments, 195 tokens on average, and the quoted-AND builder never returned nothing for them: it returned one document for 1\,402 of the 1\,406 queries and two for the other four. The reason is the collection's construction. Every query's text is also a document in the corpus, and a query is the one text guaranteed to contain all of its own tokens: on all 1\,406 queries the AND leg returned a document whose text equals the query's after whitespace and case normalisation, under the query's own identifier on 1\,298 (at the top of the list on 1\,296) and under another identifier on the remaining 108. A query's own document is not one of its relevant documents, and the AND leg returned a relevant document for one query in 1\,406.

The ceiling cannot see this. The dense leg also returns that document in its top 100 on every query for every encoder, so the two legs share it, the fused maximum is above $1/k$ on every query, and the ceiling never fired: Table~\ref{tab:legs} shows 0.0\% for every encoder. Fusion with this leg changed nothing measurable: \textsc{hybrid-and} and \textsc{dense} agree to every decimal the result files carry in both metrics for all three encoders, which is what a dead leg looks like from the outside. The ceiling tests for agreement, and a leg that agrees with the other leg on one useless document passes it. Per-leg row counts do not catch it either, since the leg returns a row on every query; what catches it is the distribution of row counts, one document on 99.7\% of queries, which is as much an alarm as zero. ArguAna's construction is unusual, but a corpus that indexes the kind of text it is queried with is not: a search engine over a mailbox, a notes vault or a ticket tracker can receive the text of an indexed item as a query. Whether the self-match is then a failure depends on the task; when finding the source item is the point, it is the answer.

\subsection{What fusion did with an empty list}
\label{sec:emptylist}

When the keyword leg is empty, the fused list is the dense list. On the 294 SciFact queries with an empty keyword leg, the per-query rows show \textsc{hybrid-and}'s list is \textsc{dense}'s list: same document count, maximum score exactly $1/60$. Over the whole collection the two conditions differ by at most 0.003 nDCG@10 and 0.000 Recall@100 as printed in Tables~\ref{tab:ndcg} and~\ref{tab:recall} (0.0022 and 0.0000 before rounding), all of it from the six live queries, and on SciDocs, with 942 empty legs, by at most 0.001 in each. Two collections moved more, in opposite directions, and the number of live queries does not predict which: on NFCorpus (159 live queries of 323) \textsc{hybrid-and} is above \textsc{dense} by 0.008 to 0.014 nDCG@10, and on TREC-COVID (13 live queries of 50) it is below by 0.027 to 0.039.

\subsection{The ceiling against the row count}
\label{sec:rowcount}

An empty keyword leg puts the maximum fused score at exactly $1/k$ whenever the dense leg returned anything, so the set of empty-leg queries is contained in the set of at-ceiling queries, and the ceiling missed no empty leg on any of the 22\,362 hybrid query runs. Everything the two instruments disagree on is the excess, at-ceiling queries whose leg was not empty: 176 query runs, 164 under the buggy builder and 12 under the fixed one. On SciFact and ArguAna there was none. Under the buggy builder the excess is 2 or 3 of NFCorpus's 159 live-leg queries (1.3 to 1.9\%), 5 to 7 of SciDocs's 58 (8.6 to 12.1\%), 35 to 43 of FiQA's 118 (29.7 to 36.4\%) and 7 or 8 of TREC-COVID's 13 (53.8 to 61.5\%), the range running over the encoders.

In 174 of the 176 the two legs shared no document: read as a zero-overlap test the ceiling was right on them, read as an empty-leg alarm it was wrong, and the row count tells the two readings apart. The other two are the case Section~\ref{sec:ceiling} said $K > k$ leaves open. On one FiQA query for bge and one for e5, under the fixed builder, both legs returned 100 documents and shared one, ranked deep enough in both that its fused score did not exceed $1/k$; the ceiling fired with overlap present. Two in 22\,362 is rare, but it is not zero, and it is why a system that runs at $K > k$ should count shared documents directly.

\begin{figure}[t]
\centering
\includegraphics[width=\textwidth]{fig-ceiling-length.pdf}
\caption{Fraction of hybrid query runs on which the ceiling fired, by the number of documents the keyword leg returned, pooled over both builders and all three encoders. A hollow marker is a cell with fewer than ten runs; a gap is a cell with none. SciFact and ArguAna sit at zero in every cell, under the other lines. Empty legs, at 100\% by construction, are not drawn.}
\label{fig:length}
\end{figure}

How often a live list shares nothing with the dense top $K$ depends on how short it is (Figure~\ref{fig:length}). Pooled over every collection except ArguAna, where the leg is never disjoint, and over both builders, the ceiling fired on 137 of the 726 live-leg query runs in which the leg returned one to three documents (18.9\%), on 35 of 588 with four to 49 (6.0\%) and on 4 of 6\,636 with 50 or more (0.06\%; the last four are two zero-overlap runs and the two overlap-present FiQA runs above). The buggy builder supplies most of the short lists: 612 of the 726 runs in the first bucket, firing on 132 of them, against 5 of 114 for the fixed builder. The short-list rate differs by collection: 0 of 18 on SciFact (5.2k documents), 13 of 330 on NFCorpus (3.6k), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k; six distinct queries, each run under three encoders). The four nonzero rates rise with corpus size and SciFact does not fit the ordering, so this is a pattern across four collections that differ in more than size, not a size effect. A short exact-match list over a large corpus was, on these collections, usually a different handful of documents from the dense top 100, whether or not it was any good. The ceiling also fired over a leg of four or more documents on 39 runs, all on FiQA, TREC-COVID and SciDocs, so ``a short leg'' is not a safe reading of every excess query; the row count is.

\subsection{Effectiveness is a separate question}
\label{sec:effect}

\begin{table}[h]
\centering
\small
\begin{tabular}{lrrrrrrrrr}
\toprule
 & \multicolumn{3}{c}{bge-base-en-v1.5} & \multicolumn{3}{c}{nomic-embed-text-v1.5} & \multicolumn{3}{c}{e5-base-v2} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}
Collection & dense & h-and & h-or & dense & h-and & h-or & dense & h-and & h-or \\
\midrule
SciFact & 0.740 & 0.741 & 0.723 & 0.703 & 0.705 & 0.708 & 0.719 & 0.722 & 0.726 \\
NFCorpus & 0.374 & 0.382 & 0.363 & 0.347 & 0.361$^{*}$ & 0.344 & 0.355 & 0.368$^{*}$ & 0.352 \\
ArguAna & 0.641 & 0.641 & 0.606$^{*}$ & 0.483 & 0.483 & 0.517$^{*}$ & 0.447 & 0.447 & 0.532$^{*}$ \\
SciDocs & 0.217 & 0.216 & 0.195$^{*}$ & 0.187 & 0.187 & 0.182 & 0.187 & 0.186 & 0.183 \\
FiQA & 0.406 & 0.396$^{*}$ & 0.348$^{*}$ & 0.376 & 0.367$^{*}$ & 0.330$^{*}$ & 0.399 & 0.389$^{*}$ & 0.362$^{*}$ \\
TREC-COVID & 0.779 & 0.744$^{*}$ & 0.763 & 0.823 & 0.784 & 0.769 & 0.696 & 0.669 & 0.714 \\
\bottomrule
\end{tabular}
\caption{nDCG@10 of the dense retriever, the hybrid with the buggy keyword leg (h-and) and the hybrid with the fixed one (h-or). A star marks a hybrid whose paired difference from the dense retriever of the same encoder is significant at $\alpha = 0.05$ after Holm's correction (two-sided randomization test, $10^5$ sign flips, 18 pairs per family).}
\label{tab:ndcg}
\end{table}

\begin{table}[h]
\centering
\small
\begin{tabular}{lrrrrrrrrr}
\toprule
 & \multicolumn{3}{c}{bge-base-en-v1.5} & \multicolumn{3}{c}{nomic-embed-text-v1.5} & \multicolumn{3}{c}{e5-base-v2} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}
Collection & dense & h-and & h-or & dense & h-and & h-or & dense & h-and & h-or \\
\midrule
SciFact & 0.967 & 0.967 & 0.969 & 0.928 & 0.928 & 0.958 & 0.963 & 0.963 & 0.959 \\
NFCorpus & 0.337 & 0.341$^{*}$ & 0.337 & 0.298 & 0.303$^{*}$ & 0.309 & 0.319 & 0.323$^{*}$ & 0.328 \\
ArguAna & 0.993 & 0.993 & 0.991 & 0.980 & 0.980 & 0.984 & 0.949 & 0.949 & 0.981$^{*}$ \\
SciDocs & 0.496 & 0.495 & 0.469$^{*}$ & 0.404 & 0.404 & 0.409 & 0.421 & 0.421 & 0.425 \\
FiQA & 0.741 & 0.740 & 0.715$^{*}$ & 0.682 & 0.682 & 0.675 & 0.732 & 0.732 & 0.711 \\
TREC-COVID & 0.141 & 0.140 & 0.133 & 0.150 & 0.148 & 0.137$^{*}$ & 0.128 & 0.127 & 0.124 \\
\bottomrule
\end{tabular}
\caption{Recall@100, same conditions, layout and star as Table~\ref{tab:ndcg}.}
\label{tab:recall}
\end{table}

Repairing the leg raises overlap: the mean number of documents credited by both legs rose from at most 4.0 per query (Appendix~\ref{app:full}) to between 19.0 and 43.7 in every collection--encoder pair. It does not reliably improve retrieval (Tables~\ref{tab:ndcg} and~\ref{tab:recall}). Over the 18 pairs, the repaired hybrid is above \textsc{dense} at nDCG@10 in 5 and below it in 13, and the paired test calls 2 of the gains and 5 of the losses significant; at Recall@100 it is above in 9 (one significant; the ninth, NFCorpus with bge, by 0.0006, which the table rounds to a tie) and below in 9 (three significant); and the buggy hybrid is above the repaired one at nDCG@10 in 12 (six significant) and below it in 6 (two significant). The two significant gains over \textsc{dense} are on ArguAna, the one collection where BM25 alone (0.484) is above two of the three encoders at nDCG@10, e5 (0.447) and, by 0.001, nomic (0.483): the repaired hybrid gains 0.085 for e5 and 0.034 for nomic, and loses 0.035 for bge, the encoder BM25 does not match, also significantly. The other three gains are small and not significant (0.005 and 0.007 on SciFact for nomic and e5; 0.018 on TREC-COVID for e5). The losses are largest on FiQA, where BM25 is far behind every encoder (0.224 nDCG@10 against 0.376 to 0.406) and the repaired hybrid is 0.037 to 0.058 below \textsc{dense}, significant for every encoder.

The buggy hybrid's 12 wins over the repaired one are mostly abstention. In 8 of the 12 the buggy hybrid is not above \textsc{dense}: on seven of them its leg was empty on 74 to 94\% of queries, on ArguAna with bge it returned only the self-match, so the fused list was the dense list on those queries, and the repaired leg's OR list diluted the top 10. Only on NFCorpus (all three encoders) and SciFact with bge is the buggy hybrid above \textsc{dense} as well, by 0.001 on SciFact and by 0.008 to 0.014 on NFCorpus (significant for nomic and e5), where the AND leg was live on half the queries and returned short exact-match lists. Unweighted RRF treats a weak keyword list and a strong dense list alike, which is one reason \citet{bruch2023fusion} find a tuned convex combination competitive; whether RRF over BM25 and a given dense encoder helps is a question these runs answer only per pair. A monitor for overlap and activity and a verdict on retrieval effectiveness are different instruments.

\subsection{How short is too short}
\label{sec:sweep}

To measure the test against short live legs under control, the fixed keyword list was capped at its first $n$ documents and fused with the dense top $K$, for $K \in \{60, 100\}$, on every SciFact and NFCorpus query where the leg returned anything, for bge and nomic (Table~\ref{tab:sweep}). A cap, not a length: a query whose leg returned fewer than $n$ documents keeps its short list in every cell, so each cell measures the ceiling rate given a cap of $n$ over the same 300 and 298 queries. Three things hold in every cell for both encoders. The ceiling fired exactly on the queries where the two lists shared no document: the fired rate and the disjoint rate are equal to the query. The rate falls fast with the cap; the ranges that follow pool the two encoders' cells, of which Table~\ref{tab:sweep} prints bge's: at $K = 60$, a cap of one document leaves the lists disjoint on 8.7 to 15.1\% of queries, a cap of three on 2.7 to 6.7\%, a cap of ten on 0.7 to 2.3\%, and a cap of twenty or more on at most 1.7\%, under 1\% in 11 of the two encoders' 20 cells. A deeper dense list never raises a figure. The $K > k$ leak, a ceiling with overlap hidden at deep ranks, is impossible by arithmetic unless $(n-1)(K-1) \ge k^2$, which among these cells holds only at $K = 100$ with $n \in \{50, 100\}$; in those eight cells, 2\,392 query runs, it did not occur. It did occur twice in the natural FiQA runs above, both with $n = 100$, so the sweep's zero is a property of these two small collections, not of the test. The sweep was not repeated on the four larger collections; the natural row counts above stand in for it there, and they show the short-list rate is several times higher on three of them than these two suggest.

\begin{table}[h]
\centering
\small
\begin{tabular}{rrrrr}
\toprule
 & \multicolumn{2}{c}{SciFact} & \multicolumn{2}{c}{NFCorpus} \\
$n$ & $K=60$ & $K=100$ & $K=60$ & $K=100$ \\
\midrule
1 & 8.7\% & 5.3\% & 15.1\% & 11.1\% \\
2 & 5.3\% & 1.7\% & 9.1\% & 6.0\% \\
3 & 2.7\% & 1.0\% & 6.0\% & 3.4\% \\
5 & 1.3\% & 0.7\% & 3.7\% & 2.0\% \\
10 & 1.0\% & 0.7\% & 2.3\% & 1.0\% \\
20 & 1.0\% & 0.0\% & 1.7\% & 1.0\% \\
50 & 0.3\% & 0.0\% & 1.3\% & 1.0\% \\
100 & -- & 0.0\% & -- & 1.0\% \\
\bottomrule
\end{tabular}
\caption{Fraction of live-leg queries on which the ceiling fired when the fixed keyword list is cut to its first $n$ documents and fused with the dense top $K$ (\texttt{bge-base-en-v1.5}; 300 SciFact and 298 NFCorpus live-leg queries). In every cell this fraction equals the fraction of queries whose two lists were disjoint, and the fraction that fired with overlap present is zero. The nomic encoder's figures are within 4.4 points of these at $n=1$ and within 1.0 point from $n=3$ on; they are in \texttt{results/*.sweep.json}.}
\label{tab:sweep}
\end{table}

\section{What to check in your own system}
\label{sec:discussion}

Log, per query, each retriever's row count and the maximum fused score. If the maximum sits at $1/k$ (or $1/(k+1)$ for one-based ranks) on more than a few queries, then with per-retriever depth $K \le k$ the retrievers are not agreeing on anything, and at greater depth no document is shared at ranks $r_1, r_2$ with $r_1 r_2 < k^2$; read the row counts to learn whether one of them is empty, nearly empty, or retrieving from a different part of the corpus, and at greater depth count shared documents directly. A ceiling over a short live list was common on the larger collections here, so a ceiling is a reason to read the row count, not a verdict. Look at the distribution of row counts, not only at zero: a leg that returns one document on nearly every query is as suspect as one that returns none, and if the corpus indexes the kind of text it is queried with (messages, notes, tickets), check whether that one document is the query itself and whether returning it is the task. Test the keyword builder with a conversational sentence, not a two-word term, and treat zero rows for a six-word query as something to explain, since a legitimately selective query can return nothing. And if your fusion scores look ``flat'', compute $1/(k+r+1)$ before concluding anything about fusion. None of these signals is a verdict on effectiveness: on these collections a leg that was alive and overlapping made the hybrid worse than the dense retriever alone more often than better (significantly worse in five pairs, significantly better in two), and that question needs relevance judgements, not scores.

\section{Limitations}
\label{sec:limits}

The production measurements are on ten and fifteen queries over private corpora and are reported as aggregates the reader cannot check; they establish that the failure happened and how it looked, not an effect size, and the claim that the leg had been inert since the system's first version is an inference from unchanged code. The public reproduction uses six collections and three encoders of one size class (768-dimensional, base-sized) and FTS5's default BM25 weighting of title and text; the three encoders rerun the same queries, so the 18 pairs are not 18 independent samples, and the paired tests are corrected within each family of 18 but not across the six families. The collections differ in several ways at once, so the orderings reported here (empty rate against content words per query, short-list disjointness across collections of different size) are observations over five or six points, not controlled effects, and the pooled row-count rates mix the two builders, whose short lists arise differently. The truncation sweep covers only the two smallest collections. The exact ceiling statement needs $K \le k$, and the guarantee that an empty leg is never missed needs two retrievers; the common $K=100, k=60$ setting gets the one-sided direction and the direct overlap count instead, and it produced two ceilings with overlap present. The ceiling detects zero overlap; attributing it to an empty leg needs the per-leg row counts, and a leg that returns one useless document the other leg also returns, as on ArguAna, passes both the ceiling and a zero-row check. The negative results in Appendix~\ref{app:negative} are negative on one system each.

\section{Conclusion}
\label{sec:conclusion}

With per-retriever depth $K \le k$, a maximum reciprocal-rank-fusion score of $1/k$ over a result list means no document in it was returned by more than one retriever, and a system that fuses can read that from the scores it already computes. In the incident, the ceiling had been present on every query for as long as the keyword query builder had existed; it was read twice as a property of fusion. On six BEIR collections the ceiling missed no empty keyword leg in 22\,362 runs, fired over a nonempty but disjoint leg on 174, mostly short lists on the larger corpora, and twice over lists that shared one document deep in both at $K > k$. It is blind by construction to a leg that returns a document the other leg also returns, which ArguAna shows with a leg that is never empty and almost never relevant; the distribution of row counts is the instrument for that case. Repairing the leg raised overlap in every pair and moved nDCG@10 above the dense retriever alone in 5 of 18, two of them significantly, and below it in 13, five significantly, so the health of a leg and the value of fusing it remain separate questions.

\section*{Use of AI tools}

The code, the experiment and audit scripts, and the text of this paper were drafted with Claude (Anthropic) running in Claude Code, directed by the author, who operated the production system in which the incident occurred, chose what to measure, ruled on every claim and takes responsibility for all content. Drafts were reviewed by GPT-6 (Astra, Sol and Luna), GPT-6.1 Sol, SWE-2, Gemini 4 Argon, Gemini, Grok 4.7, DeepSeek V4.1 Flash, GPT-5.6 and Claude Fable 5.1, through Cognition's Devin CLI, Cursor, Kagi and vendor CLIs; every defect a reviewer reported was reproduced or refuted by a script before it changed the paper, and the review records, probes and the audit script that checks every number in the text against the result files are in the repository. Every reference was checked against a primary listing.

\acks{This work received no funding. The author declares no competing interests.}

\bibliography{refs}

\appendix
\section{Two negative results measured beside the dead leg}
\label{app:negative}

Both of the following were measured on the production system before the keyword leg was fixed, with seven to fifteen queries each; both verdicts stand on their own terms, and neither says anything about the techniques in general.

\paragraph{Recency decay.} A multiplicative age penalty on fused scores (floor 0.85, time constant 180 days) changed the top-1 result on 4 of 7 real queries on a notes corpus, and the changes were as often wrong as right; a canonical note unedited for 338 days was demoted under a 13-day-old draft. On a second corpus spanning only 63 days the multiplier varied between 0.956 and 1.000 across every document and changed 0 of 8 top-1 results. The feature was rejected. At the time the sensitivity was attributed to flat fused scores; Section~\ref{sec:intro} shows the relative step between consecutive singleton scores is a property of the formula, and two identical live lists would show the same step, so the flatness said nothing about the leg, and whether decay would behave differently over a fused list with real two-leg scores was not tested.

\paragraph{A title prefix before embedding.} Prepending \texttt{kind: title} to each chunk before embedding (the stored text and the keyword index unchanged, so the vector was the only variable) and re-embedding one corpus of 3\,046 documents and 30\,734 chunks took 25 minutes. On 15 realistic queries, 13 had an identical top-1, mean top-5 overlap was 80\%, one query improved and one regressed, and the query predicted to benefit most returned an identical, still wrong, top 3. The change was not adopted. This is a heading prefix: neither document expansion by generated queries \citep{nogueira2019doc2query} nor the model-written situating context of \citet{anthropic2024contextual}, and the corpus was a weak test (documents whose title is their opening line). Because the keyword leg was inert, the A/B measured the vector change alone, which was the intent.

\section{All conditions, all collections}
\label{app:full}

Tables~\ref{tab:full-bge}, \ref{tab:full-nomic} and~\ref{tab:full-e5} give all six conditions for each encoder. The BM25-only rows do not depend on the encoder and repeat across the three tables. ``kw empty'' is the fraction of queries on which the keyword leg returned no document; ``at ceiling'' the fraction on which the maximum fused score was $1/k$; ``both-leg'' the mean number of documents credited by both retrievers. Query times are in \texttt{results/*.json} and are omitted here because the collections were timed on two different machines (Appendix~\ref{app:run}).

\begin{table}[p]
\centering
\small
\begin{tabular}{llrrrrr}
\toprule
Collection & Condition & nDCG@10 & R@100 & kw empty & at ceiling & both-leg \\
\midrule
SciFact & bm25-and & 0.018 & 0.018 & 98.0\% & -- & -- \\
SciFact & bm25-or-raw & 0.659 & 0.879 & 0.0\% & -- & -- \\
SciFact & bm25-or & 0.665 & 0.876 & 0.0\% & -- & -- \\
SciFact & dense & 0.740 & 0.967 & -- & -- & -- \\
SciFact & hybrid-and & 0.741 & 0.967 & 98.0\% & 98.0\% & 0.02 \\
SciFact & hybrid-or & 0.723 & 0.969 & 0.0\% & 0.0\% & 28.9 \\
\midrule
NFCorpus & bm25-and & 0.193 & 0.095 & 50.8\% & -- & -- \\
NFCorpus & bm25-or-raw & 0.304 & 0.232 & 7.7\% & -- & -- \\
NFCorpus & bm25-or & 0.306 & 0.233 & 7.7\% & -- & -- \\
NFCorpus & dense & 0.374 & 0.337 & -- & -- & -- \\
NFCorpus & hybrid-and & 0.382 & 0.341 & 50.8\% & 51.7\% & 4.0 \\
NFCorpus & hybrid-or & 0.363 & 0.337 & 7.7\% & 8.7\% & 21.3 \\
\midrule
ArguAna & bm25-and & 0.001 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.473 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.484 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.641 & 0.993 & -- & -- & -- \\
ArguAna & hybrid-and & 0.641 & 0.993 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.606 & 0.991 & 0.0\% & 0.0\% & 38.6 \\
\midrule
SciDocs & bm25-and & 0.003 & 0.002 & 94.2\% & -- & -- \\
SciDocs & bm25-or-raw & 0.152 & 0.343 & 0.0\% & -- & -- \\
SciDocs & bm25-or & 0.153 & 0.344 & 0.0\% & -- & -- \\
SciDocs & dense & 0.217 & 0.496 & -- & -- & -- \\
SciDocs & hybrid-and & 0.216 & 0.495 & 94.2\% & 94.9\% & 0.13 \\
SciDocs & hybrid-or & 0.195 & 0.469 & 0.0\% & 0.1\% & 29.3 \\
\midrule
FiQA & bm25-and & 0.014 & 0.015 & 81.8\% & -- & -- \\
FiQA & bm25-or-raw & 0.233 & 0.521 & 0.0\% & -- & -- \\
FiQA & bm25-or & 0.224 & 0.508 & 0.0\% & -- & -- \\
FiQA & dense & 0.406 & 0.741 & -- & -- & -- \\
FiQA & hybrid-and & 0.396 & 0.740 & 81.8\% & 87.2\% & 0.44 \\
FiQA & hybrid-or & 0.348 & 0.715 & 0.0\% & 0.3\% & 22.1 \\
\midrule
TREC-COVID & bm25-and & 0.075 & 0.003 & 74.0\% & -- & -- \\
TREC-COVID & bm25-or-raw & 0.532 & 0.091 & 0.0\% & -- & -- \\
TREC-COVID & bm25-or & 0.538 & 0.101 & 0.0\% & -- & -- \\
TREC-COVID & dense & 0.779 & 0.141 & -- & -- & -- \\
TREC-COVID & hybrid-and & 0.744 & 0.140 & 74.0\% & 90.0\% & 0.86 \\
TREC-COVID & hybrid-or & 0.763 & 0.133 & 0.0\% & 0.0\% & 21.6 \\
\bottomrule
\end{tabular}
\caption{\texttt{bge-base-en-v1.5}, all conditions.}
\label{tab:full-bge}
\end{table}

\begin{table}[p]
\centering
\small
\begin{tabular}{llrrrrr}
\toprule
Collection & Condition & nDCG@10 & R@100 & kw empty & at ceiling & both-leg \\
\midrule
SciFact & bm25-and & 0.018 & 0.018 & 98.0\% & -- & -- \\
SciFact & bm25-or-raw & 0.659 & 0.879 & 0.0\% & -- & -- \\
SciFact & bm25-or & 0.665 & 0.876 & 0.0\% & -- & -- \\
SciFact & dense & 0.703 & 0.928 & -- & -- & -- \\
SciFact & hybrid-and & 0.705 & 0.928 & 98.0\% & 98.0\% & 0.02 \\
SciFact & hybrid-or & 0.708 & 0.958 & 0.0\% & 0.0\% & 25.9 \\
\midrule
NFCorpus & bm25-and & 0.193 & 0.095 & 50.8\% & -- & -- \\
NFCorpus & bm25-or-raw & 0.304 & 0.232 & 7.7\% & -- & -- \\
NFCorpus & bm25-or & 0.306 & 0.233 & 7.7\% & -- & -- \\
NFCorpus & dense & 0.347 & 0.298 & -- & -- & -- \\
NFCorpus & hybrid-and & 0.361 & 0.303 & 50.8\% & 51.7\% & 3.7 \\
NFCorpus & hybrid-or & 0.344 & 0.309 & 7.7\% & 8.4\% & 21.0 \\
\midrule
ArguAna & bm25-and & 0.001 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.473 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.484 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.483 & 0.980 & -- & -- & -- \\
ArguAna & hybrid-and & 0.483 & 0.980 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.517 & 0.984 & 0.0\% & 0.0\% & 43.7 \\
\midrule
SciDocs & bm25-and & 0.003 & 0.002 & 94.2\% & -- & -- \\
SciDocs & bm25-or-raw & 0.152 & 0.343 & 0.0\% & -- & -- \\
SciDocs & bm25-or & 0.153 & 0.344 & 0.0\% & -- & -- \\
SciDocs & dense & 0.187 & 0.404 & -- & -- & -- \\
SciDocs & hybrid-and & 0.187 & 0.404 & 94.2\% & 94.8\% & 0.17 \\
SciDocs & hybrid-or & 0.182 & 0.409 & 0.0\% & 0.1\% & 32.3 \\
\midrule
FiQA & bm25-and & 0.014 & 0.015 & 81.8\% & -- & -- \\
FiQA & bm25-or-raw & 0.233 & 0.521 & 0.0\% & -- & -- \\
FiQA & bm25-or & 0.224 & 0.508 & 0.0\% & -- & -- \\
FiQA & dense & 0.376 & 0.682 & -- & -- & -- \\
FiQA & hybrid-and & 0.367 & 0.682 & 81.8\% & 87.5\% & 0.45 \\
FiQA & hybrid-or & 0.330 & 0.675 & 0.0\% & 0.0\% & 24.1 \\
\midrule
TREC-COVID & bm25-and & 0.075 & 0.003 & 74.0\% & -- & -- \\
TREC-COVID & bm25-or-raw & 0.532 & 0.091 & 0.0\% & -- & -- \\
TREC-COVID & bm25-or & 0.538 & 0.101 & 0.0\% & -- & -- \\
TREC-COVID & dense & 0.823 & 0.150 & -- & -- & -- \\
TREC-COVID & hybrid-and & 0.784 & 0.148 & 74.0\% & 88.0\% & 0.70 \\
TREC-COVID & hybrid-or & 0.769 & 0.137 & 0.0\% & 0.0\% & 21.9 \\
\bottomrule
\end{tabular}
\caption{\texttt{nomic-embed-text-v1.5}, all conditions.}
\label{tab:full-nomic}
\end{table}

\begin{table}[p]
\centering
\small
\begin{tabular}{llrrrrr}
\toprule
Collection & Condition & nDCG@10 & R@100 & kw empty & at ceiling & both-leg \\
\midrule
SciFact & bm25-and & 0.018 & 0.018 & 98.0\% & -- & -- \\
SciFact & bm25-or-raw & 0.659 & 0.879 & 0.0\% & -- & -- \\
SciFact & bm25-or & 0.665 & 0.876 & 0.0\% & -- & -- \\
SciFact & dense & 0.719 & 0.963 & -- & -- & -- \\
SciFact & hybrid-and & 0.722 & 0.963 & 98.0\% & 98.0\% & 0.02 \\
SciFact & hybrid-or & 0.726 & 0.959 & 0.0\% & 0.0\% & 27.9 \\
\midrule
NFCorpus & bm25-and & 0.193 & 0.095 & 50.8\% & -- & -- \\
NFCorpus & bm25-or-raw & 0.304 & 0.232 & 7.7\% & -- & -- \\
NFCorpus & bm25-or & 0.306 & 0.233 & 7.7\% & -- & -- \\
NFCorpus & dense & 0.355 & 0.319 & -- & -- & -- \\
NFCorpus & hybrid-and & 0.368 & 0.323 & 50.8\% & 51.4\% & 3.8 \\
NFCorpus & hybrid-or & 0.352 & 0.328 & 7.7\% & 7.7\% & 20.6 \\
\midrule
ArguAna & bm25-and & 0.001 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.473 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.484 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.447 & 0.949 & -- & -- & -- \\
ArguAna & hybrid-and & 0.447 & 0.949 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.532 & 0.981 & 0.0\% & 0.0\% & 33.5 \\
\midrule
SciDocs & bm25-and & 0.003 & 0.002 & 94.2\% & -- & -- \\
SciDocs & bm25-or-raw & 0.152 & 0.343 & 0.0\% & -- & -- \\
SciDocs & bm25-or & 0.153 & 0.344 & 0.0\% & -- & -- \\
SciDocs & dense & 0.187 & 0.421 & -- & -- & -- \\
SciDocs & hybrid-and & 0.186 & 0.421 & 94.2\% & 94.7\% & 0.15 \\
SciDocs & hybrid-or & 0.183 & 0.425 & 0.0\% & 0.1\% & 31.7 \\
\midrule
FiQA & bm25-and & 0.014 & 0.015 & 81.8\% & -- & -- \\
FiQA & bm25-or-raw & 0.233 & 0.521 & 0.0\% & -- & -- \\
FiQA & bm25-or & 0.224 & 0.508 & 0.0\% & -- & -- \\
FiQA & dense & 0.399 & 0.732 & -- & -- & -- \\
FiQA & hybrid-and & 0.389 & 0.732 & 81.8\% & 88.4\% & 0.36 \\
FiQA & hybrid-or & 0.362 & 0.711 & 0.0\% & 0.3\% & 19.0 \\
\midrule
TREC-COVID & bm25-and & 0.075 & 0.003 & 74.0\% & -- & -- \\
TREC-COVID & bm25-or-raw & 0.532 & 0.091 & 0.0\% & -- & -- \\
TREC-COVID & bm25-or & 0.538 & 0.101 & 0.0\% & -- & -- \\
TREC-COVID & dense & 0.696 & 0.128 & -- & -- & -- \\
TREC-COVID & hybrid-and & 0.669 & 0.127 & 74.0\% & 90.0\% & 0.78 \\
TREC-COVID & hybrid-or & 0.714 & 0.124 & 0.0\% & 0.0\% & 19.6 \\
\bottomrule
\end{tabular}
\caption{\texttt{e5-base-v2}, all conditions.}
\label{tab:full-e5}
\end{table}

\section{Run details}
\label{app:run}
{\sloppy
The SciFact and NFCorpus runs were first made on CPU (12-core x86-64, PyTorch CPU wheels), about an hour per collection and encoder for document embedding. All 18 collection--encoder pairs were then run in a Kaggle kernel on one NVIDIA T4 (\path{kaggle/run.py} in the repository, which clones the runner at a pinned commit and records package versions and the device in a manifest): PyTorch 2.11 with CUDA 12.8, \texttt{transformers} 4.49, \texttt{sentence-transformers} 3.4.1, \texttt{ir\_datasets} 0.6.3. At the same batch size, the GPU runs of the four pairs of the earlier version of this paper (SciFact and NFCorpus with bge and nomic) reproduced the CPU results to every digit the result files carry for nDCG@10 and Recall@100; every result file in the repository is from the Kaggle runs, and the CPU runs figure only as that reproduction check. Documents were embedded in batches of 64, except with nomic, which accepts 8\,192 tokens where the other two encoders stop at 512 and ran out of GPU memory at that size on the three largest collections, so every nomic run reported here used batches of 8. Batch size reaches the vectors only through padding and the order of floating-point operations; between batch 64 and batch 8 the nomic runs on SciFact were identical and on NFCorpus one query's fused maximum score changed in the fourth decimal, with no printed figure affected. \texttt{nomic-embed-text-v1.5} needs a 4.x \texttt{transformers} because its remote model code calls a method removed in 5.0; the runner pins it below 4.50. The encoder's document prefix is applied where its model card prescribes one (\texttt{search\_document:} for nomic, \texttt{passage:} for e5, none for bge); queries carry the query prefix (\texttt{search\_query:} for nomic; \texttt{query:} for e5; \texttt{Represent this sentence for searching relevant passages:} for bge, which its card asks for on retrieval queries and on nothing else). The FTS5 index is built atomically. ArguAna, SciDocs and TREC-COVID have a single test split in BEIR and are loaded as \texttt{beir/arguana}, \texttt{beir/scidocs} and \texttt{beir/trec-covid}.

The fixed builder's stoplist, 118 words: \emph{a an the and or but if then than that this these those of in on at to for from by with about into over under after before is are was were be been being am do does did doing have has had having i me my mine we us our you your he she it its they them their as not no nor so such can could should would will shall may might must what which who whom whose when where why how all any both each few more most other some only own same too very just dont don t s re ve ll m d get got make made want need know think see look}.

Per-query diagnostics are in \texttt{results/*.perquery.jsonl} and per-query effectiveness scores in \texttt{results/*.pereval.jsonl}; \texttt{scripts/keyword\_facts.py} computes the encoder-free keyword facts, \texttt{scripts/tables.py}, \texttt{scripts/natural\_lengths.py} and \texttt{scripts/figure.py} the tables, per-query counts and Figure~\ref{fig:length}, \texttt{scripts/significance.py} the paired tests, and the audit script \texttt{review/orrery-audit.py} checks every number in this paper against the result files.
\par}

\end{document}


=== paper/refs.bib ===

@inproceedings{cormack2009rrf,
  author    = {Gordon V. Cormack and Charles L. A. Clarke and Stefan B{\"u}ttcher},
  title     = {Reciprocal Rank Fusion Outperforms {Condorcet} and Individual Rank Learning Methods},
  booktitle = {Proceedings of the 32nd International {ACM} {SIGIR} Conference on Research and Development in Information Retrieval},
  year      = {2009},
  pages     = {758--759}
}

@inproceedings{thakur2021beir,
  author    = {Nandan Thakur and Nils Reimers and Andreas R{\"u}ckl{\'e} and Abhishek Srivastava and Iryna Gurevych},
  title     = {{BEIR}: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models},
  booktitle = {Thirty-fifth Conference on Neural Information Processing Systems, Datasets and Benchmarks Track},
  year      = {2021}
}

@article{bruch2023fusion,
  author  = {Sebastian Bruch and Siyu Gai and Amir Ingber},
  title   = {An Analysis of Fusion Functions for Hybrid Retrieval},
  journal = {{ACM} Transactions on Information Systems},
  volume  = {42},
  number  = {1},
  year    = {2024},
  pages   = {20:1--20:35}
}

@inproceedings{gao2021clear,
  author    = {Luyu Gao and Zhuyun Dai and Tongfei Chen and Zhen Fan and Benjamin {Van Durme} and Jamie Callan},
  title     = {Complement Lexical Retrieval Model with Semantic Residual Embeddings},
  booktitle = {Advances in Information Retrieval: 43rd European Conference on {IR} Research},
  year      = {2021},
  pages     = {146--160}
}

@inproceedings{cronentownsend2002qpp,
  author    = {Steve Cronen-Townsend and Yun Zhou and W. Bruce Croft},
  title     = {Predicting Query Performance},
  booktitle = {Proceedings of the 25th Annual International {ACM} {SIGIR} Conference on Research and Development in Information Retrieval},
  year      = {2002},
  pages     = {299--306}
}

@inproceedings{wadden2020scifact,
  author    = {David Wadden and Shanchuan Lin and Kyle Lo and Lucy Lu Wang and Madeleine van Zuylen and Arman Cohan and Hannaneh Hajishirzi},
  title     = {Fact or Fiction: Verifying Scientific Claims},
  booktitle = {Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing},
  year      = {2020},
  pages     = {7534--7550}
}

@inproceedings{boteva2016nfcorpus,
  author    = {Vera Boteva and Demian Gholipour Ghalandari and Artem Sokolov and Stefan Riezler},
  title     = {A Full-Text Learning to Rank Dataset for Medical Information Retrieval},
  booktitle = {Advances in Information Retrieval: 38th European Conference on {IR} Research},
  year      = {2016},
  pages     = {716--722}
}

@article{robertson2009bm25,
  author  = {Stephen Robertson and Hugo Zaragoza},
  title   = {The Probabilistic Relevance Framework: {BM25} and Beyond},
  journal = {Foundations and Trends in Information Retrieval},
  volume  = {3},
  number  = {4},
  year    = {2009},
  pages   = {333--389}
}

@article{nussbaum2024nomic,
  author  = {Zach Nussbaum and John X. Morris and Brandon Duderstadt and Andriy Mulyar},
  title   = {Nomic Embed: Training a Reproducible Long Context Text Embedder},
  journal = {arXiv preprint arXiv:2402.01613},
  year    = {2024}
}

@article{xiao2023cpack,
  author  = {Shitao Xiao and Zheng Liu and Peitian Zhang and Niklas Muennighoff},
  title   = {{C-Pack}: Packed Resources For General {Chinese} Embeddings},
  journal = {arXiv preprint arXiv:2309.07597},
  year    = {2023}
}

@inproceedings{vangysel2018pytrec,
  author    = {Christophe {Van Gysel} and Maarten de Rijke},
  title     = {Pytrec\_eval: An Extremely Fast Python Interface to trec\_eval},
  booktitle = {Proceedings of the 41st International {ACM} {SIGIR} Conference on Research and Development in Information Retrieval},
  year      = {2018},
  pages     = {873--876}
}

@inproceedings{macavaney2021irdatasets,
  author    = {Sean MacAvaney and Andrew Yates and Sergey Feldman and Doug Downey and Arman Cohan and Nazli Goharian},
  title     = {Simplified Data Wrangling with ir\_datasets},
  booktitle = {Proceedings of the 44th International {ACM} {SIGIR} Conference on Research and Development in Information Retrieval},
  year      = {2021},
  pages     = {2429--2436}
}

@misc{anthropic2024contextual,
  author       = {{Anthropic}},
  title        = {Introducing Contextual Retrieval},
  howpublished = {\url{https://www.anthropic.com/engineering/contextual-retrieval}},
  year         = {2024},
  note         = {Accessed 2026-10-07}
}

@misc{sqlite_fts5,
  author       = {D. Richard Hipp and others},
  title        = {{SQLite FTS5} Extension},
  howpublished = {\url{https://www.sqlite.org/fts5.html}},
  year         = {2026},
  note         = {Accessed 2026-10-07}
}

@article{webber2010rbo,
  author  = {William Webber and Alistair Moffat and Justin Zobel},
  title   = {A Similarity Measure for Indefinite Rankings},
  journal = {{ACM} Transactions on Information Systems},
  volume  = {28},
  number  = {4},
  year    = {2010},
  pages   = {20:1--20:38}
}

@inproceedings{montague2001normalization,
  author    = {Mark Montague and Javed A. Aslam},
  title     = {Relevance Score Normalization for Metasearch},
  booktitle = {Proceedings of the Tenth International Conference on Information and Knowledge Management},
  year      = {2001},
  pages     = {427--433}
}

@article{luan2021sparse,
  author  = {Yi Luan and Jacob Eisenstein and Kristina Toutanova and Michael Collins},
  title   = {Sparse, Dense, and Attentional Representations for Text Retrieval},
  journal = {Transactions of the Association for Computational Linguistics},
  volume  = {9},
  year    = {2021},
  pages   = {329--345}
}

@article{nogueira2019doc2query,
  author  = {Rodrigo Nogueira and Wei Yang and Jimmy Lin and Kyunghyun Cho},
  title   = {Document Expansion by Query Prediction},
  journal = {arXiv preprint arXiv:1904.08375},
  year    = {2019}
}


@inproceedings{fox1994combination,
  author    = {Edward A. Fox and Joseph A. Shaw},
  title     = {Combination of Multiple Searches},
  booktitle = {Proceedings of the Second Text REtrieval Conference ({TREC-2})},
  year      = {1994},
  pages     = {243--252}
}

@inproceedings{lee1997analyses,
  author    = {Joon Ho Lee},
  title     = {Analyses of Multiple Evidence Combination},
  booktitle = {Proceedings of the 20th Annual International {ACM} {SIGIR} Conference on Research and Development in Information Retrieval},
  year      = {1997},
  pages     = {267--276}
}

@inproceedings{kamphuis2020bm25,
  author    = {Chris Kamphuis and Arjen P. de Vries and Leonid Boytsov and Jimmy Lin},
  title     = {Which {BM25} Do You Mean? A Large-Scale Reproducibility Study of Scoring Variants},
  booktitle = {Advances in Information Retrieval: 42nd European Conference on {IR} Research},
  year      = {2020},
  pages     = {28--34}
}

@article{cooper1998monitoring,
  author  = {Michael D. Cooper},
  title   = {Design Considerations in Instrumenting and Monitoring {Web}-Based Information Retrieval Systems},
  journal = {Journal of the American Society for Information Science},
  volume  = {49},
  number  = {10},
  year    = {1998},
  pages   = {903--919}
}

@inproceedings{wachsmuth2018arguana,
  author    = {Henning Wachsmuth and Shahbaz Syed and Benno Stein},
  title     = {Retrieval of the Best Counterargument without Prior Topic Knowledge},
  booktitle = {Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year      = {2018},
  pages     = {241--251}
}

@inproceedings{cohan2020specter,
  author    = {Arman Cohan and Sergey Feldman and Iz Beltagy and Doug Downey and Daniel Weld},
  title     = {{SPECTER}: Document-level Representation Learning using Citation-informed Transformers},
  booktitle = {Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics},
  year      = {2020},
  pages     = {2270--2282}
}

@inproceedings{maia2018fiqa,
  author    = {Macedo Maia and Siegfried Handschuh and Andr{\'e} Freitas and Brian Davis and Ross McDermott and Manel Zarrouk and Alexandra Balahur},
  title     = {{WWW'18} Open Challenge: Financial Opinion Mining and Question Answering},
  booktitle = {Companion Proceedings of The Web Conference 2018},
  year      = {2018},
  pages     = {1941--1942}
}

@article{voorhees2020treccovid,
  author  = {Ellen Voorhees and Tasmeer Alam and Steven Bedrick and Dina Demner-Fushman and William R. Hersh and Kyle Lo and Kirk Roberts and Ian Soboroff and Lucy Lu Wang},
  title   = {{TREC-COVID}: Constructing a Pandemic Information Retrieval Test Collection},
  journal = {{ACM} {SIGIR} Forum},
  volume  = {54},
  number  = {1},
  year    = {2020},
  pages   = {1--12}
}

@article{wang2022e5,
  author  = {Liang Wang and Nan Yang and Xiaolong Huang and Binxing Jiao and Linjun Yang and Daxin Jiang and Rangan Majumder and Furu Wei},
  title   = {Text Embeddings by Weakly-Supervised Contrastive Pre-training},
  journal = {arXiv preprint arXiv:2212.03533},
  year    = {2022}
}


=== results/significance.json ===

{
 "test": "paired sign-flip randomization, two-sided",
 "trials": 100000,
 "seed": 20261014,
 "correction": "Holm within each (metric, comparison) family",
 "rows": [
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": -0.034304840768956894,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": 0.034304840768956894,
   "p": 1.999980000199998e-05,
   "p_holm": 0.00027999720002799973
  },
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": -0.001422475106685633,
   "p": 0.6267537324626754,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": 0.001422475106685633,
   "p": 0.6224837751622484,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.08454100645682124,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": -0.08454100645682124,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.032005689900426744,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": -0.032005689900426744,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.033090974367015046,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": -0.033090974367015046,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0035561877667140826,
   "p": 0.22757772422275777,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1406,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_arguana__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1406,
   "mean_diff": -0.0035561877667140826,
   "p": 0.22696773032269676,
   "p_holm": 1.0
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.0586311437799321,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.010571612492843942,
   "p": 0.00015999840001599985,
   "p_holm": 0.0028799712002879974
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.048059531287088154,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.02636491166583759,
   "p": 0.0005999940000599994,
   "p_holm": 0.00959990400095999
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.0011574074074074073,
   "p": 0.5030549694503055,
   "p_holm": 1.0
  },
  {
   "tag": "beir_fiqa_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.025207504258430186,
   "p": 0.0008899911000889991,
   "p_holm": 0.014239857601423985
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.03714365746293073,
   "p": 0.0002599974000259997,
   "p_holm": 0.0031199688003119967
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.009859659169479432,
   "p": 0.0002599974000259997,
   "p_holm": 0.004419955800441995
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.027283998293451295,
   "p": 0.006569934300656994,
   "p_holm": 0.06549934500654994
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.020852929649225947,
   "p": 0.006729932700672994,
   "p_holm": 0.08748912510874891
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": 0.00020576131687242793,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_fiqa_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.021058690966098376,
   "p": 0.005449945500544995,
   "p_holm": 0.08174918250817492
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.04677197143742044,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.009871179265294966,
   "p": 0.0002599974000259997,
   "p_holm": 0.004419955800441995
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.03690079217212548,
   "p": 7.999920000799993e-05,
   "p_holm": 0.001039989600103999
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 648,
   "mean_diff": -0.006987923770331178,
   "p": 0.3980860191398086,
   "p_holm": 1.0
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 648,
   "mean_diff": 0.00038580246913580245,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 648,
   "mean_diff": 0.007373726239466981,
   "p": 0.3715462845371546,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": -0.011532873328449371,
   "p": 0.12168878311216888,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.007543164341381242,
   "p": 0.028199718002819972,
   "p_holm": 0.2537974620253797
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": 0.01907603766983061,
   "p": 0.0033899661003389966,
   "p_holm": 0.03728962710372896
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.0005875487240621439,
   "p": 0.8989310106898931,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.004655081340794877,
   "p": 0.0005099949000509995,
   "p_holm": 0.008159918400815992
  },
  {
   "tag": "beir_nfcorpus_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": 0.004067532616732734,
   "p": 0.35009649903500967,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": -0.0031260467074473303,
   "p": 0.6282037179628204,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.01279326387640751,
   "p": 0.0015699843001569984,
   "p_holm": 0.021979780202197978
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": 0.01591931058385484,
   "p": 0.0027999720002799973,
   "p_holm": 0.033599664003359966
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.00930590856372043,
   "p": 0.01935980640193598,
   "p_holm": 0.2323176768232318
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.004099704192461676,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_nfcorpus_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": -0.005206204371258753,
   "p": 0.17299827001729984,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": -0.0028215680992977697,
   "p": 0.6997230027699723,
   "p_holm": 1.0
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.01327446980597156,
   "p": 0.0013499865001349986,
   "p_holm": 0.020249797502024977
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": 0.01609603790526933,
   "p": 0.0065499345006549935,
   "p_holm": 0.06549934500654994
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.011118752926355592,
   "p": 0.005919940800591994,
   "p_holm": 0.08287917120828792
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 323,
   "mean_diff": 0.005378549646179727,
   "p": 1.999980000199998e-05,
   "p_holm": 0.00033999660003399966
  },
  {
   "tag": "beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 323,
   "mean_diff": -0.0057402032801758636,
   "p": 0.12829871701282988,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.022225856378005556,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.0016614736341565837,
   "p": 0.005909940900590994,
   "p_holm": 0.06500934990650094
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": 0.020564382743848975,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.027133333333333332,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.0002,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": 0.026933333333333333,
   "p": 9.99990000099999e-06,
   "p_holm": 0.00017999820001799984
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.0036879533960772534,
   "p": 0.32789672103278966,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.0007708149566843002,
   "p": 0.16124838751612483,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": 0.0029171384393929536,
   "p": 0.43736562634373655,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": 0.003666666666666667,
   "p": 0.34977650223497764,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": -0.0036666666666666666,
   "p": 0.34707652923470766,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": -0.005047872875165261,
   "p": 0.16834831651683482,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": -3.195772406813801e-05,
   "p": 0.9498905010949891,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": 0.005015915151097124,
   "p": 0.17117828821711784,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 1000,
   "mean_diff": 0.0055499999999999985,
   "p": 0.15625843741562584,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 1000,
   "mean_diff": 0.0002,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scidocs__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 1000,
   "mean_diff": -0.00535,
   "p": 0.17399826001739982,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": -0.017168395566541962,
   "p": 0.22506774932250678,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0009297731841396672,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": 0.01809816875068163,
   "p": 0.2042979570204298,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.002666666666666667,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": -0.002666666666666667,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.006707368882750133,
   "p": 0.6372536274637254,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0021931892411735463,
   "p": 0.4970850291497085,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": -0.0045141796415765845,
   "p": 0.7497625023749762,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": -0.0033333333333333335,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": 0.0033333333333333335,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.004335396123716067,
   "p": 0.7610123898761012,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0016703438671287186,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": -0.002665052256587351,
   "p": 0.8516714832851672,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.03,
   "p": 0.035219647803521964,
   "p_holm": 0.38741612583874163
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 300,
   "mean_diff": 0.0,
   "p": 1.0,
   "p_holm": 1.0
  },
  {
   "tag": "beir_scifact_test__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 300,
   "mean_diff": -0.03,
   "p": 0.03535964640353596,
   "p_holm": 0.4596754032459675
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.016416375517160714,
   "p": 0.4181658183418166,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.035183284678146805,
   "p": 0.003299967000329997,
   "p_holm": 0.04289957100428996
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": -0.018766909160986098,
   "p": 0.42304576954230455,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.008093658850869281,
   "p": 0.05047949520504795,
   "p_holm": 0.5047949520504795
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.0007379330746610235,
   "p": 0.17021829781702183,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__BAAI_bge-base-en-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": 0.007355725776208257,
   "p": 0.08386916130838691,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": 0.017659453713883513,
   "p": 0.4382756172438276,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.02744745328339488,
   "p": 0.023499765002349977,
   "p_holm": 0.23499765002349976
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": -0.045106906997278394,
   "p": 0.06993930060699392,
   "p_holm": 0.5595144048559514
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.0037713866484167745,
   "p": 0.32721672783272165,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.0008997209555409232,
   "p": 0.26834731652683474,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__intfloat_e5-base-v2",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": 0.002871665692875852,
   "p": 0.4699253007469925,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.054482796060498294,
   "p": 0.018769812301876982,
   "p_holm": 0.2064679353206468
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.0394732093411543,
   "p": 0.004819951800481995,
   "p_holm": 0.05783942160578394
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "ndcg_cut_10",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": 0.015009586719344003,
   "p": 0.5519844801551984,
   "p_holm": 1.0
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_or",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.012753353355433119,
   "p": 0.0023399766002339976,
   "p_holm": 0.03509964900350997
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "dense",
   "n": 50,
   "mean_diff": -0.0015638326235496126,
   "p": 0.024239757602423976,
   "p_holm": 0.36359636403635964
  },
  {
   "tag": "beir_trec-covid__nomic-ai_nomic-embed-text-v1.5",
   "metric": "recall_100",
   "a": "hybrid_and",
   "b": "hybrid_or",
   "n": 50,
   "mean_diff": 0.011189520731883507,
   "p": 0.01033989660103399,
   "p_holm": 0.14475855241447586
  }
 ]
}


=== results/keyword_facts.json ===

[
 {
  "dataset": "beir/scifact/test",
  "n_queries": 300,
  "tokens_mean": 12.626666666666667,
  "tokens_median": 12.0,
  "kept_tokens_mean": 8.733333333333333,
  "and_empty": 294,
  "and_rows_1_3": 6,
  "and_rows_4_plus": 0,
  "and_returns_query_itself": 0,
  "and_query_itself_at_rank_1": 0,
  "and_returns_query_text": 0,
  "and_any_relevant_hit": 6,
  "query_id_is_doc_id": 0
 },
 {
  "dataset": "beir/nfcorpus/test",
  "n_queries": 323,
  "tokens_mean": 3.303405572755418,
  "tokens_median": 2,
  "kept_tokens_mean": 2.513931888544892,
  "and_empty": 164,
  "and_rows_1_3": 73,
  "and_rows_4_plus": 86,
  "and_returns_query_itself": 0,
  "and_query_itself_at_rank_1": 0,
  "and_returns_query_text": 0,
  "and_any_relevant_hit": 123,
  "query_id_is_doc_id": 0
 },
 {
  "dataset": "beir/arguana",
  "n_queries": 1406,
  "tokens_mean": 195.13869132290185,
  "tokens_median": 176.0,
  "kept_tokens_mean": 106.08108108108108,
  "and_empty": 0,
  "and_rows_1_3": 1406,
  "and_rows_4_plus": 0,
  "and_returns_query_itself": 1298,
  "and_query_itself_at_rank_1": 1296,
  "and_returns_query_text": 1406,
  "and_any_relevant_hit": 1,
  "query_id_is_doc_id": 1298
 },
 {
  "dataset": "beir/scidocs",
  "n_queries": 1000,
  "tokens_mean": 9.423,
  "tokens_median": 9.0,
  "kept_tokens_mean": 7.287,
  "and_empty": 942,
  "and_rows_1_3": 46,
  "and_rows_4_plus": 12,
  "and_returns_query_itself": 0,
  "and_query_itself_at_rank_1": 0,
  "and_returns_query_text": 0,
  "and_any_relevant_hit": 10,
  "query_id_is_doc_id": 0
 },
 {
  "dataset": "beir/fiqa/test",
  "n_queries": 648,
  "tokens_mean": 11.064814814814815,
  "tokens_median": 11.0,
  "kept_tokens_mean": 6.177469135802469,
  "and_empty": 530,
  "and_rows_1_3": 73,
  "and_rows_4_plus": 45,
  "and_returns_query_itself": 0,
  "and_query_itself_at_rank_1": 0,
  "and_returns_query_text": 0,
  "and_any_relevant_hit": 19,
  "query_id_is_doc_id": 55
 },
 {
  "dataset": "beir/trec-covid",
  "n_queries": 50,
  "tokens_mean": 10.6,
  "tokens_median": 10.0,
  "kept_tokens_mean": 5.68,
  "and_empty": 37,
  "and_rows_1_3": 6,
  "and_rows_4_plus": 7,
  "and_returns_query_itself": 0,
  "and_query_itself_at_rank_1": 0,
  "and_returns_query_text": 0,
  "and_any_relevant_hit": 12,
  "query_id_is_doc_id": 0
 }
]


=== results/natural_lengths.json ===

{
 "pooled_without": "beir_arguana",
 "buckets": [
  {
   "n_keyword": "1-3",
   "fired": 137,
   "total": 726,
   "rate": 0.1887052341597796
  },
  {
   "n_keyword": "4-49",
   "fired": 35,
   "total": 588,
   "rate": 0.05952380952380952
  },
  {
   "n_keyword": "50-100",
   "fired": 4,
   "total": 6636,
   "rate": 0.0006027727546714888
  }
 ],
 "by_collection": {
  "beir_arguana": {
   "1-3": {
    "fired": 0,
    "total": 4218
   },
   "50-100": {
    "fired": 0,
    "total": 4218
   }
  },
  "beir_fiqa_test": {
   "1-3": {
    "fired": 90,
    "total": 219
   },
   "4-49": {
    "fired": 25,
    "total": 105
   },
   "50-100": {
    "fired": 4,
    "total": 1974
   }
  },
  "beir_nfcorpus_test": {
   "1-3": {
    "fired": 13,
    "total": 330
   },
   "50-100": {
    "fired": 0,
    "total": 627
   },
   "4-49": {
    "fired": 0,
    "total": 414
   }
  },
  "beir_scidocs": {
   "1-3": {
    "fired": 18,
    "total": 141
   },
   "4-49": {
    "fired": 3,
    "total": 42
   },
   "50-100": {
    "fired": 0,
    "total": 2991
   }
  },
  "beir_scifact_test": {
   "1-3": {
    "fired": 0,
    "total": 18
   },
   "50-100": {
    "fired": 0,
    "total": 891
   },
   "4-49": {
    "fired": 0,
    "total": 9
   }
  },
  "beir_trec-covid": {
   "4-49": {
    "fired": 7,
    "total": 18
   },
   "1-3": {
    "fired": 16,
    "total": 18
   },
   "50-100": {
    "fired": 0,
    "total": 153
   }
  }
 }
}


=== results/beir_arguana__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/arguana",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0007112375533428165,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 34.457427674968635
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.4733200193151377,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 905.4240860320114
  },
  "bm25_or": {
   "ndcg_cut_10": 0.48360519237538113,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 51.5130756500733
  },
  "dense": {
   "ndcg_cut_10": 0.6405549400621677,
   "recall_100": 0.9928876244665719,
   "mean_query_ms": 0.8329619523429002
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.6405549400621677,
   "recall_100": 0.9928876244665719,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 74.06509695021072
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.6062500992932108,
   "recall_100": 0.9914651493598862,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 38.578947368421055,
   "mean_query_ms": 91.77292985704439
  }
 }
}


=== results/beir_arguana__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/arguana",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0007112375533428165,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 36.093606991466935
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.4733200193151377,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 914.1127244523553
  },
  "bm25_or": {
   "ndcg_cut_10": 0.48360519237538113,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 52.96692121763389
  },
  "dense": {
   "ndcg_cut_10": 0.4470590457213425,
   "recall_100": 0.9487908961593172,
   "mean_query_ms": 0.8331361479168207
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.4470590457213425,
   "recall_100": 0.9487908961593172,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 75.28825145304882
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.5316000521781638,
   "recall_100": 0.980796586059744,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 33.49644381223329,
   "mean_query_ms": 93.66321482504121
  }
 }
}


=== results/beir_arguana__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/arguana",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0007112375533428165,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 36.28502304124898
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.4733200193151377,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 907.5259179829343
  },
  "bm25_or": {
   "ndcg_cut_10": 0.48360519237538113,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 52.181358220491056
  },
  "dense": {
   "ndcg_cut_10": 0.4834407167619483,
   "recall_100": 0.9800853485064012,
   "mean_query_ms": 0.8899592204748896
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.4834407167619483,
   "recall_100": 0.9800853485064012,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 74.285679776691
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.5165316911289634,
   "recall_100": 0.9836415362731152,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 43.66216216216216,
   "mean_query_ms": 92.56313039402652
  }
 }
}


=== results/beir_fiqa_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.8281378719355774
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 103.59331025468539
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 18.55196859111104
  },
  "dense": {
   "ndcg_cut_10": 0.406231202203102,
   "recall_100": 0.7414716927448408,
   "mean_query_ms": 7.131569859554059
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.39565958971025805,
   "recall_100": 0.7403142853374335,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.8719135802469136,
   "multi_leg_docs_mean": 0.4382716049382716,
   "mean_query_ms": 15.745104404307616
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.34760005842316993,
   "recall_100": 0.7151067810790034,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0030864197530864196,
   "multi_leg_docs_mean": 22.057098765432098,
   "mean_query_ms": 43.25730130248314
  }
 }
}


=== results/beir_fiqa_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.8451425602269644
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 104.67865806944482
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 18.494731922887528
  },
  "dense": {
   "ndcg_cut_10": 0.3986663557596119,
   "recall_100": 0.732044310285051,
   "mean_query_ms": 7.159476040133535
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3888066965901325,
   "recall_100": 0.7322500716019235,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.8842592592592593,
   "multi_leg_docs_mean": 0.35648148148148145,
   "mean_query_ms": 15.592786748390642
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3615226982966812,
   "recall_100": 0.7111913806358251,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0030864197530864196,
   "multi_leg_docs_mean": 19.03858024691358,
   "mean_query_ms": 43.2826817144573
  }
 }
}


=== results/beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.8494726990713253
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 103.91837222839878
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 18.683119256130105
  },
  "dense": {
   "ndcg_cut_10": 0.37647587524591536,
   "recall_100": 0.6816969381784197,
   "mean_query_ms": 7.182668663596287
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.36660469598062045,
   "recall_100": 0.6820827406475555,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.875,
   "multi_leg_docs_mean": 0.44907407407407407,
   "mean_query_ms": 15.665220367301668
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.32970390380849496,
   "recall_100": 0.6747090144080885,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 24.07253086419753,
   "mean_query_ms": 43.11616507874656
  }
 }
}


=== results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.19634378637650907
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.604910040239865
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 1.1970306842100884
  },
  "dense": {
   "ndcg_cut_10": 0.3743755691751346,
   "recall_100": 0.3367217011621948,
   "mean_query_ms": 0.4304284148667716
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.38191873351651584,
   "recall_100": 0.34137678250298964,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5170278637770898,
   "multi_leg_docs_mean": 4.006191950464396,
   "mean_query_ms": 1.0279896811054032
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.36284269584668527,
   "recall_100": 0.33730924988625693,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.08668730650154799,
   "multi_leg_docs_mean": 21.328173374613,
   "mean_query_ms": 2.6499623250735453
  }
 }
}


=== results/beir_nfcorpus_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.20907633435837328
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.7272139690313697
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 1.0739804891641664
  },
  "dense": {
   "ndcg_cut_10": 0.35510251404870363,
   "recall_100": 0.3185760067364094,
   "mean_query_ms": 0.41033316097479655
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3678957779251112,
   "recall_100": 0.3226757109288711,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5139318885448917,
   "multi_leg_docs_mean": 3.7863777089783284,
   "mean_query_ms": 1.0421005975172264
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3519764673412563,
   "recall_100": 0.32788191530012983,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.07739938080495357,
   "multi_leg_docs_mean": 20.563467492260063,
   "mean_query_ms": 2.6343234829757995
  }
 }
}


=== results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.2243764458255196
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.698692037150183
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 1.103532777093678
  },
  "dense": {
   "ndcg_cut_10": 0.3472922048732708,
   "recall_100": 0.2976659245321355,
   "mean_query_ms": 0.42659790092372024
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.36056667467924236,
   "recall_100": 0.3030444741783152,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5170278637770898,
   "multi_leg_docs_mean": 3.7058823529411766,
   "mean_query_ms": 1.047801065021723
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.344470636773973,
   "recall_100": 0.3087846774584911,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.08359133126934984,
   "multi_leg_docs_mean": 20.993808049535605,
   "mean_query_ms": 2.699557334360683
  }
 }
}


=== results/beir_scidocs__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/scidocs",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 1.0329977360170233
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 41.89922915100669
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 12.60673530101576
  },
  "dense": {
   "ndcg_cut_10": 0.2172458820187077,
   "recall_100": 0.49568333333333336,
   "mean_query_ms": 3.097026601003563
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.21558440838455112,
   "recall_100": 0.49548333333333333,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.949,
   "multi_leg_docs_mean": 0.131,
   "mean_query_ms": 5.601762678999876
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.19502002564070217,
   "recall_100": 0.46855,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 29.253,
   "mean_query_ms": 27.606898035000995
  }
 }
}


=== results/beir_scidocs__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/scidocs",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 1.1023498850045144
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 42.32073675904758
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 12.935040366979592
  },
  "dense": {
   "ndcg_cut_10": 0.18681165035878386,
   "recall_100": 0.42086666666666667,
   "mean_query_ms": 3.157666159020664
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.18604083540209956,
   "recall_100": 0.42086666666666667,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.947,
   "multi_leg_docs_mean": 0.146,
   "mean_query_ms": 5.5536601259955205
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.18312369696270658,
   "recall_100": 0.4245333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 31.686,
   "mean_query_ms": 27.77016292202461
  }
 }
}


=== results/beir_scidocs__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/scidocs",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 1.0807826060081425
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 42.2408295550149
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 12.700958016988807
  },
  "dense": {
   "ndcg_cut_10": 0.18720982971345648,
   "recall_100": 0.40351666666666663,
   "mean_query_ms": 3.115459200002988
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.18717787198938834,
   "recall_100": 0.4037166666666667,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.948,
   "multi_leg_docs_mean": 0.165,
   "mean_query_ms": 5.5899801190025755
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.18216195683829123,
   "recall_100": 0.4090666666666667,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 32.335,
   "mean_query_ms": 27.58528369699434
  }
 }
}


=== results/beir_scifact_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/scifact/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.49118353333559145
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 13.595297593333271
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 4.130055509995145
  },
  "dense": {
   "ndcg_cut_10": 0.740391287918679,
   "recall_100": 0.9666666666666667,
   "mean_query_ms": 0.5337012466634405
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7413210611028186,
   "recall_100": 0.9666666666666667,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 1.6933436833327657
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.723222892352137,
   "recall_100": 0.9693333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 28.923333333333332,
   "mean_query_ms": 7.798421146666972
  }
 }
}


=== results/beir_scifact_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/scifact/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.5286559500026063
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 14.621643430000782
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 3.756217093335484
  },
  "dense": {
   "ndcg_cut_10": 0.7194288840281022,
   "recall_100": 0.9626666666666667,
   "mean_query_ms": 0.5170211533288693
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7216220732692757,
   "recall_100": 0.9626666666666667,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 1.669976179994516
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7261362529108524,
   "recall_100": 0.9593333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 27.88,
   "mean_query_ms": 7.95921461333478
  }
 }
}


=== results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/scifact/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.5511385300007987
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 13.770269963332188
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 3.947254483330577
  },
  "dense": {
   "ndcg_cut_10": 0.703264558006416,
   "recall_100": 0.9283333333333333,
   "mean_query_ms": 0.5722580966687474
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7049349018735447,
   "recall_100": 0.9283333333333333,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 1.7764524400013215
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.707599954130132,
   "recall_100": 0.9583333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 25.9,
   "mean_query_ms": 8.606827753333542
  }
 }
}


=== results/beir_trec-covid__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/trec-covid",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 15.639846579942969
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 352.5785985801849
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 110.23678433997702
  },
  "dense": {
   "ndcg_cut_10": 0.7794198743263,
   "recall_100": 0.1406060337521087,
   "mean_query_ms": 21.298244100034935
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7442365896481532,
   "recall_100": 0.1398681006774477,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.9,
   "multi_leg_docs_mean": 0.86,
   "mean_query_ms": 53.75930489975872
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7630034988091393,
   "recall_100": 0.13251237490123943,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 21.62,
   "mean_query_ms": 199.54773687986744
  }
 }
}


=== results/beir_trec-covid__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/trec-covid",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 13.445708319995902
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 305.9090719998494
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 93.74320860006264
  },
  "dense": {
   "ndcg_cut_10": 0.6964665036183234,
   "recall_100": 0.12825429859351073,
   "mean_query_ms": 19.883966140114353
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.6690190503349285,
   "recall_100": 0.12735457763796978,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.9,
   "multi_leg_docs_mean": 0.78,
   "mean_query_ms": 46.852595459713484
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7141259573322069,
   "recall_100": 0.12448291194509395,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 19.64,
   "mean_query_ms": 180.25273754006776
  }
 }
}


=== results/beir_trec-covid__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/trec-covid",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "ignore_identical_ids": true,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 13.574454100089497
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 311.5806790001807
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 96.6492606200336
  },
  "dense": {
   "ndcg_cut_10": 0.8233852502363679,
   "recall_100": 0.14969146695405253,
   "mean_query_ms": 19.807920739840483
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7839120408952137,
   "recall_100": 0.1481276343305029,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.88,
   "multi_leg_docs_mean": 0.7,
   "mean_query_ms": 47.575508559748414
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7689024541758697,
   "recall_100": 0.1369381135986194,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 21.9,
   "mean_query_ms": 181.2533663195063
  }
 }
}
