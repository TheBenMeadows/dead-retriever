"""Synthetic corpus: the and_quoted builder returns nothing for conversational
queries, and the fused scores show it as a 1/k ceiling."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dead_retriever import (RRF_K, DenseIndex, HybridRetriever, KeywordIndex,  # noqa: E402
                            ceiling_report, fts_query, rrf_fuse)

DOCS = [
    ("d1", "Feed builder", "The build-feed script writes an empty feed when the blog directory is missing."),
    ("d2", "Headers", "Cache-Control and Onion-Location headers are emitted per path block."),
    ("d3", "Release signing", "sign-release aborts on the first failed relay because of set -euo pipefail."),
    ("d4", "Accessibility", "The theme toggle gets its accessible name from CSS ::before content."),
]
QUERIES = [
    "how do i fix the empty feed in the build script",
    "why is the onion header missing from the cache control block",
    "does the release signing script exit when a relay fails",
]


def fake_embed(text, dim=16):
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    return rng.standard_normal(dim)


def build():
    kw = KeywordIndex()
    kw.add(DOCS)
    ids = [d[0] for d in DOCS]
    dense = DenseIndex(ids, np.stack([fake_embed(d[2]) for d in DOCS]))
    return kw, dense


def test_and_quoted_leg_is_empty():
    kw, _ = build()
    for q in QUERIES:
        assert kw.search(fts_query(q, "and_quoted"), 10) == []
        assert kw.search(fts_query(q, "or_bm25"), 10) != []


def test_ceiling_flags_dead_leg():
    kw, dense = build()
    dead = HybridRetriever(kw, dense, fts_mode="and_quoted")
    live = HybridRetriever(kw, dense, fts_mode="or_bm25")
    for q in QUERIES:
        qv = fake_embed(q)
        s, r = dead.retrieve(q, qv)
        rep = ceiling_report(s, r)
        assert rep.at_ceiling and rep.empty_legs == ["keyword"]
        assert abs(rep.max_score - 1 / RRF_K) < 1e-12
        s, r = live.retrieve(q, qv)
        rep = ceiling_report(s, r)
        assert not rep.empty_legs


def test_rrf_two_legs_beats_ceiling():
    scores, ranks = rrf_fuse({"a": ["x", "y"], "b": ["y", "z"]})
    assert scores["y"] > 1 / RRF_K >= scores["x"]
    rep = ceiling_report(scores, ranks)
    assert rep.multi_leg_docs == 1 and not rep.at_ceiling


if __name__ == "__main__":
    test_and_quoted_leg_is_empty()
    test_ceiling_flags_dead_leg()
    test_rrf_two_legs_beats_ceiling()
    print("ok")
