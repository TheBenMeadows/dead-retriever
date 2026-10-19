# Review: dead-retriever paper, journal draft — round 4

You are reviewing a paper about to be submitted to the Information Retrieval Research Journal (IRRJ; single-blind, normal papers are "about 20 pages", SIGIR/ECIR-like). An earlier 10-page version went through three review rounds (nine reviews) that settled the thesis: the 1/k ceiling in reciprocal rank fusion detects zero overlap between retrievers, not an empty retriever. That version is on Zenodo and pending at arXiv. For the journal the reproduction was expanded from 2 BEIR collections and 2 encoders to 6 collections (SciFact, NFCorpus, ArguAna, SciDocs, FiQA, TREC-COVID) and 3 encoders (bge-base-en-v1.5, nomic-embed-text-v1.5, e5-base-v2), 22,362 hybrid query runs. Section 6, the abstract, the limitations, the operator advice and both appendices were rewritten on the new data and have not been reviewed by anyone. The new data overturned two claims of the old version (no ceiling over a keyword leg of 4+ documents; the K > k leak never observed) and added a blind spot (ArguAna, where the buggy leg returns the query's own text). Answer as the one careful reviewer whose job is to stop the author from submitting something wrong. Formulas, section names and quoted phrases over adjectives; no compliments; do not restate the paper. Under 1200 words.

## What to do

1. **Read the whole paper once as a journal referee would** and name anything that would get it rejected or embarrass the author: a false sentence, a number that does not follow from the tables or the JSON below, a claim wider than the evidence, a citation that does not say what it is cited for, an inconsistency between sections (Sections 1 to 5 were not rewritten; check they still agree with the new Section 6).
2. **Section 6 numbers.** Spot-check the prose figures against the inline result files: the legs table, the AND-empty counts, the content-token ordering, the ArguAna counts, the excess-ceiling counts and percentages, the natural row-count rates, the effectiveness counts (5 of 18, 9 of 18, 12 of 18) and the named gains and losses. Quote any figure you cannot reproduce.
3. **Interpretation.** Are these stated no wider than the evidence: (a) the empty rate ordered by content tokens per query across five collections; (b) short-list disjointness growing with corpus size; (c) the ArguAna self-match generalising to real systems that index the text they are queried with; (d) "a monitor for leg health and a verdict on retrieval effectiveness are different instruments"?
4. **Journal fit.** What would an IRRJ referee ask for that the paper lacks, ranked by how likely it is to decide acceptance (for example significance tests on the effectiveness comparisons, a section structure, related work depth, a figure)? One sentence each, and say which you would require and which are optional. No new experiments unless one is essential.
5. **Abstract and title.** Do they claim exactly what the body shows, no more?

## Attached (inline below; do not use any tool: do not read files, run commands, or fetch URLs; answer in your final message)

- `paper/main.tex` — the paper (IRRJ LaTeX style).
- `paper/refs.bib` — the bibliography (every entry was checked against Crossref, arXiv or the publisher listing; flag only if you know one to be wrong).
- `results/keyword_facts.json` — encoder-free facts per collection (query tokens, content tokens, what the quoted-AND leg returns).
- `results/natural_lengths.json` — ceiling firing rate by the keyword leg's natural row count.
- `results/beir_<collection>__<encoder>.json` — the 18 summary files (six conditions each: nDCG@10, Recall@100, keyword-empty rate, at-ceiling rate, mean shared documents, mean query ms). Per-query rows are too large to inline; the audit script checks the per-query figures against them, and the author will verify any count you dispute.


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
\ShortHeadings{A Score Ceiling in Reciprocal Rank Fusion Detects Zero Overlap}{Meadows}
\firstpageno{1}

\begin{document}

\title{A Score Ceiling in Reciprocal Rank Fusion\\Detects Zero Overlap, and Found a Dead Retriever}

\author{\name Benjamin Meadows \email ben@benjaminmeadows.com \\
       \addr Independent Researcher\\
       ORCID 0009-0007-9698-0910}

\editor{-}

\maketitle

\begin{abstract}%
A hybrid search system fuses a keyword retriever and a vector retriever with reciprocal rank fusion (RRF). In the system described here, the keyword retriever returned no results for most natural-language queries from the system's first version until 2026-08-18, and nobody noticed: the vector retriever always filled the result list, and the usual spot checks used short keyword queries, which still matched. The failure was visible the whole time in the fused scores. RRF credits a document $1/(k+r)$ from each retriever that ranks it at position $r$, so with per-retriever depth $K \le k$ a document found by two retrievers scores above $1/k$ and a document found by one scores at most $1/k$. A result list whose maximum fused score is $1/k$ therefore contains no document that both retrievers returned. That is a statement about overlap, not about either retriever: two working retrievers can return disjoint lists, and in the incident four of ten queries did. I give the derivation and its limits, the bug (quoting every token of an SQLite FTS5 query, which FTS5 reads as an implicit AND), before-and-after aggregates from the production system, two negative results measured beside the dead leg, and a reproduction on six BEIR collections with three encoders, 22\,362 hybrid query runs. The buggy builder returns nothing for 50.8 to 98.0\% of queries on five collections, in the order of their content words per query, and the ceiling missed none of those empty legs. Where the two disagree, the ceiling fired over a live leg that shared nothing with the vector leg in 174 runs, mostly short lists on large corpora, and with one shared document deep in both lists in two, the case depth $K > k$ leaves open. On the sixth collection, whose queries are themselves corpus documents, the buggy leg is never empty and never useful: it returns the query's own text, the vector leg agrees, and the ceiling never fires. Repairing the leg restores overlap on every collection and improves nDCG@10 over the vector retriever alone in 5 of 18 collection--encoder pairs. Code, results, per-query diagnostics and this paper's source are at \url{https://github.com/TheBenMeadows/dead-retriever}.
\end{abstract}

\begin{keywords}
  reciprocal rank fusion, hybrid retrieval, rank fusion diagnostics, SQLite FTS5, BM25, dense retrieval
\end{keywords}

\section{The incident}

The system is a personal search engine over about 30\,000 to 217\,000 text chunks per corpus, split across five SQLite databases that share one retrieval module. Each query runs two retrievers over the same chunks: an SQLite FTS5 index ranked by BM25 \citep{robertson2009bm25,sqlite_fts5}, and a 768-dimensional embedding index searched by exact cosine. The two ranked lists, each cut at depth $K=60$, are fused with reciprocal rank fusion at $k=60$ \citep{cormack2009rrf}.

On 2026-08-07 a recency-decay feature was evaluated and rejected because RRF scores were ``flat near the top'': adjacent ranks differed by about 1.4\%, so even a 5\% age multiplier acted as a strong reranker rather than a tie-break. That flatness was recorded as a property of fusion. On 2026-08-18, while investigating why the keyword side rarely seemed to matter, I logged the keyword retriever's row counts for ten real queries. Five of five conversational queries matched zero chunks, as did a two-word place-name query. Only queries of two or three technical tokens matched anything. The keyword retriever had been inert on prose queries since the system was built, and all four sibling engines carried the same line of code.

The fused scores had said so from the start. Over the top 100 fused results of those ten queries, the maximum score was exactly $1/60 = 0.01\overline{6}$. The values were $1/60, 1/61, 1/62, \ldots$ with gaps where per-file deduplication removed a chunk: every fused score was a single term $1/(k+r)$, so no document had been credited by both retrievers. The ``1.4\% flatness'' was misread twice. Between consecutive singleton scores it is the relative step of the formula, $\bigl(1/(k+r) - 1/(k+r+1)\bigr) / \bigl(1/(k+r)\bigr) = 1/(k+r+1)$, 1.6\% at the top of the list and 1.4\% around rank 10, and two live lists that agreed on every document would show the same step at twice the scale. What marked the incident was not the step but the scale: nothing scored above $1/60$.

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

Three qualifications bound what that means in practice. First, it is a statement about overlap. Two retrievers that both return $K$ documents and share none of them produce the same ceiling as one retriever and one empty list, and so does a keyword leg that returns one or two documents the vector leg did not; with more retrievers, any number of pairwise-disjoint live lists do too. In the incident, the keyword leg returned rows on four of the ten queries and the ceiling held on all ten (Table~\ref{tab:prod}); those four were lists of one to three chunks, with nothing in common with the vector top 60. The ceiling says no document was reinforced by agreement; the per-retriever row counts say whether that is because a leg is empty, nearly empty, or live and disjoint, and a system that fuses should log both. Second, the equivalence needs $K \le k$. One direction survives at any depth: a maximum above $1/k$ proves that some document was returned by two retrievers, since a singleton scores at most $1/k$ for every $K$. The other does not. With $K > k$, a document ranked deep in both lists scores below $1/k$ (rank 90 in both at $k=60$ gives $2/150$), and one ranked exactly $k$ in both scores exactly $1/k$; two ranks $r_1, r_2$ combine to more than $1/k$ exactly when $r_1 r_2 < k^2$. So at $K > k$ a maximum of $1/k$ shows that every retriever's rank-0 document is exclusive and leaves deeper overlap open, and a system that keeps per-retriever ranks should count shared documents directly. Section~\ref{sec:beir}, which uses $K = 100 > k$, reports both and measures how often the two disagree. Third, with two retrievers an empty leg always produces the ceiling when the other leg returned anything, so the test cannot miss one and everything it gets wrong is in the other direction; with three or more, an empty leg can hide behind two live legs that overlap. The equivalence itself holds for any $L$. The one-based RRF of \citet{cormack2009rrf} shifts every figure by one: the singleton ceiling is $1/(k+1)$, and strict separation holds for $K \le k+1$. Throughout, the scores compared are the unweighted RRF sums before any downstream filtering or rescaling, and ``at the ceiling'' means $\max_d s(d) \le 1/k + 10^{-12}$.

\section{The bug}

The keyword query builder was
\begin{verbatim}
fq = " ".join(f'"{t}"' for t in tokens)
\end{verbatim}
which, for the query \emph{how do I fix the empty feed}, produced
\begin{verbatim}
"how" "do" "i" "fix" "the" "empty" "feed"
\end{verbatim}
FTS5 reads a sequence of phrases separated by whitespace as an implicit AND \citep[\S 3]{sqlite_fts5}: every phrase must occur in the same row. Rows here were 1\,400-character chunks, so a six-token conversational query almost never matched. Two further details made the constraint stricter than ``every token present''. The tokeniser kept hyphens, dots and some punctuation inside a token, and FTS5's own tokeniser splits on them, so a token such as \texttt{il-6} became a two-word phrase, an adjacency constraint. And an FTS5 syntax error was caught and ignored, so a malformed query also returned nothing without a trace. Two- or three-token technical queries did match, which is why spot checks during development passed, and the vector retriever returns $K$ documents whenever the corpus has that many, so result lists were always full.

The fix has two parts, and the second is not cosmetic. Tokens are joined with \verb|OR| and ranked by BM25; a raw OR over all tokens matched about 100\,000 chunks and cost 161\,ms per query, so stopwords and tokens shorter than three characters are dropped first, after which a typical query matches about 3\,500 chunks in 2 to 4\,ms. If a query is all stopwords, the raw tokens are used. Section~\ref{sec:beir} measures both variants on public data.

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
Maximum fused score over the top 100 results & $1/60 = 0.0167$ & 0.025 -- 0.033 \\
Keyword leg latency, conversational queries & -- & 2 -- 4\,ms \\
\bottomrule
\end{tabular}
\caption{The keyword leg before and after the fix, ten real queries, one production shard, $K = k = 60$. The ``before'' latency is omitted because a query that matches nothing is fast; a raw OR without the stopword drop took 161\,ms. On the four ``before'' queries where the leg returned rows, it returned one to three chunks, none shared with the vector top 60.}
\label{tab:prod}
\end{table}

The same builder was present at a different line number in four sibling engines over four other corpora, each inert on prose queries in the same way; the five have since been merged into one module.

\section{Two negative results measured beside the dead leg}

Both of the following were measured on the same system before the keyword leg was fixed, with seven to fifteen queries each; both verdicts stand on their own terms, and neither says anything about the techniques in general.

\paragraph{Recency decay.} A multiplicative age penalty on fused scores (floor 0.85, time constant 180 days) changed the top-1 result on 4 of 7 real queries on a notes corpus, and the changes were as often wrong as right; a canonical note unedited for 338 days was demoted under a 13-day-old draft. On a second corpus spanning only 63 days the multiplier varied between 0.956 and 1.000 across every document and changed 0 of 8 top-1 results. The feature was rejected. At the time the sensitivity was attributed to flat fused scores; Section~1 shows the relative step between consecutive singleton scores is a property of the formula, and two identical live lists would show the same step, so the flatness said nothing about the leg, and whether decay would behave differently over a fused list with real two-leg scores was not tested.

\paragraph{A title prefix before embedding.} Prepending \texttt{kind: title} to each chunk before embedding (the stored text and the keyword index unchanged, so the vector was the only variable) and re-embedding one corpus of 3\,046 documents and 30\,734 chunks took 25 minutes. On 15 realistic queries, 13 had an identical top-1, mean top-5 overlap was 80\%, one query improved and one regressed, and the query predicted to benefit most returned an identical, still wrong, top 3. The change was not adopted. This is a heading prefix, the cheapest form of document expansion \citep{nogueira2019doc2query}, not the model-written situating context of \citet{anthropic2024contextual}, and the corpus was a weak test (documents whose title is their opening line). Because the keyword leg was inert, the A/B measured the vector change alone, which was the intent.

\section{Reproduction on public collections}
\label{sec:beir}

To check that the effect is a property of the query builder and not of one private corpus, I ran six retrieval conditions on six BEIR collections \citep{thakur2021beir} with three encoders. The collections are SciFact \citep{wadden2020scifact} (claim sentences against scientific abstracts), NFCorpus \citep{boteva2016nfcorpus} (short nutrition titles against medical documents), ArguAna \citep{wachsmuth2018arguana} (whole arguments against counter-arguments), SciDocs \citep{cohan2020specter} (paper titles against abstracts), FiQA \citep{maia2018fiqa} (finance questions against forum posts) and TREC-COVID \citep{voorhees2020treccovid} (COVID-19 questions against CORD-19 abstracts); Table~\ref{tab:legs} gives their sizes. They differ in domain, corpus size and relevance style as well as in query length, so contrasts between them are suggestive, not controlled. The encoders are \texttt{nomic-embed-text-v1.5} \citep{nussbaum2024nomic}, the public release of the production encoder, \texttt{bge-base-en-v1.5} \citep{xiao2023cpack} and \texttt{e5-base-v2} \citep{wang2022e5}, all 768-dimensional, each with the prefixes its model card prescribes (Appendix~\ref{app:run}). Data came through \texttt{ir\_datasets} \citep{macavaney2021irdatasets} and metrics through \texttt{pytrec\_eval} \citep{vangysel2018pytrec}. Depth $K = 100$, $k = 60$, so the ceiling is read in its weak form and overlap is also counted directly from the ranks.

The conditions are \textsc{bm25-and} (the buggy builder), \textsc{bm25-or-raw} (OR over every token), \textsc{bm25-or} (the fix: OR over non-stopword tokens), \textsc{dense}, \textsc{hybrid-and} (dense + buggy keyword, RRF) and \textsc{hybrid-or} (dense + fixed keyword, RRF). For each hybrid condition the runner writes, per query, whether the keyword leg returned nothing, how many documents it returned, whether the maximum fused score sat at $1/k$, the maximum itself, and how many documents both legs credited. The 18 collection--encoder pairs give 22\,362 hybrid query runs. Whether the keyword leg is alive and overlapping with the dense leg, and whether the hybrid retrieves better than its parts, are different questions, and the subsections below keep them apart: Table~\ref{tab:legs} is about the leg and the ceiling, Tables~\ref{tab:ndcg} and~\ref{tab:recall} about effectiveness, and every condition for every pair is in Appendix~\ref{app:full}.

\begin{table}[h]
\centering
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrrrrr}
\toprule
 & & & & \multicolumn{2}{c}{quoted AND} & \multicolumn{2}{c}{OR, stopwords dropped} \\
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

