from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".cocoindex-spike"
CORPUS = WORK / "corpus"
DB = WORK / "index.sqlite"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ALLOWED = {".md", ".json", ".py", ".php", ".ts", ".tsx", ".yml", ".yaml"}
SOURCES = [
    "README.md", "AGENTS.md", "docs", "governance", "design", "reference",
    "scripts", "tests/governance", "tests/Feature", "app/Http/Controllers", "app/Music",
]


def stage_corpus() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    CORPUS.mkdir(parents=True)
    count = 0
    for source in SOURCES:
        src = ROOT / source
        if not src.exists():
            continue
        candidates = [src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()]
        for path in candidates:
            if path.suffix.lower() not in ALLOWED:
                continue
            relative = path.relative_to(ROOT)
            target = CORPUS / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            count += 1
    return count


def run_update() -> tuple[float, str]:
    env = os.environ.copy()
    env["COCOINDEX_SPIKE_CORPUS"] = str(CORPUS)
    env["COCOINDEX_SPIKE_DB"] = str(DB)
    started = time.perf_counter()
    proc = subprocess.run(
        ["cocoindex", "update", "research/cocoindex/app.py"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        raise RuntimeError(f"cocoindex update failed ({proc.returncode})\n{proc.stdout}")
    return elapsed, proc.stdout[-12000:]


def load_index() -> list[tuple[str, np.ndarray]]:
    rows: list[tuple[str, np.ndarray]] = []
    with sqlite3.connect(DB) as conn:
        for path, embedding in conn.execute("SELECT path, embedding FROM repo_chunks"):
            if isinstance(embedding, memoryview):
                embedding = embedding.tobytes()
            vector = np.frombuffer(embedding, dtype=np.float32).copy()
            norm = float(np.linalg.norm(vector))
            if norm:
                vector /= norm
            rows.append((str(path), vector))
    return rows


def rank_paths(model: SentenceTransformer, rows: list[tuple[str, np.ndarray]], query: str, top_k: int) -> list[str]:
    q = np.asarray(model.encode(query, normalize_embeddings=True), dtype=np.float32)
    best: dict[str, float] = {}
    for path, vector in rows:
        score = float(np.dot(q, vector))
        if score > best.get(path, -2.0):
            best[path] = score
    return [path for path, _ in sorted(best.items(), key=lambda item: (-item[1], item[0]))[:top_k]]


def path_matches(actual: str, expected: str) -> bool:
    return actual == expected or actual.startswith(expected.rstrip("/") + "/")


def evaluate(model: SentenceTransformer, rows: list[tuple[str, np.ndarray]], spec: dict) -> dict:
    authority = []
    for item in spec["authority_questions"]:
        ranked = rank_paths(model, rows, item["q"], 5)
        hit = any(any(path_matches(path, e) for e in item["expect"]) for path in ranked)
        authority.append({"q": item["q"], "hit": hit, "top5": ranked})

    impact = []
    precisions = []
    recalls = []
    for item in spec["impact_probes"]:
        ranked = rank_paths(model, rows, item["q"], 5)
        matched_expected = {e for e in item["expect"] if any(path_matches(path, e) for path in ranked)}
        matched_results = sum(1 for path in ranked if any(path_matches(path, e) for e in item["expect"]))
        precision = matched_results / max(len(ranked), 1)
        recall = len(matched_expected) / len(item["expect"])
        precisions.append(precision)
        recalls.append(recall)
        impact.append({"q": item["q"], "precision_at_5": precision, "recall_at_5": recall, "top5": ranked})

    contradictions = []
    for item in spec["contradiction_probes"]:
        ranked = rank_paths(model, rows, item["q"], 10)
        hit = any(any(path_matches(path, e) for e in item["expect_any"]) for path in ranked)
        contradictions.append({"q": item["q"], "retrieval_hit": hit, "top10": ranked})

    return {
        "authority_hit_rate_at_5": sum(x["hit"] for x in authority) / len(authority),
        "impact_mean_precision_at_5": sum(precisions) / len(precisions),
        "impact_mean_recall_at_5": sum(recalls) / len(recalls),
        "impact_false_positive_proxy": 1.0 - (sum(precisions) / len(precisions)),
        "contradiction_retrieval_hit_rate_at_10": sum(x["retrieval_hit"] for x in contradictions) / len(contradictions),
        "authority_questions": authority,
        "impact_probes": impact,
        "contradiction_probes": contradictions,
    }


def dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(WORK / "benchmark.json"))
    args = parser.parse_args()

    file_count = stage_corpus()
    initial_seconds, initial_log = run_update()

    md = CORPUS / "README.md"
    original_md = md.read_text(encoding="utf-8")
    md.write_text(original_md + "\nCocoIndex incremental markdown probe.\n", encoding="utf-8")
    markdown_seconds, markdown_log = run_update()
    md.write_text(original_md, encoding="utf-8")
    run_update()

    source_candidates = sorted((CORPUS / "app").rglob("*.php"))
    if not source_candidates:
        raise RuntimeError("no staged PHP source available for incremental source probe")
    src = source_candidates[0]
    original_src = src.read_text(encoding="utf-8")
    src.write_text(original_src + "\n// CocoIndex incremental source probe.\n", encoding="utf-8")
    source_seconds, source_log = run_update()
    src.write_text(original_src, encoding="utf-8")
    run_update()

    rows = load_index()
    model = SentenceTransformer(MODEL)
    spec = json.loads((ROOT / "research/cocoindex/questions.json").read_text(encoding="utf-8"))
    quality = evaluate(model, rows, spec)

    output = {
        "schema_version": 1,
        "tool": {
            "name": "cocoindex",
            "version": "1.0.25",
            "upstream_tag_commit": "17c84f1a0f9bc5b0b4e1d8ebabb28bde79c4afa3",
            "license": "Apache-2.0",
            "embedding_model": MODEL,
        },
        "corpus": {"files": file_count, "indexed_chunks": len(rows)},
        "timings_seconds": {
            "initial": round(initial_seconds, 3),
            "incremental_markdown": round(markdown_seconds, 3),
            "incremental_source": round(source_seconds, 3),
        },
        "storage_bytes": {"sqlite": DB.stat().st_size, "spike_workdir": dir_size(WORK)},
        "quality": quality,
        "boundaries": {
            "derived_only": True,
            "production_dependency": False,
            "merge_blocking_semantic_judgement": False,
            "authority_remains_git": True,
        },
        "log_tails": {"initial": initial_log, "incremental_markdown": markdown_log, "incremental_source": source_log},
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ("tool", "corpus", "timings_seconds", "storage_bytes", "quality", "boundaries")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
