# Review: dead-retriever paper, draft 2 — round 2 (narrow)

You are reviewing the revised Section 2 and Section 6 of a short arXiv paper (cs.IR), plus one question about the paper as a whole. Round 1 (six reviewers) established that the 1/k ceiling in reciprocal rank fusion proves zero overlap between the fused lists, not an empty retriever; that the K > k weak form needed counter-examples; that bge's query instruction was missing; and that per-query diagnostics were needed to support the false-positive explanation. All of that has been changed. Answer as a demanding IR reviewer. Be specific; formulas and line references over adjectives; no compliments; do not restate the paper. Under 800 words.

## Earlier rounds

Round 1 changed: title and abstract (zero-overlap framing); Section 2 rewritten with the equivalence stated in both directions, the K > k counter-examples, the L = 2 qualification and the one-based ceiling; Section 6 re-run with bge's query instruction, a no-stopword OR condition, timings and per-query rows; Section 6's reading paragraphs rewritten (leg health vs effectiveness, excess ceiling queries verified individually, buggy-beats-fixed stated); eleven references added; Table 1 backed by an aggregates file.

## What is under review

Only Section 2 ("The ceiling, and what it does and does not say") and Section 6 ("Reproduction on public collections"), and the question in item 4. Everything else is settled for this round.

## Attached

The paper's LaTeX source is reproduced in full below, followed by the four result JSON files. Do not use any tool: do not read files, run commands, or fetch URLs. Answer in your final message.

## Questions

1. **Section 2** — Is every sentence now true as stated? Is the "if and only if" correct under the stated assumptions (K <= k, each document once per list, at least one result)? Is anything still over-claimed about what the ceiling diagnoses? Is anything now under-claimed (a true, useful statement the section could make and does not)?
2. **Section 6** — Do the four reading paragraphs follow from Tables 2 and 3 and the stated per-query facts? Is the false-positive accounting (excess queries, denominators, "the alarm was literally right") sound? Is the effectiveness paragraph fair to both directions of the evidence?
3. **Prose** — Which sentences in these two sections are filler, repetition or stakes inflation?
4. **The paper as a whole.** The author's own question, verbatim: "are you sure this paper is good/relevant?" Answer as a program-committee member would: what is the contribution, who would read it, is it worth publishing as an arXiv preprint, would it be accepted at any IR venue and which, and what one change would most raise its value. Be blunt.


=== paper/main.tex ===