The quoted-AND builder matched nothing on 294 of SciFact's 300 claim-length queries, 942 of SciDocs's 1\,000 titles, 530 of FiQA's 648 questions, 37 of TREC-COVID's 50 questions and 164 of NFCorpus's 323 titles. Mean query length alone does not order these: NFCorpus has the shortest queries and the lowest rate, but TREC-COVID's questions are about as long as FiQA's and SciDocs's and come out lower. Counting only the tokens the fixed builder would keep (stopwords and tokens under three characters dropped) orders all five, in \texttt{results/keyword\_facts.json}: 8.7 content tokens per query on SciFact, 7.3 on SciDocs, 6.2 on FiQA, 5.7 on TREC-COVID and 2.5 on NFCorpus, against empty rates of 98.0, 94.2, 81.8, 74.0 and 50.8\%. Every quoted token must appear in one 1\,400-character chunk or one abstract, stopwords appear almost everywhere, and the content words are what run out. Five collections are too few to call this a law, and corpus size, document length and vocabulary differ along the same ordering.

BM25 with the fixed builder is a usable retriever on every collection (Appendix~\ref{app:full}), and after the fix only NFCorpus has queries that match nothing: 25 title queries (7.7\%). The stopword drop that made the fix cheap in production is cheaper everywhere and costs little effectiveness: \textsc{bm25-or-raw} is 2.6 to 18 times slower (10.2 against 3.0\,ms on SciFact and 2.1 against 0.8 on NFCorpus on one machine; 782 against 44\,ms on ArguAna, whose queries average 195 tokens, on another) and is within 0.008 nDCG@10 of \textsc{bm25-or} on five collections. The exception is FiQA, where OR over every token is better by 0.009 nDCG@10 and 0.012 Recall@100, at 5.8 times the cost. Timings compare conditions within a collection, not collections: SciFact and NFCorpus were timed on a 12-core CPU, the other four on Kaggle's GPU host, whose keyword search and fusion also run on the CPU.

