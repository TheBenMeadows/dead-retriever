#!/usr/bin/env python3
"""Kaggle GPU kernel for the dead-retriever BEIR evaluation.

Kaggle runs this file with no arguments. It
  1. clones TheBenMeadows/dead-retriever at PINNED_COMMIT,
  2. installs the dependencies pinned in scripts/beir_run.py's inline header
     (transformers>=4.44,<4.50 among them), keeping the image's CUDA torch,
  3. downloads each BEIR dataset through ir_datasets,
  4. runs scripts/beir_run.py (all six conditions) for every dataset x encoder,
  5. writes <tag>.json and <tag>.perquery.jsonl per run into <out>/results/,
     plus manifest.json, ndcg10.md and one log per run into <out>/.

<out> is /kaggle/working on Kaggle, ./kaggle-out elsewhere.

A wall-clock deadline (--deadline-minutes, default 690) is counted from the
start of this script and handed to every beir_run.py invocation, which checks
it inside its per-query loop, writes partial results and exits 0. Runs not yet
started when the deadline passes are recorded as skipped; this script then
exits 0. It exits 1 if any run failed.

    python kaggle/run.py                       # full: SciFact + NFCorpus, both encoders
    python kaggle/run.py --smoke               # SciFact, bge, 5 queries
    python kaggle/run.py --smoke --limit-queries 20 --models nomic-ai/nomic-embed-text-v1.5
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

T0 = time.time()

REPO_URL = "https://github.com/TheBenMeadows/dead-retriever.git"
PINNED_COMMIT = "031d657fcb218a97020774823dee16914aed3361"
DATASETS = ("beir/scifact/test", "beir/nfcorpus/test", "beir/arguana", "beir/scidocs",
            "beir/fiqa/test", "beir/trec-covid")
MODELS = ("BAAI/bge-base-en-v1.5", "nomic-ai/nomic-embed-text-v1.5", "intfloat/e5-base-v2")
# nomic accepts 8,192 tokens; at the runner default of 64 its longest batches
# exhaust a T4 on SciDocs, FiQA and TREC-COVID. The other encoders stop at 512.
MODEL_BATCH = {"nomic-ai/nomic-embed-text-v1.5": 8}
CONDITIONS = ("bm25_and", "bm25_or_raw", "bm25_or", "dense", "hybrid_and", "hybrid_or")
ON_KAGGLE = Path("/kaggle/working").is_dir()
TORCH_CPU_INDEX = "https://download.pytorch.org/whl/cpu"


def log(msg):
    print(f"[run.py +{time.time() - T0:7.1f}s] {msg}", flush=True)


def sh(cmd, **kw):
    log("$ " + " ".join(str(c) for c in cmd))
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def checkout(repo_dir, commit):
    """Shallow fetch of exactly one commit; refuses to proceed on a mismatch."""
    if not (repo_dir / ".git").is_dir():
        repo_dir.mkdir(parents=True, exist_ok=True)
        sh(["git", "-C", repo_dir, "init", "-q"])
        sh(["git", "-C", repo_dir, "remote", "add", "origin", REPO_URL])
    sh(["git", "-C", repo_dir, "fetch", "-q", "--depth", "1", "origin", commit])
    sh(["git", "-C", repo_dir, "checkout", "-q", "--force", "FETCH_HEAD"])
    head = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    if head != commit:
        raise SystemExit(f"checked out {head}, expected {commit}")
    return head


def header_dependencies(script):
    """The `dependencies` list from a PEP 723 `# /// script` block."""
    lines, inside = [], False
    for line in script.read_text().splitlines():
        if line.strip() == "# /// script":
            inside = True
        elif inside and line.strip() == "# ///":
            break
        elif inside:
            lines.append(line[2:] if line.startswith("# ") else line.lstrip("#"))
    block = "\n".join(lines)
    try:
        import tomllib
        return list(tomllib.loads(block)["dependencies"])
    except ImportError:
        return json.loads(re.search(r"^dependencies\s*=\s*(\[.*?\])", block, re.M | re.S).group(1))


def importable(module):
    return subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True).returncode == 0


def pip_install(specs, extra=()):
    sh([sys.executable, "-m", "pip", "install", "--no-input", "--disable-pip-version-check",
        "--progress-bar", "off", *extra, *specs])


def install(repo_dir):
    """Install the runner's pinned dependencies. torch is taken from the image
    when present (Kaggle's CUDA build); otherwise the CPU wheel the header names
    is tried first. pytrec_eval ships only an sdist whose build needs network
    access to the trec_eval sources; if it fails to build, pytrec-eval-terrier
    (same C extension, published as wheels, same import name) is installed."""
    deps = header_dependencies(repo_dir / "scripts" / "beir_run.py")
    if not any(re.match(r"transformers\b.*<\s*4\.50", d) for d in deps):
        raise SystemExit(f"transformers<4.50 pin missing from runner header: {deps}")
    torch_specs = [d for d in deps if re.match(r"torch\b", d)]
    rest = [d for d in deps if d not in torch_specs]
    if torch_specs and not importable("torch"):
        try:
            pip_install(torch_specs, ["--index-url", TORCH_CPU_INDEX])
        except subprocess.CalledProcessError:
            log("CPU torch index unreachable; installing torch from the default index")
            pip_install(torch_specs)
    try:
        pip_install(rest)
    except subprocess.CalledProcessError:
        log("install failed; retrying with pytrec-eval-terrier in place of pytrec_eval")
        pip_install(["pytrec-eval-terrier" if re.match(r"pytrec_eval\b", d) else d for d in rest])


def environment_report():
    """Versions and device, from a fresh interpreter so the freshly installed
    packages are the ones reported. Fails if transformers is not <4.50."""
    code = r"""
import json, torch, transformers, sentence_transformers, numpy, ir_datasets, pytrec_eval
info = {"python": __import__("sys").version.split()[0], "torch": torch.__version__,
        "transformers": transformers.__version__, "sentence_transformers": sentence_transformers.__version__,
        "numpy": numpy.__version__, "ir_datasets": ir_datasets.__version__,
        "cuda_available": torch.cuda.is_available(), "device": "cpu"}
if torch.cuda.is_available():
    info["device"] = torch.cuda.get_device_name(0)
    try:
        x = torch.ones(64, 64, device="cuda"); float((x @ x).sum()); info["cuda_ok"] = True
    except Exception as e:  # e.g. a GPU architecture the installed torch was not built for
        info["cuda_ok"] = False; info["cuda_error"] = repr(e)
print(json.dumps(info))
"""
    out = subprocess.run([sys.executable, "-c", code], check=True, stdout=subprocess.PIPE, text=True).stdout
    info = json.loads(out.strip().splitlines()[-1])
    major, minor = (int(p) for p in info["transformers"].split(".")[:2])
    if (major, minor) >= (4, 50):
        raise SystemExit(f"transformers {info['transformers']} installed; the pin is <4.50")
    return info


def download(dataset, env):
    """Fetch docs, queries and qrels through ir_datasets; report counts and
    the on-disk size of the dataset directory."""
    code = (
        "import ir_datasets, json, sys\n"
        "ds = ir_datasets.load(sys.argv[1])\n"
        "n = {'docs': sum(1 for _ in ds.docs_iter()), 'queries': sum(1 for _ in ds.queries_iter()),"
        " 'qrels': sum(1 for _ in ds.qrels_iter())}\n"
        "print(json.dumps(n))\n")
    out = subprocess.run([sys.executable, "-c", code, dataset], check=True, env=env,
                         stdout=subprocess.PIPE, text=True).stdout
    counts = json.loads(out.strip().splitlines()[-1])
    root = Path(env["IR_DATASETS_HOME"]) / dataset.split("/")[0] / dataset.split("/")[1]
    size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) if root.exists() else None
    return {**counts, "bytes_on_disk": size}


def tag(dataset, model):
    return dataset.replace("/", "_") + "__" + model.replace("/", "_")


def ndcg_table(runs):
    cols = [r for r in runs if r.get("summary")]
    if not cols:
        return "(no results)\n"
    head = ["condition"] + [f"{r['dataset'].split('/')[1]} / {r['model'].split('/')[1]}"
                            + (" (partial)" if r["summary"].get("partial") else "") for r in cols]
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] + ["---:"] * len(cols)) + "|"]
    for cond in CONDITIONS:
        cells = []
        for r in cols:
            c = r["summary"]["conditions"].get(cond)
            cells.append(f"{c['ndcg_cut_10']:.3f}" if c else "-")
        lines.append(f"| {cond} | " + " | ".join(cells) + " |")
    lines.append("| n_queries | " + " | ".join(str(r["summary"]["n_queries"]) for r in cols) + " |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true",
                    help="SciFact with bge only, 5 queries unless --limit-queries is given")
    ap.add_argument("--datasets", nargs="+", default=None)
    ap.add_argument("--models", nargs="+", default=None)
    ap.add_argument("--limit-queries", type=int, default=None, help="0 = all queries")
    ap.add_argument("--deadline-minutes", type=float, default=690.0,
                    help="wall-clock budget from this script's start (Kaggle kills at 720)")
    ap.add_argument("--batch", type=int, default=64, help="encoder batch size (runner default)")
    ap.add_argument("--commit", default=PINNED_COMMIT)
    ap.add_argument("--repo-dir", default=None, help="checkout location (default <work>/dead-retriever)")
    ap.add_argument("--work", default="/tmp/dead-retriever" if ON_KAGGLE else "kaggle-work",
                    help="clone, caches and datasets (not part of the kernel output)")
    ap.add_argument("--out", default="/kaggle/working" if ON_KAGGLE else "kaggle-out")
    ap.add_argument("--skip-install", action="store_true")
    a = ap.parse_args()

    datasets = a.datasets or (DATASETS[:1] if a.smoke else DATASETS)
    models = a.models or (MODELS[:1] if a.smoke else MODELS)
    limit = a.limit_queries if a.limit_queries is not None else (5 if a.smoke else 0)
    deadline_at = T0 + 60.0 * a.deadline_minutes

    work, out = Path(a.work).resolve(), Path(a.out).resolve()
    repo_dir = Path(a.repo_dir).resolve() if a.repo_dir else work / "dead-retriever"
    (out / "results").mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "IR_DATASETS_HOME": str(work / "ir_datasets"), "HF_HOME": str(work / "hf"),
           "PYTHONUNBUFFERED": "1", "TOKENIZERS_PARALLELISM": "false"}

    manifest = {"repo": REPO_URL, "commit": None, "smoke": a.smoke, "datasets": list(datasets),
                "models": list(models), "limit_queries": limit, "deadline_minutes": a.deadline_minutes,
                "batch": a.batch, "model_batch": MODEL_BATCH, "started_unix": T0, "on_kaggle": ON_KAGGLE, "environment": None,
                "downloads": {}, "runs": []}
    manifest_path = out / "manifest.json"

    def save():
        manifest["elapsed_s"] = time.time() - T0
        manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")

    manifest["commit"] = checkout(repo_dir, a.commit)
    save()
    if not a.skip_install:
        install(repo_dir)
    manifest["environment"] = info = environment_report()
    log(f"environment: {json.dumps(info)}")
    if ON_KAGGLE and not info.get("cuda_ok"):
        log("WARNING: no usable GPU; encoding will run on CPU")
    save()

    for ds in datasets:
        try:
            manifest["downloads"][ds] = d = download(ds, env)
        except subprocess.CalledProcessError:
            manifest["downloads"][ds] = {"error": "download failed; see the traceback above"}
            manifest["status"] = "failed"
            save()
            raise SystemExit(f"download of {ds} failed")
        log(f"{ds}: {d}")
        if d["bytes_on_disk"] and d["bytes_on_disk"] > 2 * 1024 ** 3:
            log(f"WARNING: {ds} occupies {d['bytes_on_disk'] / 1024 ** 3:.2f} GiB")
    save()

    failed, stopped = False, False
    for ds in datasets:
        for model in models:
            rec = {"dataset": ds, "model": model, "tag": tag(ds, model), "status": None}
            manifest["runs"].append(rec)
            if stopped or time.time() >= deadline_at:
                rec["status"], stopped = "skipped_deadline", True
                save()
                continue
            cmd = [sys.executable, repo_dir / "scripts" / "beir_run.py", "--dataset", ds, "--model", model,
                   "--out", out / "results", "--cache", work / "cache", "--batch", MODEL_BATCH.get(model, a.batch),
                   "--limit-queries", limit, "--deadline-minutes", a.deadline_minutes, "--clock-start", T0]
            t1 = time.time()
            log_path = out / "logs" / f"{rec['tag']}.log"
            log(f"run {ds} x {model} (log: {log_path})")
            with log_path.open("w") as lf:
                proc = subprocess.Popen([str(c) for c in cmd], cwd=repo_dir, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
                for line in proc.stdout:
                    sys.stdout.write(line)
                    lf.write(line)
                rc = proc.wait()
            rec["returncode"], rec["seconds"] = rc, time.time() - t1
            summary = out / "results" / f"{rec['tag']}.json"
            if rc == 0 and summary.exists():
                rec["summary"] = json.loads(summary.read_text())
                if rec["summary"].get("partial"):
                    rec["status"], stopped = "partial_deadline", True
                else:
                    rec["status"] = "complete"
            else:
                rec["status"], failed = "failed", True
            log(f"{rec['tag']}: {rec['status']} in {rec['seconds']:.0f}s")
            save()

    table = ndcg_table(manifest["runs"])
    (out / "ndcg10.md").write_text(table)
    for r in manifest["runs"]:
        r.pop("summary", None)
    manifest["status"] = "failed" if failed else ("deadline" if stopped else "complete")
    save()
    print("\nnDCG@10\n\n" + table, flush=True)
    log(f"done: {manifest['status']}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
