# Kaggle GPU kernel for the BEIR runs

`run.py` is a Kaggle script kernel. It clones this repository at a pinned commit
(`PINNED_COMMIT` in `run.py`), installs the dependencies pinned in the inline
header of `scripts/beir_run.py` (`transformers>=4.44,<4.50`,
`sentence-transformers>=3,<4`, `ir_datasets`, `pytrec_eval`, `numpy`, `einops`),
downloads the BEIR test splits through `ir_datasets`, and runs all six conditions
(`bm25_and`, `bm25_or_raw`, `bm25_or`, `dense`, `hybrid_and`, `hybrid_or`) for every
dataset and encoder:

| datasets | encoders |
|---|---|
| `beir/scifact/test`, `beir/nfcorpus/test` | `BAAI/bge-base-en-v1.5`, `nomic-ai/nomic-embed-text-v1.5` |

The image's own CUDA build of torch is kept, and only the other packages are installed.
If the image has no torch, the CPU wheel named in the header is installed. If
`pytrec_eval` fails to build from its sdist, `pytrec-eval-terrier` (same C
extension, same import name, published as wheels) is installed in its place.
`run.py` stops with an error if the installed `transformers` is 4.50 or later.

## Output (`/kaggle/working/`)

| path | content |
|---|---|
| `results/<tag>.json` | per-condition nDCG@10, Recall@100, mean query time and fusion diagnostics; same keys as `results/*.json` in the repository |
| `results/<tag>.perquery.jsonl` | one row per (query, condition) with the diagnostics |
| `ndcg10.md` | nDCG@10 table, conditions by run |
| `manifest.json` | commit, package versions, GPU name, dataset sizes, per-run status and timing |
| `logs/<tag>.log` | full stdout/stderr of each `beir_run.py` invocation |

`<tag>` is `beir_<dataset>_test__<org>_<model>`, the same naming `results/` uses.
To compare against the committed numbers, use
`diff <(jq -S '.conditions | map_values({ndcg_cut_10, recall_100})' out/results/<tag>.json) <(jq -S '.conditions | map_values({ndcg_cut_10, recall_100})' results/<tag>.json)`
(timing fields differ by construction).
GPU and CPU embeddings differ at float precision, so small differences in the
third or fourth decimal are expected. Larger differences are not.

## Deadline

Kaggle stops a kernel at 12 h. `--deadline-minutes` (default 690) is counted from
the start of `run.py` and passed to every `beir_run.py` call as
`--deadline-minutes` plus `--clock-start`. `beir_run.py` checks it before encoding
and inside the per-query loop. When it fires, the runner evaluates the queries
finished so far and writes `<tag>.json` with `"partial": true`, a `deadline`
record and `n_queries_evaluated` on the interrupted condition. It flushes the
per-query JSONL and exits 0. `run.py` marks later runs `skipped_deadline` and
exits 0. The summary is also rewritten after each condition, marked
`"partial": true` until the run finishes, so a hard kill loses at most one
condition. A single encode pass can't be interrupted, so the deadline has to
leave room for one.

Kernel status: `run.py` exits 0 when all runs complete or the deadline stops
them, and 1 if any run or download fails.

## Push and poll (from the owner's machine)

Requires the Kaggle CLI (`pip install kaggle`) and your API token, exported in
your own shell as `KAGGLE_API_TOKEN`. Never commit it.

```sh
kaggle kernels push -p kaggle/
kaggle kernels status thebenmeadows/dead-retriever-beir
kaggle kernels output thebenmeadows/dead-retriever-beir -p out/
```

`kernel-metadata.json` sets `enable_gpu` and `enable_internet`. Internet is
required for the clone, the pip installs, the BEIR download (from
`public.ukp.informatik.tu-darmstadt.de`) and the Hugging Face model weights. The
nomic model also loads remote code (`trust_remote_code=True`).

`manifest.json` records `environment.device` and `environment.cuda_ok`. If Kaggle
assigns a GPU that the image's torch was not built for, `cuda_ok` is false and
`cuda_error` holds the exception. Check this before trusting the timing columns.
The numbers are computed the same way on CPU, only more slowly.

The pinned commit (`699d7dd`) is on branch `kaggle/beir-kernel`. GitHub serves a
fetch by SHA only while the commit is reachable from some ref. If the branch
is squash-merged and deleted, set `PINNED_COMMIT` to the corresponding commit on
`main` before pushing the kernel again.

## Local use

```sh
python kaggle/run.py --smoke                     # SciFact, bge, first 5 queries, CPU is fine
python kaggle/run.py --smoke --limit-queries 20 --models nomic-ai/nomic-embed-text-v1.5
python kaggle/run.py --deadline-minutes 30       # full grid with a 30-minute budget
```

Outside Kaggle the clone, caches and datasets go to `kaggle-work/` and the
outputs to `kaggle-out/`. Both are git-ignored. Use a virtualenv: `run.py`
installs packages into the interpreter that runs it.

## Smoke test (CPU, 5 queries)

**Not completed.** The build environment (a cloud VM without a GPU) has a network
policy that denies `public.ukp.informatik.tu-darmstadt.de` (BEIR zips),
`huggingface.co` (encoder weights) and `download.pytorch.org` (CPU torch index).
Command, run under Python 3.11 in a fresh virtualenv:

```sh
python kaggle/run.py --smoke --limit-queries 5
```

What ran and was checked:

- Shallow fetch of `699d7dd5f86b34f0995f3c688f5930be5063644e` from GitHub and the HEAD check.
- Dependency install from the runner header. The CPU torch index was unreachable,
  so the fallback to PyPI torch was used. `pytrec_eval` failed to build from its
  sdist, so the fallback to `pytrec-eval-terrier` was used. Resulting versions:
  Python 3.11.17, torch 2.14.1, transformers 4.49.0, sentence-transformers 3.4.1,
  ir_datasets 0.6.3, numpy 2.4.6. `cuda_available` was false.
- Download of `beir/scifact/test` failed with `ProxyError ... Tunnel connection
  failed: 403 Forbidden` for `public.ukp.informatik.tu-darmstadt.de`, and `run.py`
  exited 1. No nDCG@10 table was produced.

Checked separately, with no network and a synthetic 200-document corpus where
`load`/`embed_all` were replaced by stubs (these are not BEIR results):

- With a 0.6 s deadline, the check fired inside the `bm25_and` per-query loop
  after 28 of 40 queries. `<tag>.json` carried `"partial": true` and
  `n_queries_evaluated: 28`, the JSONL held 28 rows, and the exit code was 0.
- Without a deadline, all 6 conditions finished. The summary's top-level keys and
  per-condition keys matched the committed `results/` files exactly, and the
  JSONL held 240 rows.
- `tests/` passed (4 tests).
- The `ndcg10.md` formatter applied to the committed
  `results/beir_scifact_test__BAAI_bge-base-en-v1.5.json` gives dense 0.740 and
  hybrid_or 0.723, matching `paper/main.tex`.

To complete the smoke test, run the command above on any machine that can reach
those three hosts. Then replace this section with the printed table.