\subsection{A leg that is never empty and never useful}

ArguAna's queries are whole arguments, 195 tokens on average, and the quoted-AND builder never returned nothing for them: it returned one document for 1\,402 of the 1\,406 queries and two for the other four. The reason is the collection's construction. Every query's text is also a document in the corpus, and a query is the one text guaranteed to contain all of its own tokens: on all 1\,406 queries the AND leg returned a document whose text equals the query's after whitespace and case normalisation, under the query's own identifier on 1\,298 (at rank one on 1\,296) and under another identifier on the remaining 108. A query's own document is not one of its relevant documents, and the AND leg returned a relevant document for one query in 1\,406.

The ceiling cannot see this. The dense leg also returns that document in its top 100 on every query for every encoder, so the two legs share it, the fused maximum is above $1/k$ on every query, and the ceiling never fired: Table~\ref{tab:legs} shows 0.0\% for every encoder. Fusion with this leg changed nothing measurable: \textsc{hybrid-and} and \textsc{dense} agree to the third decimal in both metrics for all three encoders, which is what a dead leg looks like from the outside. The ceiling tests for agreement, and a leg that agrees with the other leg on one useless document passes it. Per-leg row counts do not catch it either, since the leg returns a row on every query; what catches it is the distribution of row counts, one document on 99.7\% of queries, which is as much an alarm as zero. ArguAna's construction is unusual, but a corpus that indexes the queries it is searched with is not: a search engine over a mailbox, a notes vault or a ticket tracker routinely receives the text of an indexed item as a query.

