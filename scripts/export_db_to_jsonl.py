from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.models import Document
from app.db.session import SessionLocal


def slugify(name: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", name.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:120] or "untitled"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def export_documents() -> tuple[int, int]:
    data_dir = PROJECT_ROOT / "data"
    parsed_dir = data_dir / "parsed"
    chunks_dir = data_dir / "chunks"
    exports_dir = data_dir / "exports"

    ensure_dir(parsed_dir)
    ensure_dir(chunks_dir)
    ensure_dir(exports_dir)

    db = SessionLocal()
    try:
        documents = db.scalars(
            select(Document)
            .options(selectinload(Document.chunks))
            .order_by(Document.id.asc())
        ).all()

        manifest: list[dict] = []
        total_chunks = 0

        for document in documents:
            ordered_chunks = sorted(document.chunks, key=lambda item: item.chunk_index)
            total_chunks += len(ordered_chunks)

            safe_name = f"{document.id:03d}_{slugify(document.title)}"
            chunk_rows: list[dict] = []
            grouped_pages: dict[str, list[str]] = defaultdict(list)

            for chunk in ordered_chunks:
                chunk_rows.append(
                    {
                        "document_id": document.id,
                        "document_title": document.title,
                        "source_path": document.source_path,
                        "file_type": document.file_type,
                        "chunk_id": chunk.id,
                        "chunk_index": chunk.chunk_index,
                        "page_label": chunk.page_label,
                        "content": chunk.content,
                    }
                )

                page_key = chunk.page_label or f"chunk_{chunk.chunk_index}"
                grouped_pages[page_key].append(chunk.content)

            parsed_rows = [
                {
                    "document_id": document.id,
                    "document_title": document.title,
                    "source_path": document.source_path,
                    "file_type": document.file_type,
                    "page_label": page_label,
                    # 注意：这里是按 page_label 聚合 chunk 的近似页文本，不是原始 parse 结果。
                    "content": "\n\n".join(parts),
                }
                for page_label, parts in grouped_pages.items()
            ]

            chunk_file = chunks_dir / f"{safe_name}.jsonl"
            parsed_file = parsed_dir / f"{safe_name}.jsonl"

            write_jsonl(chunk_file, chunk_rows)
            write_jsonl(parsed_file, parsed_rows)

            manifest.append(
                {
                    "document_id": document.id,
                    "document_title": document.title,
                    "source_path": document.source_path,
                    "file_type": document.file_type,
                    "chunk_count": len(chunk_rows),
                    "parsed_record_count": len(parsed_rows),
                    "chunks_file": str(chunk_file),
                    "parsed_file": str(parsed_file),
                }
            )

        write_jsonl(exports_dir / "documents_manifest.jsonl", manifest)
        return len(documents), total_chunks
    finally:
        db.close()


def main() -> None:
    doc_count, chunk_count = export_documents()
    print(f"已导出 documents={doc_count}, chunks={chunk_count}")
    print(f"parsed 目录：{PROJECT_ROOT / 'data' / 'parsed'}")
    print(f"chunks 目录：{PROJECT_ROOT / 'data' / 'chunks'}")
    print(f"manifest：{PROJECT_ROOT / 'data' / 'exports' / 'documents_manifest.jsonl'}")


if __name__ == "__main__":
    main()