\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}
\usepackage{natbib}
\usepackage{xcolor}
\newcommand{\todo}[1]{\textcolor{red}{[#1]}}
\setlength{\parskip}{0.35em}

\title{A Score Ceiling in Reciprocal Rank Fusion Detects Zero Overlap,\\and Found a Dead Retriever}
\author{Benjamin Meadows\\Independent Researcher\\\texttt{ben@benjaminmeadows.com}}
\date{October 2026}

\begin{document}
\maketitle

\begin{abstract}
A hybrid search system fuses a keyword retriever and a vector retriever with reciprocal rank fusion (RRF). In the system described here, the keyword retriever returned no results for most natural-language queries from the system's first version until 2026-08-18, and nobody noticed: the vector retriever always filled the result list, and the usual spot checks used short keyword queries, which still matched. The failure was visible the whole time in the fused scores. RRF credits a document $1/(k+r)$ from each retriever that ranks it at position $r$, so with per-retriever depth $K \le k$ a document found by two retrievers scores above $1/k$ and a document found by one scores at most $1/k$. A result list whose maximum fused score is $1/k$ therefore contains no document that both retrievers returned. That is a statement about overlap, not about either retriever: two working retrievers can return disjoint lists, and in the incident four of ten queries did. Across a set of queries, a ceiling that never lifts means the fusion is fusing nothing, and the per-retriever row counts, which the ceiling tells you to go and read, say why. I give the derivation and its limits, the bug (quoting every token of an SQLite FTS5 query, which FTS5 reads as an implicit AND), before-and-after aggregates from the production system, two negative results measured beside the dead leg, and a reproduction on two BEIR collections with two encoders: the builder returns nothing for 98.0\% of SciFact's sentence queries and 50.8\% of NFCorpus's title queries, the ceiling rate tracks the empty-leg rate to within one percentage point, and repairing the leg restores overlap and recall at depth without improving nDCG@10 for the stronger encoder. Code, results, per-query diagnostics and this paper's source are at \todo{repository URL}.
\end{abstract}

\section{The incident}

The system is a personal search engine over about 30\,000 to 217\,000 text chunks per corpus, split across five SQLite databases that share one retrieval module. Each query runs two retrievers over the same chunks: an SQLite FTS5 index ranked by BM25 \citep{robertson2009bm25,sqlite_fts5}, and a 768-dimensional embedding index searched by exact cosine. The two ranked lists, each cut at depth $K=60$, are fused with reciprocal rank fusion at $k=60$ \citep{cormack2009rrf}.

On 2026-08-07 a recency-decay feature was evaluated and rejected because RRF scores were ``flat near the top'': adjacent ranks differed by about 1.4\%, so even a 5\% age multiplier acted as a strong reranker rather than a tie-break. That flatness was recorded as a property of fusion. On 2026-08-18, while investigating why the keyword side rarely seemed to matter, I logged the keyword retriever's row counts for ten real queries. Five of five conversational queries matched zero chunks, as did a two-word place-name query. Only queries of two or three technical tokens matched anything. The keyword retriever had been inert on prose queries since the system was built, and all four sibling engines carried the same line of code.

The fused scores had said so from the start. Over the top 100 fused results of those ten queries, the maximum score was exactly $1/60 = 0.01\overline{6}$. The values were $1/60, 1/61, 1/62, \ldots$ with gaps where per-file deduplication removed a chunk: one retriever's rank list passed through the RRF formula. The ``1.4\% flatness'' was a red herring in both directions. It is the relative step of the formula, $\bigl(1/(k+r) - 1/(k+r+1)\bigr) / \bigl(1/(k+r)\bigr) = 1/(k+r+1)$, 1.6\% at the top of the list and 1.4\% around rank 10, and two live lists that agreed on every document would show the same step at twice the scale. The signature of the single list was the scale, $1/60$ rather than $2/60$, and the integer staircase under it.

\section{The ceiling, and what it does and does not say}
\label{sec:ceiling}

Let $L$ retrievers each return a ranked list cut at depth $K$ in which every document appears once, and let $r_\ell(d) \in \{0,\ldots,K-1\}$ be document $d$'s 0-based rank in retriever $\ell$'s list when present. Reciprocal rank fusion scores
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

Three qualifications bound what that means in practice. First, it is a statement about overlap. Two retrievers that both return $K$ documents and share none of them produce the same ceiling as one retriever and one empty list, and so does a keyword leg that returns one or two documents the vector leg did not. In the incident, the keyword leg returned rows on four of the ten queries and the ceiling held on all ten (Table~\ref{tab:prod}); those four were lists of one to three chunks, with nothing in common with the vector top 60. The ceiling says the fusion is not fusing. The per-retriever row count says why, and a system that fuses should log both. Second, the equivalence needs $K \le k$. With $K > k$, a document ranked deep in both lists scores below $1/k$ (rank 90 in both at $k=60$ gives $2/150$), and one ranked exactly $k$ in both scores exactly $1/k$, so a maximum of $1/k$ no longer excludes overlap; what survives is that every retriever's rank-0 document is exclusive, and the sequence $1/k, 1/(k+1), 1/(k+2), \ldots$ running down the fused scores is still the fingerprint of a single list. A system that keeps per-retriever ranks measures overlap directly by counting documents credited by two or more retrievers, and Section~\ref{sec:beir}, which uses $K = 100 > k$, reports both. Third, with more than two retrievers the test detects at most one live leg, not one dead leg among several; the setting here is $L = 2$. The one-based RRF of \citet{cormack2009rrf} shifts every figure by one: the singleton ceiling is $1/(k+1)$.

What the test costs is one comparison per query on numbers the system already has. What it buys is an alarm that cannot miss an empty leg (an empty leg gives exactly $1/k$ whenever the other leg returned anything) and can only over-fire, so the only thing to calibrate is how often live legs are disjoint, which Section~\ref{sec:beir} measures.

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

The corpus is private. This section reports counts, timings and overlaps recorded at the time, with no query or document text; the figures are in \texttt{results/production-aggregates.json} in the released repository and are checkable by nobody but the operator, which is the reason the public reproduction exists. Ten real queries were replayed before and after the fix on the same shard (Table~\ref{tab:prod}).

\begin{table}[h]
\centering
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

\paragraph{Recency decay.} A multiplicative age penalty on fused scores (floor 0.85, time constant 180 days) changed the top-1 result on 4 of 7 real queries on a notes corpus, and the changes were as often wrong as right; a canonical note unedited for 338 days was demoted under a 13-day-old draft. On a second corpus spanning only 63 days the multiplier varied between 0.956 and 1.000 across every document and changed 0 of 8 top-1 results. The feature was rejected. At the time the sensitivity was attributed to flat fused scores; Section~\ref{sec:ceiling} shows the relative step is a property of the formula at any overlap, so the flatness explained nothing, and whether decay would behave differently over a fused list with real two-leg scores was not tested.

\paragraph{A title prefix before embedding.} Prepending \texttt{kind: title} to each chunk before embedding (the stored text and the keyword index unchanged, so the vector was the only variable) and re-embedding one corpus of 3\,046 documents and 30\,734 chunks took 25 minutes. On 15 realistic queries, 13 had an identical top-1, mean top-5 overlap was 80\%, one query improved and one regressed, and the query predicted to benefit most returned an identical, still wrong, top 3. The change was not adopted. This is a heading prefix, the cheapest member of the document-expansion family \citep{nogueira2019doc2query,gao2023hyde}, not the model-written situating context of \citet{anthropic2024contextual}, and the corpus was a weak test (documents whose title is their opening line). Because the keyword leg was inert, the A/B measured the vector change alone, which was the intent.

\section{Reproduction on public collections}
\label{sec:beir}

To check that the effect is a property of the query builder and not of one private corpus, I ran six retrieval conditions on two BEIR test collections \citep{thakur2021beir}: SciFact \citep{wadden2020scifact}, 5\,183 abstracts and 300 claim queries, and NFCorpus \citep{boteva2016nfcorpus}, 3\,633 documents and 323 queries. SciFact queries are full sentences; NFCorpus queries are short titles. The collections differ in domain, corpus and relevance style as well as query length, so the contrast is suggestive, not controlled. Two encoders were used: \texttt{nomic-embed-text-v1.5} \citep{nussbaum2024nomic}, the public release of the production encoder, and \texttt{bge-base-en-v1.5} \citep{xiao2023cpack}, both 768-dimensional, each with the prefixes its model card prescribes (Appendix~\ref{app:run}). Data came through \texttt{ir\_datasets} \citep{macavaney2021irdatasets} and metrics through \texttt{pytrec\_eval} \citep{vangysel2018pytrec}. Depth $K = 100$, $k = 60$, so the ceiling is read in its weak form and overlap is also counted directly from the ranks.

The conditions are \textsc{bm25-and} (the buggy builder), \textsc{bm25-or-raw} (OR over every token), \textsc{bm25-or} (the fix: OR over non-stopword tokens), \textsc{dense}, \textsc{hybrid-and} (dense + buggy keyword, RRF) and \textsc{hybrid-or} (dense + fixed keyword, RRF). For each hybrid condition the runner writes, per query, whether the keyword leg returned nothing, whether the maximum fused score sat at $1/k$, the maximum itself, and how many documents both legs credited. Two things are reported separately throughout, because they are different results: whether the keyword leg is alive and fusing (overlap, recall at depth), and whether the hybrid retrieves better than its parts (nDCG@10).

\begin{table}[h]
\centering
\begin{tabular}{llrrrrrr}
\toprule
Collection & Condition & nDCG@10 & R@100 & ms & kw empty & at ceiling & both-leg \\
\midrule
SciFact & bm25-and & 0.018 & 0.018 & 0.3 & 98.0\% & -- & -- \\
SciFact & bm25-or-raw & 0.659 & 0.879 & 10.2 & 0.0\% & -- & -- \\
SciFact & bm25-or & 0.665 & 0.876 & 3.0 & 0.0\% & -- & -- \\
SciFact & dense & 0.740 & 0.967 & 2.4 & -- & -- & -- \\
SciFact & hybrid-and & 0.741 & 0.967 & 2.1 & 98.0\% & 98.0\% & 0.02 \\
SciFact & hybrid-or & 0.723 & 0.969 & 6.2 & 0.0\% & 0.0\% & 28.9 \\
\midrule
NFCorpus & bm25-and & 0.193 & 0.095 & 0.2 & 50.8\% & -- & -- \\
NFCorpus & bm25-or-raw & 0.304 & 0.232 & 2.1 & 7.7\% & -- & -- \\
NFCorpus & bm25-or & 0.306 & 0.233 & 0.8 & 7.7\% & -- & -- \\
NFCorpus & dense & 0.374 & 0.337 & 0.4 & -- & -- & -- \\
NFCorpus & hybrid-and & 0.382 & 0.341 & 0.9 & 50.8\% & 51.7\% & 4.0 \\
NFCorpus & hybrid-or & 0.363 & 0.337 & 1.8 & 7.7\% & 8.7\% & 21.3 \\
\bottomrule
\end{tabular}
\caption{\texttt{bge-base-en-v1.5} on two BEIR test collections. ``ms'' is mean retrieval time per query on a 12-core CPU, keyword and fusion only (query encoding excluded). ``kw empty'' is the fraction of queries on which the keyword leg returned no document; ``at ceiling'' the fraction on which the maximum fused score was $1/k$; ``both-leg'' the mean number of documents credited by both retrievers. Single runs; no paired uncertainty is reported, so differences are read as observed magnitudes, not as significant. The second encoder is in Appendix~\ref{app:nomic}.}
\label{tab:beir}
\end{table}

\paragraph{The leg.} The quoted-AND builder matched nothing on 294 of SciFact's 300 claim-length queries and on 164 of NFCorpus's 323 title queries. BM25 with the fixed builder is a usable retriever on both (0.665 and 0.306 nDCG@10). The stopword drop that made the fix cheap in production holds up here: \textsc{bm25-or-raw} is three times slower (10.2 against 3.0\,ms on SciFact, 2.1 against 0.8 on NFCorpus) and no more effective (0.659 against 0.665; 0.304 against 0.306). The fix does not eliminate empty legs: 25 NFCorpus title queries (7.7\%) still match no document after it, which is why the residual ceiling rate below is a measurement and not noise.

\paragraph{What fusion did with an empty list.} On the 294 SciFact queries with an empty keyword leg, the per-query rows show \textsc{hybrid-and}'s fused list is \textsc{dense}'s list: same document count, maximum score exactly $1/60$. Over the whole collection the two conditions differ by 0.001 nDCG@10 and 0.000 Recall@100, the contribution of the six live queries. On NFCorpus the leg was live on 159 queries, and there \textsc{hybrid-and} differs from \textsc{dense} by 0.008 nDCG@10 and 0.005 Recall@100.

\paragraph{The ceiling as a detector.} An empty keyword leg puts the maximum fused score at exactly $1/k$ whenever the dense leg returned anything, so the set of empty-leg queries is contained in the set of at-ceiling queries, and the ceiling missed no empty leg on any of the 2\,492 hybrid query runs behind Tables~\ref{tab:beir} and~\ref{tab:nomic}. The excess is the test's false positives. On SciFact there were none. On NFCorpus the ceiling fired on 167 queries against 164 empty under the buggy builder, three excess queries out of the 159 on which the leg returned something (1.9\%); after the fix, 28 against 25 for bge and 27 against 25 for nomic, three and two out of 298 (1.0\% and 0.7\%). The per-query rows settle what those queries are: in every one the keyword leg returned one or three documents and the two legs shared none, so the alarm was literally right (nothing was fused) on a leg that was alive but nearly empty. In the incident the same thing happened on four of ten queries. The test's false-positive rate is a function of how short the live list is, which is one more reason to log the row count beside the score.

\paragraph{Effectiveness is a separate question.} Repairing the leg restored overlap (0.02 to 28.9 shared documents per query on SciFact) and recall at depth for the weaker encoder (nomic Recall@100 0.928 to 0.958 on SciFact, 0.298 to 0.309 on NFCorpus); for bge it changed Recall@100 by 0.003 and 0.001. It did not improve nDCG@10 with bge (0.723 against 0.740 on SciFact, 0.363 against 0.374 on NFCorpus) and barely with nomic (0.708 against 0.703; 0.344 against 0.347). The buggy hybrid out-scores the fixed hybrid at nDCG@10 in three of the four encoder--collection pairs, and on NFCorpus it out-scores dense alone (0.382 against 0.374 for bge): where the AND builder fired at all it returned a short, specific list on which BM25 is at its best, and it stayed silent where it would have added noise. Whether RRF over BM25 and a given dense encoder helps is a question \citet{bruch2023fusion} treat at length, and two encoders and two collections cannot settle it. The point here is narrower: a monitor for leg health and a verdict on retrieval effectiveness are different instruments, and this system had neither.

\section{Related work}

Reciprocal rank fusion was proposed by \citet{cormack2009rrf}, who set $k=60$ by experiment; the system here used that constant unchanged, which is what made the $1/60$ ceiling recognisable on sight. The older fusion literature studied overlap between the lists being fused: CombSUM and CombMNZ \citep{fox1994combination} reward documents returned by several systems, \citet{lee1997analyses} showed that fusion helps when the systems agree on relevant documents more than on non-relevant ones, and \citet{montague2001normalization} treated the score-scale problem that rank fusion sidesteps. Rank-biased overlap \citep{webber2010rbo} is the principled measure of agreement between two indefinite rankings; the both-leg count in Section~\ref{sec:beir} is its crudest relative, measured where it had gone to zero. On hybrid lexical and dense retrieval, \citet{luan2021sparse} and \citet{gao2021clear} establish the complementarity the hybrid relies on, and \citet{bruch2023fusion} analyse fusion functions and show when RRF is and is not competitive with a tuned convex combination; this paper is about a failure upstream of that choice, where one of the lists is empty. Query performance prediction \citep{cronentownsend2002qpp} asks, per query, whether a retriever did well; the ceiling asks a cruder question of the fusion, whether its inputs agreed on anything, and the instrumentation it calls for is the kind \citet{cooper1998monitoring} argued retrieval systems should carry. \citet{kamphuis2020bm25} show how much BM25 scores vary across implementations of the same formula; the FTS5 variant here is one more, and its query grammar, not its scoring, is what failed.

\section{Limitations}

The production measurements are on ten and fifteen queries over private corpora and are reported as aggregates the reader cannot check; they establish that the failure happened and how it looked, not an effect size. The public reproduction uses two small collections, two encoders, single runs without paired uncertainty, and FTS5's default BM25 weighting of title and text. The exact ceiling statement needs $K \le k$ and two retrievers; the common $K=100, k=60$ setting gets the fingerprint and the direct overlap count instead. The ceiling detects zero overlap; attributing it to an empty leg, as this paper does for the incident, needs the per-leg row counts. The negative results are negative on one system each.

\section{What to check in your own system}

Log, per query, each retriever's row count and the maximum fused score. If the maximum sits at $1/k$ (or $1/(k+1)$ for one-based ranks) on more than a few queries, the retrievers are not agreeing on anything; read the row counts to learn whether one of them is empty, nearly empty, or searching a different world. Test the keyword builder with a conversational sentence, not a two-word term, and treat zero rows for a six-word query as something to explain, since a legitimately selective query can return nothing. And if your fusion scores look ``flat'', compute $1/(k+r+1)$ before concluding anything about fusion.

\bibliographystyle{plainnat}
\bibliography{refs}

\appendix
\section{Second encoder}
\label{app:nomic}

\begin{table}[h]
\centering
\begin{tabular}{llrrrrrr}
\toprule
Collection & Condition & nDCG@10 & R@100 & ms & kw empty & at ceiling & both-leg \\
\midrule
SciFact & dense & 0.703 & 0.928 & 0.3 & -- & -- & -- \\
SciFact & hybrid-and & 0.705 & 0.928 & 1.4 & 98.0\% & 98.0\% & 0.02 \\
SciFact & hybrid-or & 0.708 & 0.958 & 5.3 & 0.0\% & 0.0\% & 25.9 \\
\midrule
NFCorpus & dense & 0.347 & 0.298 & 0.3 & -- & -- & -- \\
NFCorpus & hybrid-and & 0.361 & 0.303 & 1.8 & 50.8\% & 51.7\% & 3.7 \\
NFCorpus & hybrid-or & 0.344 & 0.309 & 2.2 & 7.7\% & 8.4\% & 21.0 \\
\bottomrule
\end{tabular}
\caption{\texttt{nomic-embed-text-v1.5}, same collections and layout as Table~\ref{tab:beir}. The BM25-only rows are encoder-independent and identical to Table~\ref{tab:beir}.}
\label{tab:nomic}
\end{table}

\section{Run details}
\label{app:run}
Both encoders ran on CPU (12-core x86-64, PyTorch CPU wheels) in about an hour per collection for document embedding; embeddings are cached under a signature of model, prefix, document count and a hash of the texts, and recomputed when any of those changes. \texttt{nomic-embed-text-v1.5} needs \texttt{transformers} below 4.50 because its remote model code calls a method removed in later releases; the runner pins it. Documents were embedded as title and text joined by a space, with the encoder's document prefix where its model card prescribes one (\texttt{search\_document:} for nomic, none for bge); queries with the query prefix (\texttt{search\_query:} for nomic; \texttt{Represent this sentence for searching relevant passages:} for bge, as its card prescribes for short queries); all vectors normalised. The FTS5 index holds title and text columns, BM25 with default weights, built atomically. Depth 100 for every retriever; $k = 60$ for fusion. Per-query diagnostics are in \texttt{results/*.perquery.jsonl}; the audit script \texttt{review/orrery-audit.py} checks every number in this paper against the result files.

\end{document}


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