\subsection{What fusion did with an empty list}

When the keyword leg is empty, the fused list is the dense list. On the 294 SciFact queries with an empty keyword leg, the per-query rows show \textsc{hybrid-and}'s list is \textsc{dense}'s list: same document count, maximum score exactly $1/60$. Over the whole collection the two conditions differ by at most 0.002 nDCG@10 and 0.000 Recall@100 for each encoder, all of it from the six live queries, and on SciDocs, with 942 empty legs, they differ by at most 0.002 and 0.000. Where the buggy leg was live on more queries the hybrid did move: on NFCorpus (159 live queries) \textsc{hybrid-and} is above \textsc{dense} by 0.008 to 0.013 nDCG@10, and on TREC-COVID (13 live queries of 50) it is below by 0.027 to 0.039.

\subsection{The ceiling against the row count}

An empty keyword leg puts the maximum fused score at exactly $1/k$ whenever the dense leg returned anything, so the set of empty-leg queries is contained in the set of at-ceiling queries, and the ceiling missed no empty leg on any of the 22\,362 hybrid query runs. Everything the two instruments disagree on is the excess, at-ceiling queries whose leg was not empty: 176 query runs, 164 under the buggy builder and 12 under the fixed one. On SciFact and ArguAna there was none. Under the buggy builder the excess is 2 or 3 of NFCorpus's 159 live-leg queries (1.3 to 1.9\%), 5 to 7 of SciDocs's 58 (8.6 to 12.1\%), 35 to 43 of FiQA's 118 (29.7 to 36.4\%) and 7 or 8 of TREC-COVID's 13 (53.8 to 61.5\%), the range running over the encoders.

In 174 of the 176 the two legs shared no document: read as a zero-overlap test the ceiling was right on them, read as an empty-leg alarm it was wrong, and the row count tells the two readings apart. The other two are the case Section~\ref{sec:ceiling} said $K > k$ leaves open. On one FiQA query for bge and one for e5, under the fixed builder, both legs returned 100 documents and shared one, ranked deep enough in both that its fused score did not exceed $1/k$; the ceiling fired with overlap present. Two in 22\,362 is rare, but it is not zero, and it is why a system that runs at $K > k$ should count shared documents directly.

How often a live list shares nothing with the dense top $K$ depends on how short it is, and on these collections also on how big the corpus is. Pooled over every collection except ArguAna, where the leg is never disjoint, the ceiling fired on 137 of the 726 live-leg query runs in which the leg returned one to three documents (18.9\%), on 35 of 588 with four to 49 (6.0\%) and on 4 of 6\,636 with 50 or more (0.1\%). The short-list rate varies by an order of magnitude between collections: 13 of 330 on NFCorpus (3.6k documents), 18 of 141 on SciDocs (26k), 90 of 219 on FiQA (58k) and 16 of 18 on TREC-COVID (171k). A short exact-match list over a large corpus is likely to be a different handful of documents from the dense top 100, whether or not it is any good. The ceiling also fired over a leg of four or more documents on 39 runs, all on FiQA, TREC-COVID and SciDocs, so ``a short leg'' is not a safe reading of every excess query on a large corpus; the row count is.

\subsection{Effectiveness is a separate question}

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
NFCorpus & 0.374 & 0.382 & 0.363 & 0.347 & 0.361 & 0.344 & 0.355 & 0.368 & 0.352 \\
ArguAna & 0.456 & 0.456 & 0.438 & 0.356 & 0.356 & 0.383 & 0.329 & 0.329 & 0.389 \\
SciDocs & 0.217 & 0.216 & 0.195 & 0.187 & 0.187 & 0.182 & 0.187 & 0.186 & 0.183 \\
FiQA & 0.406 & 0.396 & 0.348 & 0.376 & 0.367 & 0.330 & 0.399 & 0.389 & 0.362 \\
TREC-COVID & 0.779 & 0.744 & 0.763 & 0.823 & 0.784 & 0.769 & 0.696 & 0.669 & 0.714 \\
\bottomrule
\end{tabular}
\caption{nDCG@10 of the dense retriever, the hybrid with the buggy keyword leg (h-and) and the hybrid with the fixed one (h-or). Single runs; no paired uncertainty is reported, so differences are read as observed magnitudes, not as significant.}
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
NFCorpus & 0.337 & 0.341 & 0.337 & 0.298 & 0.303 & 0.309 & 0.319 & 0.323 & 0.328 \\
ArguAna & 0.993 & 0.993 & 0.991 & 0.980 & 0.980 & 0.984 & 0.949 & 0.949 & 0.981 \\
SciDocs & 0.496 & 0.495 & 0.469 & 0.404 & 0.404 & 0.409 & 0.421 & 0.421 & 0.425 \\
FiQA & 0.741 & 0.740 & 0.715 & 0.682 & 0.682 & 0.675 & 0.732 & 0.732 & 0.711 \\
TREC-COVID & 0.141 & 0.140 & 0.133 & 0.150 & 0.148 & 0.137 & 0.128 & 0.127 & 0.124 \\
\bottomrule
\end{tabular}
\caption{Recall@100, same conditions and layout as Table~\ref{tab:ndcg}.}
\label{tab:recall}
\end{table}

Repairing the leg restores overlap: the mean number of documents credited by both legs rose from at most 4.0 per query to between 19.0 and 43.7 on every collection. It does not reliably improve retrieval (Tables~\ref{tab:ndcg} and~\ref{tab:recall}). Over the 18 collection--encoder pairs, the repaired hybrid is above \textsc{dense} at nDCG@10 in 5 and above it at Recall@100 in 9, and the buggy hybrid is above the repaired one at nDCG@10 in 12. The two largest gains are on ArguAna, the one collection where BM25 (0.360) beats two of the encoders at nDCG@10 (e5 +0.059 and nomic +0.027); the other three are small (nomic and e5 on SciFact, +0.004 and +0.007; e5 on TREC-COVID, +0.018). The losses are largest on FiQA, where BM25 is far behind every encoder (0.224 nDCG@10 against 0.376 to 0.406) and the repaired hybrid is 0.037 to 0.059 below \textsc{dense}. A plausible mechanism, not tested here, is that where the AND builder fired at all it returned a short list of exact matches that ranked well at depth 10, while the OR list adds candidates that help at depth 100 when the dense leg misses them and dilute depth 10 when it does not. Whether RRF over BM25 and a given dense encoder helps is a question \citet{bruch2023fusion} treat at length; these runs say only that it depended on the pair. A monitor for leg health and a verdict on retrieval effectiveness are different instruments.

