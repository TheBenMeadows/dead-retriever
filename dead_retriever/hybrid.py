"""Hybrid keyword + dense retrieval with reciprocal-rank fusion, and the
score-ceiling diagnostic that detects a leg returning nothing.

Reciprocal-rank fusion gives a document 1/(k + r) from every leg that ranks
it at position r (0-based). A document found by two legs therefore scores at
least 2/(k + K - 1), and a document ranked first by one leg alone scores
exactly 1/k. If the maximum fused score over a whole result list is 1/k, no
document was found by more than one leg: either the legs disagree completely
or one of them returned nothing. Across many queries the second explanation
is the only plausible one, and it can be read off the scores without looking
at any document.

The keyword builder has two modes. `and_quoted` reproduces the FTS5 query a
naive builder emits: every token quoted and space-joined, which FTS5 reads as
an implicit AND over all tokens. On conversational queries that match no
chunk. `or_bm25` drops stopwords and short tokens and joins the rest with OR,
ranked by bm25.
"""
import re
import sqlite3
from dataclasses import dataclass, field

import numpy as np

RRF_K = 60

FTS_STOP = frozenset("""a an the and or but if then than that this these those of in on at to
for from by with about into over under after before is are was were be been being am do does
did doing have has had having i me my mine we us our you your he she it its they them their
as not no nor so such can could should would will shall may might must what which who whom
whose when where why how all any both each few more most other some only own same too very
just dont don t s re ve ll m d get got make made want need know think see look
""".split())


def tokens(q):
    return re.findall(r"[\w$#.@-]+", q.lower())


def fts_query(q, mode="or_bm25"):
    """FTS5 MATCH string for a natural-language query.

    and_quoted: '"how" "do" "i" "fix" "the" "feed"'  (implicit AND)
    or_bm25:    '"fix" OR "feed"'
    """
    toks = tokens(q)
    if mode == "and_quoted":
        return " ".join(f'"{t}"' for t in toks)
    if mode == "or_bm25":
        kw = [t for t in toks if len(t) > 2 and t not in FTS_STOP] or toks
        return " OR ".join(f'"{t}"' for t in kw)
    raise ValueError(f"unknown fts mode {mode!r}")


class KeywordIndex:
    """SQLite FTS5 over (doc_id, title, text), ranked by bm25."""

    def __init__(self, path=":memory:"):
        self.c = sqlite3.connect(path)
        self.c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(doc_id UNINDEXED, title, text)")

    def add(self, rows):
        self.c.executemany("INSERT INTO fts(doc_id, title, text) VALUES (?, ?, ?)", rows)
        self.c.commit()

    def search(self, match, limit):
        """Ranked doc ids for an FTS5 MATCH string; [] on a syntax error."""
        try:
            cur = self.c.execute(
                "SELECT doc_id FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT ?", (match, limit))
            return [r[0] for r in cur]
        except sqlite3.OperationalError:
            return []


class DenseIndex:
    """Exact cosine search over a unit-normalised matrix."""

    def __init__(self, ids, matrix):
        self.ids = list(ids)
        m = np.asarray(matrix, dtype=np.float32)
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.m = m / norms

    def search(self, qv, limit):
        q = np.asarray(qv, dtype=np.float32)
        q = q / (np.linalg.norm(q) or 1.0)
        sims = self.m @ q
        k = min(limit, len(sims))
        if k == 0:
            return []
        cand = np.argpartition(-sims, k - 1)[:k]
        order = cand[np.lexsort((cand, -sims[cand]))]
        return [self.ids[i] for i in order]


def rrf_fuse(legs, k=RRF_K):
    """legs: {name: [doc_id, ...] ranked}. Returns (scores, ranks) where
    scores = {doc_id: fused} and ranks = {name: {doc_id: rank}}."""
    scores, ranks = {}, {}
    for name, ranked in legs.items():
        ranks[name] = {}
        for r, d in enumerate(ranked):
            if d in ranks[name]:
                continue
            ranks[name][d] = r
            scores[d] = scores.get(d, 0.0) + 1.0 / (k + r)
    return scores, ranks


@dataclass
class CeilingReport:
    max_score: float
    ceiling: float
    legs_configured: int
    legs_nonempty: int
    multi_leg_docs: int
    at_ceiling: bool
    empty_legs: list = field(default_factory=list)


def ceiling_report(scores, ranks, k=RRF_K, eps=1e-12):
    """Was any document found by more than one leg? If not, the maximum fused
    score is exactly 1/k (the top document of one leg, credited once).
    `at_ceiling` needs at least one result: a list where every leg returned
    nothing has max 0, which is an outage, not a single live leg."""
    mx = max(scores.values(), default=0.0)
    multi = sum(1 for d in scores if sum(d in r for r in ranks.values()) > 1)
    empty = [n for n, r in ranks.items() if not r]
    return CeilingReport(
        max_score=mx, ceiling=1.0 / k, legs_configured=len(ranks),
        legs_nonempty=len(ranks) - len(empty), multi_leg_docs=multi,
        at_ceiling=(len(ranks) > 1 and mx > 0 and mx <= 1.0 / k + eps), empty_legs=empty)


class HybridRetriever:
    def __init__(self, keyword, dense, fts_mode="or_bm25", depth=60, k=RRF_K):
        self.keyword, self.dense = keyword, dense
        self.fts_mode, self.depth, self.k = fts_mode, depth, k

    def retrieve(self, q, qv=None):
        legs = {}
        if self.dense is not None and qv is not None:
            legs["dense"] = self.dense.search(qv, self.depth)
        if self.keyword is not None:
            legs["keyword"] = self.keyword.search(fts_query(q, self.fts_mode), self.depth)
        scores, ranks = rrf_fuse(legs, self.k)
        return scores, ranks
