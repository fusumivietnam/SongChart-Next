from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Iterator

import cocoindex as coco
from cocoindex.connectors import localfs, sqlite
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from numpy.typing import NDArray

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CORPUS = Path(os.environ.get("COCOINDEX_SPIKE_CORPUS", ".cocoindex-spike/corpus")).resolve()
DATABASE = Path(os.environ.get("COCOINDEX_SPIKE_DB", ".cocoindex-spike/index.sqlite")).resolve()
CHUNK_SIZE = 2400
CHUNK_OVERLAP = 400

SQLITE_DB = coco.ContextKey[sqlite.ManagedConnection]("songchart_repo_context_db")
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("songchart_repo_context_embedder", detect_change=True)


@coco.lifespan
def coco_lifespan(builder: coco.EnvironmentBuilder) -> Iterator[None]:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite.managed_connection(DATABASE, load_vec=True) as conn:
        builder.provide(SQLITE_DB, conn)
        builder.provide(EMBEDDER, SentenceTransformerEmbedder(MODEL))
        yield


@dataclass
class RepoChunk:
    chunk_id: str
    path: str
    start_offset: int
    end_offset: int
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


def _iter_chunks(text: str):
    step = CHUNK_SIZE - CHUNK_OVERLAP
    if len(text) <= CHUNK_SIZE:
        yield 0, len(text), text
        return
    for start in range(0, len(text), step):
        end = min(len(text), start + CHUNK_SIZE)
        yield start, end, text[start:end]
        if end == len(text):
            break


def _relative_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(CORPUS).as_posix()
    except ValueError as exc:
        raise ValueError(f"indexed file escaped staged corpus: {resolved}") from exc


@coco.fn(memo=True)
async def process_file(file: FileLike, table: sqlite.TableTarget[RepoChunk]) -> None:
    text = await file.read_text()
    relative_path = _relative_repo_path(Path(file.file_path.path))
    embedder = coco.use_context(EMBEDDER)
    for start, end, chunk_text in _iter_chunks(text):
        chunk_id = hashlib.sha256(f"{relative_path}:{start}:{end}".encode()).hexdigest()
        table.declare_row(
            row=RepoChunk(
                chunk_id=chunk_id,
                path=relative_path,
                start_offset=start,
                end_offset=end,
                text=chunk_text,
                embedding=await embedder.embed(chunk_text),
            )
        )


@coco.fn
async def app_main() -> None:
    table = await sqlite.mount_table_target(
        SQLITE_DB,
        "repo_chunks",
        await sqlite.TableSchema.from_class(RepoChunk, primary_key=["chunk_id"]),
    )
    files = localfs.walk_dir(
        CORPUS,
        recursive=True,
        path_matcher=PatternFilePathMatcher(
            included_patterns=[
                "**/*.md", "**/*.json", "**/*.py", "**/*.php",
                "**/*.ts", "**/*.tsx", "**/*.yml", "**/*.yaml",
            ]
        ),
        live=False,
    )
    await coco.mount_each(process_file, files.items(), table)


app = coco.App(coco.AppConfig(name="SongChartRepoContextSpike"), app_main)