\subsection{How short is too short}

To measure the test against short live legs under control, the fixed keyword list was capped at its first $n$ documents and fused with the dense top $K$, for $K \in \{60, 100\}$, on every SciFact and NFCorpus query where the leg returned anything, for bge and nomic (Table~\ref{tab:sweep}). A cap, not a length: a query whose leg returned fewer than $n$ documents keeps its short list in every cell, so each cell measures the ceiling rate given a cap of $n$ over the same 300 and 298 queries. Three things hold in every cell for both encoders. The ceiling fired exactly on the queries where the two lists shared no document: the fired rate and the disjoint rate are equal to the query. The rate falls fast with the cap: at $K = 60$, a cap of one document leaves the lists disjoint on 8.7 to 15.1\% of queries, a cap of three on 2.7 to 6.7\%, a cap of ten on 0.7 to 2.3\%, and a cap of twenty or more on at most 1.7\%, under 1\% in 11 of those 20 cells. A deeper dense list never raises a figure. The $K > k$ leak, a ceiling with overlap hidden at deep ranks, is impossible by arithmetic unless $(n-1)(K-1) \ge k^2$, which among these cells holds only at $K = 100$ with $n \in \{50, 100\}$; in those eight cells, 2\,392 query runs, it did not occur. It did occur twice in the natural FiQA runs above, both with $n = 100$, so the sweep's zero is a property of these two small collections, not of the test. The sweep was not repeated on the four larger collections; the natural row counts above stand in for it there, and they show the short-list rate is several times higher on a large corpus than these two small ones suggest.

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

\section{Related work}

Reciprocal rank fusion was proposed by \citet{cormack2009rrf}, who set $k=60$ by experiment; the system here used that constant unchanged, which is what made the $1/60$ ceiling recognisable on sight. The older fusion literature studied overlap between the lists being fused: CombSUM and CombMNZ \citep{fox1994combination} reward documents returned by several systems, \citet{lee1997analyses} showed that fusion helps when the systems agree on relevant documents more than on non-relevant ones, and \citet{montague2001normalization} treated the score-scale problem that rank fusion sidesteps. Rank-biased overlap \citep{webber2010rbo} is the principled measure of agreement between two indefinite rankings; the both-leg count in Section~\ref{sec:beir} is its crudest relative, measured where it had gone to zero. On hybrid lexical and dense retrieval, \citet{luan2021sparse} and \citet{gao2021clear} establish the complementarity the hybrid relies on, and \citet{bruch2023fusion} analyse fusion functions and show when RRF is and is not competitive with a tuned convex combination; this paper is about a failure upstream of that choice, where one of the lists is empty. Query performance prediction \citep{cronentownsend2002qpp} asks, per query, whether a retriever did well; the ceiling asks a cruder question of the fusion, whether its inputs agreed on anything, and the instrumentation it calls for is the kind \citet{cooper1998monitoring} argued retrieval systems should carry. \citet{kamphuis2020bm25} show how much BM25 scores vary across implementations of the same formula; the FTS5 variant here is one more, and its query grammar, not its scoring, is what failed.

\section{Limitations}

The production measurements are on ten and fifteen queries over private corpora and are reported as aggregates the reader cannot check; they establish that the failure happened and how it looked, not an effect size. The public reproduction uses six collections and three encoders of one size class (768-dimensional, base-sized), single runs without paired uncertainty, and FTS5's default BM25 weighting of title and text. The collections differ in several ways at once, so the orderings reported here (empty rate against content words per query, short-list disjointness against corpus size) are observations over five or six points, not controlled effects. The truncation sweep covers only the two smallest collections. The exact ceiling statement needs $K \le k$, and the guarantee that an empty leg is never missed needs two retrievers; the common $K=100, k=60$ setting gets the one-sided direction and the direct overlap count instead, and it produced two ceilings with overlap present. The ceiling detects zero overlap; attributing it to an empty leg needs the per-leg row counts, and a leg that returns one useless document the other leg also returns, as on ArguAna, passes both the ceiling and a zero-row check. The negative results are negative on one system each.

\section{What to check in your own system}

Log, per query, each retriever's row count and the maximum fused score. If the maximum sits at $1/k$ (or $1/(k+1)$ for one-based ranks) on more than a few queries, then with per-retriever depth $K \le k$ the retrievers are not agreeing on anything, and at greater depth they are not agreeing near the top; read the row counts to learn whether one of them is empty, nearly empty, or retrieving from a different part of the corpus, and at greater depth count shared documents directly. Expect more such queries on a large corpus, where a short exact-match list is often a different handful of documents from the vector list. Look at the distribution of row counts, not only at zero: a leg that returns one document on nearly every query is as suspect as one that returns none, and if the corpus indexes the kind of text it is queried with (messages, notes, tickets), check whether that one document is the query itself. Test the keyword builder with a conversational sentence, not a two-word term, and treat zero rows for a six-word query as something to explain, since a legitimately selective query can return nothing. And if your fusion scores look ``flat'', compute $1/(k+r+1)$ before concluding anything about fusion.

\section*{Use of AI tools}

The code, the experiment and audit scripts, and the text of this paper were drafted with Claude (Anthropic) running in Claude Code, directed by the author, who operated the production system in which the incident occurred, chose what to measure, ruled on every claim and takes responsibility for all content. Drafts were reviewed by GPT-6 (Astra and Sol) and SWE-2 through Cognition's Devin CLI, by DeepSeek V4.1 Flash and GPT-5.6, and by Gemini; every defect a reviewer reported was reproduced or refuted by a script before it changed the paper, and the review records, probes and the audit script that checks every number in the text against the result files are in the repository. Every reference was checked against a primary listing.

\acks{This work received no funding. The author declares no competing interests.}

\bibliography{refs}

