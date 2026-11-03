# Review: title, abstract, introduction and conclusion of a short IR paper (round 2 of 3)

Below are the title, abstract, introduction and conclusion of a short information-retrieval paper that a journal editor desk-rejected last week as "hard to understand, as if it was AI-generated". The author rewrote it. You see only these four parts; the body (derivation, incident, experiments on six BEIR collections with three encoders, a logging recommendation, related work, limitations) is not attached, so do not judge claims you cannot check. Judge the writing.

Answer as a careful reader of cs.IR. Under 500 words. No compliments. Quote each sentence you would change and give the rewrite.

1. Which sentences would make you read twice, and why (too many numbers in one clause, a qualifier nobody asked for, a term used before it is explained)?
2. Does the introduction say, in order, what the test is, what it does not say, and why it is worth checking beside the row counts? If not, what is missing or out of order?
3. Does the conclusion add anything the abstract does not, or is it a second abstract?
4. Does the title match the abstract?

Do not use any tool. Answer in your final message.

=== title ===

The 1/k Ceiling: A Zero-Overlap Test for Hybrid Retrieval

=== abstract ===

\begin{abstract}
Hybrid search runs a keyword retriever and a dense retriever over the same corpus and fuses their ranked lists, usually with reciprocal rank fusion (RRF). If the keyword retriever silently returns nothing, the fused list still looks full, because the dense retriever fills it. This paper shows that the fused scores reveal when the two lists did not overlap. With ranks starting at zero, RRF gives a document $1/(k+r)$ from each retriever that ranks it at position $r$. With per-retriever depth $K \le k$, a document returned by two retrievers always scores above $1/k$, and a document returned by one scores at most $1/k$. So a result list whose maximum fused score is $1/k$, a list \emph{at the ceiling}, contains no document that both retrievers returned. The test measures overlap, not health: two nonempty lists that share nothing produce the same ceiling as an empty list, and per-retriever row counts tell the two cases apart. I describe a production system whose keyword query builder quoted every token of an SQLite FTS5 query, which FTS5 reads as an AND over all of them. Replayed on ten real queries, the builder returned nothing for every conversational one, and the fused list was at the ceiling on all ten. On six BEIR collections with three encoders, across 22\,362 hybrid query runs at $K = 100 > k = 60$, the buggy builder returns nothing for 50.8 to 98.0\% of queries on five collections, and the ceiling missed none of those empty lists, as the derivation requires with two retrievers. In 174 further query runs the keyword list was nonempty but shared nothing with the dense list, mostly a short list on a large corpus. In two runs under the repaired builder, the lists shared one document at deep ranks, the case $K > k$ leaves open. On the sixth collection, ArguAna, each query is itself a corpus document, so the buggy keyword list is never empty and almost never relevant, and the ceiling never appears. Repairing the keyword retriever raises overlap in every collection--encoder pair. At nDCG@10 the repaired hybrid beats the dense retriever alone in 5 of 18 pairs and loses to it in 13; two of the gains and five of the losses are significant under a paired randomization test with Holm's correction. Code, results, per-query diagnostics and this paper's source are at \url{https://github.com/TheBenMeadows/dead-retriever}.
\end{abstract}

=== introduction ===

\section{Introduction}
\label{sec:intro}

A hybrid search system runs two retrievers over the same documents, typically a keyword index scored by BM25 and a dense embedding index searched by vector similarity, and fuses the two ranked lists into one. Reciprocal rank fusion \citep[RRF;][]{cormack2009rrf} is the usual way to fuse them. With ranks starting at zero, it scores each document by the sum, over the retrievers that returned it, of $1/(k+r)$, where $r$ is the document's rank in that retriever's list and $k$ is a constant, 60 by convention.

Fusion is forgiving by design. If one retriever returns nothing, the fused list is simply the other retriever's list, and the user still sees a full page of results. That is the right behaviour for a query one retriever cannot answer. It is also the reason a broken retriever can go unnoticed: nothing downstream of the fusion distinguishes ``the keyword retriever found nothing relevant'' from ``the keyword retriever is broken''.

The fused scores can show something narrower, and useful. A document returned by only one retriever scores at most $1/k$ (rank 0 gives exactly $1/k$). A document returned by two retrievers, each cut at depth $K$, scores at least $2/(k+K-1)$, and that is above $1/k$ exactly when $K \le k$. So, at $K \le k$, a fused list whose maximum score is $1/k$ contains no document that both retrievers returned. It does not say that either list is empty. The per-retriever \emph{row counts}, the number of documents each retriever returned for the query, separate an empty list from a short one and from two full lists that happen to share nothing. The row counts cost a counter in each retriever; the maximum fused score costs nothing, because the fusion has already computed it, and it can be read from a log that kept only scores. A system that fuses should record both.

I came to this through an incident. A personal search engine of mine fused an SQLite FTS5 keyword index with a dense index at $K = k = 60$. Its keyword query builder quoted every token of the query, and FTS5 reads a sequence of quoted phrases as an AND over all of them, so a conversational query of six or seven words matched no 1\,400-character chunk. The dense retriever filled every result list, and short technical queries, the kind used in spot checks, still matched. The row counts were first logged on 2026-08-18: zero on every conversational query. The maximum fused score on those queries had been $1/60$ all along, and eleven days earlier it had been written down as ``RRF scores are flat''.

The contributions are:
\begin{enumerate}
\item the derivation and its limits (Section~\ref{sec:ceiling}): the equivalence needs $K \le k$; one direction holds at any depth; at $K > k$ a document shared at deep ranks can hide below the ceiling; with two retrievers an empty list can never be missed while the other list is nonempty;
\item the incident (Section~\ref{sec:incident}): the bug, the fix, and before-and-after counts from the production system;
\item a measurement on six BEIR collections with three encoders, 22\,362 hybrid query runs (Sections~\ref{sec:setup} and~\ref{sec:results}): how often the buggy builder returns nothing, whether the ceiling catches it, where the ceiling and the row counts disagree and why, one collection on which the test is blind by construction, and whether repairing the keyword retriever improves retrieval;
\item what a system that fuses should log (Section~\ref{sec:log}).
\end{enumerate}
Section~\ref{sec:related} places the ceiling among the fusion and monitoring literature, and Section~\ref{sec:limits} states the limits.


=== conclusion ===

\section{Conclusion}
\label{sec:conclusion}

With per-retriever depth $K \le k$, a maximum reciprocal-rank-fusion score of $1/k$ over a result list means no document in it was returned by more than one retriever, and a system that fuses can read that from the scores it already computes. In the incident, the ceiling held on all ten replayed queries and had been read as a property of fusion. On six BEIR collections the ceiling missed no empty keyword list in 22\,362 runs, as it must with two retrievers, and where it disagreed with the row counts it was reporting a nonempty list that shared nothing with the dense list, except twice, at $K > k$, where a shared document sat too deep to show. It cannot see a retriever whose one returned document the other retriever also returns, as on ArguAna; the distribution of row counts can. Repairing the keyword retriever raised overlap in every pair and improved nDCG@10 over the dense retriever alone in 5 of 18, two of them significantly, and lowered it in 13, five significantly. The scores can say whether two retrievers agreed on anything, the row counts can say what that means, and whether fusing a retriever helps is a question for relevance judgements.