\appendix
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
ArguAna & bm25-and & 0.000 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.352 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.360 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.456 & 0.993 & -- & -- & -- \\
ArguAna & hybrid-and & 0.456 & 0.993 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.438 & 0.991 & 0.0\% & 0.0\% & 38.6 \\
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
ArguAna & bm25-and & 0.000 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.352 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.360 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.356 & 0.980 & -- & -- & -- \\
ArguAna & hybrid-and & 0.356 & 0.980 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.383 & 0.984 & 0.0\% & 0.0\% & 43.7 \\
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
ArguAna & bm25-and & 0.000 & 0.001 & 0.0\% & -- & -- \\
ArguAna & bm25-or-raw & 0.352 & 0.957 & 0.0\% & -- & -- \\
ArguAna & bm25-or & 0.360 & 0.965 & 0.0\% & -- & -- \\
ArguAna & dense & 0.329 & 0.949 & -- & -- & -- \\
ArguAna & hybrid-and & 0.329 & 0.949 & 0.0\% & 0.0\% & 1.0 \\
ArguAna & hybrid-or & 0.389 & 0.981 & 0.0\% & 0.0\% & 33.5 \\
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
The SciFact and NFCorpus runs were first made on CPU (12-core x86-64, PyTorch CPU wheels), about an hour per collection and encoder for document embedding. All 18 collection--encoder pairs were then run in a Kaggle kernel on one NVIDIA T4 (\path{kaggle/run.py} on branch \path{kaggle/irrj-expansion} of the repository, which clones the runner at a pinned commit and records package versions and the device in a manifest): PyTorch 2.11 with CUDA 12.8, \texttt{transformers} 4.49, \texttt{sentence-transformers} 3.4.1, \texttt{ir\_datasets} 0.6.3. The GPU runs of the four original SciFact and NFCorpus pairs reproduced the CPU results to every digit the result files carry for nDCG@10 and Recall@100, so the tables mix the two without distinction; query times are not comparable across the two machines. Documents were embedded in batches of 64, except nomic on SciDocs, FiQA and TREC-COVID, which ran out of GPU memory at that size (nomic accepts 8\,192 tokens, the other two encoders 512) and were run at batch 8 in a second kernel; batch size reaches the vectors only through padding and the order of floating-point operations, and its effect on these runs was not measured. \texttt{nomic-embed-text-v1.5} needs a 4.x \texttt{transformers} because its remote model code calls a method removed in 5.0; the runner pins it below 4.50. Documents were embedded as title and text joined by a space, with the encoder's document prefix where its model card prescribes one (\texttt{search\_document:} for nomic, \texttt{passage:} for e5, none for bge); queries with the query prefix (\texttt{search\_query:} for nomic; \texttt{query:} for e5; \texttt{Represent this sentence for searching relevant passages:} for bge, which its card asks for on retrieval queries and on nothing else); all vectors normalised. The FTS5 index holds title and text columns, BM25 with default weights, built atomically. Depth 100 for every retriever; $k = 60$ for fusion. ArguAna, SciDocs and TREC-COVID have a single test split in BEIR and are loaded as \texttt{beir/arguana}, \texttt{beir/scidocs} and \texttt{beir/trec-covid}. Per-query diagnostics are in \texttt{results/*.perquery.jsonl}; \texttt{scripts/keyword\_facts.py} computes the encoder-free keyword facts, \texttt{scripts/tables.py} and \texttt{scripts/natural\_lengths.py} the tables and per-query counts, and the audit script \texttt{review/orrery-audit.py} checks every number in this paper against the result files.
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
  "and_any_relevant_hit": 6
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
  "and_any_relevant_hit": 123
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
  "and_any_relevant_hit": 1
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
  "and_any_relevant_hit": 10
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
  "and_any_relevant_hit": 19
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
  "and_any_relevant_hit": 12
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
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0004487409342613496,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 29.480320423896554
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.35152149497562707,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 782.1531721578966
  },
  "bm25_or": {
   "ndcg_cut_10": 0.35988905046468606,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 43.91389776102364
  },
  "dense": {
   "ndcg_cut_10": 0.45576416153131655,
   "recall_100": 0.9928876244665719,
   "mean_query_ms": 0.7121472788097875
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.45576416153131655,
   "recall_100": 0.9928876244665719,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 59.33096300142274
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.43763310247794285,
   "recall_100": 0.9914651493598862,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 38.578947368421055,
   "mean_query_ms": 75.75917838690951
  }
 }
}


=== results/beir_arguana__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/arguana",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0004487409342613496,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 29.742316383369246
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.35152149497562707,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 783.4038812276063
  },
  "bm25_or": {
   "ndcg_cut_10": 0.35988905046468606,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 43.8203715405547
  },
  "dense": {
   "ndcg_cut_10": 0.32938953525120884,
   "recall_100": 0.9487908961593172,
   "mean_query_ms": 0.728653400431179
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.32938953525120884,
   "recall_100": 0.9487908961593172,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 61.28247096088604
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3885912759011939,
   "recall_100": 0.980796586059744,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 33.49644381223329,
   "mean_query_ms": 77.39747595946375
  }
 }
}


=== results/beir_arguana__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/arguana",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 8674,
 "n_queries": 1406,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0004487409342613496,
   "recall_100": 0.0007112375533428165,
   "empty_rate": 0.0,
   "mean_query_ms": 29.765502093877682
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.35152149497562707,
   "recall_100": 0.9566145092460882,
   "empty_rate": 0.0,
   "mean_query_ms": 780.6437071571881
  },
  "bm25_or": {
   "ndcg_cut_10": 0.35988905046468606,
   "recall_100": 0.965149359886202,
   "empty_rate": 0.0,
   "mean_query_ms": 44.21132260098936
  },
  "dense": {
   "ndcg_cut_10": 0.3558668227110038,
   "recall_100": 0.9800853485064012,
   "mean_query_ms": 0.7578813136588953
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3558668227110038,
   "recall_100": 0.9800853485064012,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 1.0028449502133712,
   "mean_query_ms": 61.208941650073086
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3830907048042733,
   "recall_100": 0.9836415362731152,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 43.66216216216216,
   "mean_query_ms": 79.56817839969871
  }
 }
}


=== results/beir_fiqa_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.2993820570964876
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 89.03561540585733
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 15.439129319483309
  },
  "dense": {
   "ndcg_cut_10": 0.406231202203102,
   "recall_100": 0.7414716927448408,
   "mean_query_ms": 6.529918007698951
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.39565958971025805,
   "recall_100": 0.7403142853374335,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.8719135802469136,
   "multi_leg_docs_mean": 0.4382716049382716,
   "mean_query_ms": 13.505908955244475
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.34760005842316993,
   "recall_100": 0.7151067810790034,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0030864197530864196,
   "multi_leg_docs_mean": 22.057098765432098,
   "mean_query_ms": 36.109278753108946
  }
 }
}


=== results/beir_fiqa_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.2591779320649006
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 89.39611233800682
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 15.479901174327928
  },
  "dense": {
   "ndcg_cut_10": 0.3986663557596119,
   "recall_100": 0.732044310285051,
   "mean_query_ms": 6.552540330232413
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3888066965901325,
   "recall_100": 0.7322500716019235,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.8842592592592593,
   "multi_leg_docs_mean": 0.35648148148148145,
   "mean_query_ms": 13.476075157465553
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3615226982966812,
   "recall_100": 0.7111913806358251,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0030864197530864196,
   "multi_leg_docs_mean": 19.03858024691358,
   "mean_query_ms": 36.435344537014515
  }
 }
}


=== results/beir_fiqa_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/fiqa/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 57638,
 "n_queries": 648,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.01363216111432012,
   "recall_100": 0.015277777777777779,
   "empty_rate": 0.8179012345679012,
   "mean_query_ms": 3.4622585169711186
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.23303809052065316,
   "recall_100": 0.5206037361129954,
   "empty_rate": 0.0,
   "mean_query_ms": 94.25293754012529
  },
  "bm25_or": {
   "ndcg_cut_10": 0.22408679700516937,
   "recall_100": 0.5081195467769543,
   "empty_rate": 0.0,
   "mean_query_ms": 16.445687060170567
  },
  "dense": {
   "ndcg_cut_10": 0.37647587524591536,
   "recall_100": 0.6816969381784197,
   "mean_query_ms": 6.76870209259227
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.36660469598062045,
   "recall_100": 0.6820827406475555,
   "keyword_empty_rate": 0.8179012345679012,
   "at_ceiling_rate": 0.875,
   "multi_leg_docs_mean": 0.44907407407407407,
   "mean_query_ms": 14.279290521622801
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.32970390380849496,
   "recall_100": 0.6747090144080885,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 24.07253086419753,
   "mean_query_ms": 39.02668452469613
  }
 }
}


=== results/beir_nfcorpus_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.15729987923464603
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.064087758600426
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 0.8090575417664462
  },
  "dense": {
   "ndcg_cut_10": 0.3743755691751346,
   "recall_100": 0.3367217011621948,
   "mean_query_ms": 0.40244657595433947
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.38191873351651584,
   "recall_100": 0.34137678250298964,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5170278637770898,
   "multi_leg_docs_mean": 4.006191950464396,
   "mean_query_ms": 0.8640091269716387
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.36284269584668527,
   "recall_100": 0.33730924988625693,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.08668730650154799,
   "multi_leg_docs_mean": 21.328173374613,
   "mean_query_ms": 1.7930602942541676
  }
 }
}


=== results/beir_nfcorpus_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.1743028235347539
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.330778978327879
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 0.937357801857286
  },
  "dense": {
   "ndcg_cut_10": 0.35510251404870363,
   "recall_100": 0.3185760067364094,
   "mean_query_ms": 0.3737557399417091
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3678957779251112,
   "recall_100": 0.3226757109288711,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5139318885448917,
   "multi_leg_docs_mean": 3.7863777089783284,
   "mean_query_ms": 0.8547177894713168
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.3519764673412563,
   "recall_100": 0.32788191530012983,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.07739938080495357,
   "multi_leg_docs_mean": 20.563467492260063,
   "mean_query_ms": 2.1673852879321314
  }
 }
}


=== results/beir_nfcorpus_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/nfcorpus/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 3633,
 "n_queries": 323,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.19328748232833015,
   "recall_100": 0.09468591006219289,
   "empty_rate": 0.5077399380804953,
   "mean_query_ms": 0.15119433124996967
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.3037511132701872,
   "recall_100": 0.23181089503141783,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 2.0541741516027168
  },
  "bm25_or": {
   "ndcg_cut_10": 0.30593933783412974,
   "recall_100": 0.23332407907648695,
   "empty_rate": 0.07739938080495357,
   "mean_query_ms": 0.7938742043055635
  },
  "dense": {
   "ndcg_cut_10": 0.3472864545686363,
   "recall_100": 0.2976659245321355,
   "mean_query_ms": 0.25227166252389505
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.3605609243746079,
   "recall_100": 0.3030444741783152,
   "keyword_empty_rate": 0.5077399380804953,
   "at_ceiling_rate": 0.5170278637770898,
   "multi_leg_docs_mean": 3.7058823529411766,
   "mean_query_ms": 1.8153405510678984
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.34446534110281624,
   "recall_100": 0.3087846774584911,
   "keyword_empty_rate": 0.07739938080495357,
   "at_ceiling_rate": 0.08359133126934984,
   "multi_leg_docs_mean": 20.993808049535605,
   "mean_query_ms": 2.242180479689261
  }
 }
}


=== results/beir_scidocs__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/scidocs",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 0.8357485419801378
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 35.19910329500999
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 10.345789832011178
  },
  "dense": {
   "ndcg_cut_10": 0.2172458820187077,
   "recall_100": 0.49568333333333336,
   "mean_query_ms": 2.6334860129991284
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.21558440838455112,
   "recall_100": 0.49548333333333333,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.949,
   "multi_leg_docs_mean": 0.131,
   "mean_query_ms": 4.658116915991741
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.19502002564070217,
   "recall_100": 0.46855,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 29.253,
   "mean_query_ms": 22.38212548899719
  }
 }
}


=== results/beir_scidocs__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/scidocs",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 0.8290599469828521
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 35.42375780301427
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 10.428617210011907
  },
  "dense": {
   "ndcg_cut_10": 0.18681165035878386,
   "recall_100": 0.42086666666666667,
   "mean_query_ms": 2.642463571000917
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.18604083540209956,
   "recall_100": 0.42086666666666667,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.947,
   "multi_leg_docs_mean": 0.146,
   "mean_query_ms": 4.619135006014403
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.18312369696270658,
   "recall_100": 0.4245333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 31.686,
   "mean_query_ms": 22.314079938998475
  }
 }
}


=== results/beir_scidocs__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/scidocs",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 25657,
 "n_queries": 1000,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.0027395069961148235,
   "recall_100": 0.0024,
   "empty_rate": 0.942,
   "mean_query_ms": 0.9501093750000109
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.15191525123523383,
   "recall_100": 0.3429666666666667,
   "empty_rate": 0.0,
   "mean_query_ms": 37.55358973499961
  },
  "bm25_or": {
   "ndcg_cut_10": 0.15263822634742566,
   "recall_100": 0.34376666666666666,
   "empty_rate": 0.0,
   "mean_query_ms": 11.241255229000444
  },
  "dense": {
   "ndcg_cut_10": 0.18720982971345648,
   "recall_100": 0.40351666666666663,
   "mean_query_ms": 2.804715709999755
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.18717787198938834,
   "recall_100": 0.4037166666666667,
   "keyword_empty_rate": 0.942,
   "at_ceiling_rate": 0.948,
   "multi_leg_docs_mean": 0.165,
   "mean_query_ms": 5.07448345799753
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.18216195683829123,
   "recall_100": 0.4090666666666667,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.001,
   "multi_leg_docs_mean": 32.335,
   "mean_query_ms": 24.818990353994195
  }
 }
}


=== results/beir_scifact_test__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/scifact/test",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.33051206002710387
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 10.242607866651573
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 2.9847529800220705
  },
  "dense": {
   "ndcg_cut_10": 0.740391287918679,
   "recall_100": 0.9666666666666667,
   "mean_query_ms": 2.4072878233588804
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7413210611028186,
   "recall_100": 0.9666666666666667,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 2.059341619957801
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.723222892352137,
   "recall_100": 0.9693333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 28.923333333333332,
   "mean_query_ms": 6.196321916625796
  }
 }
}


=== results/beir_scifact_test__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/scifact/test",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.4913985899960001
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 13.20471807333206
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 3.6053670966638642
  },
  "dense": {
   "ndcg_cut_10": 0.7194288840281022,
   "recall_100": 0.9626666666666667,
   "mean_query_ms": 0.5209540033327661
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7216220732692757,
   "recall_100": 0.9626666666666667,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 1.5684053133365221
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7261362529108524,
   "recall_100": 0.9593333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 27.88,
   "mean_query_ms": 7.252525286670182
  }
 }
}


=== results/beir_scifact_test__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/scifact/test",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 5183,
 "n_queries": 300,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.017967933499973672,
   "recall_100": 0.0175,
   "empty_rate": 0.98,
   "mean_query_ms": 0.3349109666911924
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.6592629715070466,
   "recall_100": 0.8792222222222221,
   "empty_rate": 0.0,
   "mean_query_ms": 10.346700153349957
  },
  "bm25_or": {
   "ndcg_cut_10": 0.6652831835476664,
   "recall_100": 0.8758888888888888,
   "empty_rate": 0.0,
   "mean_query_ms": 2.8774194467284055
  },
  "dense": {
   "ndcg_cut_10": 0.703264558006416,
   "recall_100": 0.9283333333333333,
   "mean_query_ms": 0.31695034329459304
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7049349018735447,
   "recall_100": 0.9283333333333333,
   "keyword_empty_rate": 0.98,
   "at_ceiling_rate": 0.98,
   "multi_leg_docs_mean": 0.023333333333333334,
   "mean_query_ms": 1.4162938199782122
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.707599954130132,
   "recall_100": 0.9583333333333334,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 25.9,
   "mean_query_ms": 5.30859065009281
  }
 }
}


=== results/beir_trec-covid__BAAI_bge-base-en-v1.5.json ===

{
 "dataset": "beir/trec-covid",
 "model": "BAAI/bge-base-en-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 13.073440160151222
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 299.58420768005453
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 92.33034881988715
  },
  "dense": {
   "ndcg_cut_10": 0.7794198743263,
   "recall_100": 0.1406060337521087,
   "mean_query_ms": 19.884081819873245
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7442365896481532,
   "recall_100": 0.1398681006774477,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.9,
   "multi_leg_docs_mean": 0.86,
   "mean_query_ms": 46.81774325981678
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7630034988091393,
   "recall_100": 0.13251237490123943,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 21.62,
   "mean_query_ms": 172.96919829994295
  }
 }
}


=== results/beir_trec-covid__intfloat_e5-base-v2.json ===

{
 "dataset": "beir/trec-covid",
 "model": "intfloat/e5-base-v2",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 13.03973546004272
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 306.5490443001909
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 91.93774745988776
  },
  "dense": {
   "ndcg_cut_10": 0.6964665036183234,
   "recall_100": 0.12825429859351073,
   "mean_query_ms": 21.195974100010062
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.6690190503349285,
   "recall_100": 0.12735457763796978,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.9,
   "multi_leg_docs_mean": 0.78,
   "mean_query_ms": 46.42892326002766
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7141259573322069,
   "recall_100": 0.12448291194509395,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 19.64,
   "mean_query_ms": 175.97261862003506
  }
 }
}


=== results/beir_trec-covid__nomic-ai_nomic-embed-text-v1.5.json ===

{
 "dataset": "beir/trec-covid",
 "model": "nomic-ai/nomic-embed-text-v1.5",
 "depth": 100,
 "rrf_k": 60,
 "n_docs": 171332,
 "n_queries": 50,
 "conditions": {
  "bm25_and": {
   "ndcg_cut_10": 0.07471900786398018,
   "recall_100": 0.0034231960123585338,
   "empty_rate": 0.74,
   "mean_query_ms": 12.940481939967867
  },
  "bm25_or_raw": {
   "ndcg_cut_10": 0.5324579822779097,
   "recall_100": 0.09092455548779359,
   "empty_rate": 0.0,
   "mean_query_ms": 301.2609381200491
  },
  "bm25_or": {
   "ndcg_cut_10": 0.5381490128385611,
   "recall_100": 0.10073632354564847,
   "empty_rate": 0.0,
   "mean_query_ms": 92.04611055993155
  },
  "dense": {
   "ndcg_cut_10": 0.8233852502363679,
   "recall_100": 0.14969146695405253,
   "mean_query_ms": 20.220418280023296
  },
  "hybrid_and": {
   "ndcg_cut_10": 0.7839120408952137,
   "recall_100": 0.1481276343305029,
   "keyword_empty_rate": 0.74,
   "at_ceiling_rate": 0.88,
   "multi_leg_docs_mean": 0.7,
   "mean_query_ms": 47.59616048004318
  },
  "hybrid_or": {
   "ndcg_cut_10": 0.7689024541758697,
   "recall_100": 0.1369381135986194,
   "keyword_empty_rate": 0.0,
   "at_ceiling_rate": 0.0,
   "multi_leg_docs_mean": 21.9,
   "mean_query_ms": 175.59457323997776
  }
 }
}
