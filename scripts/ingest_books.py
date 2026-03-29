from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal, init_db
from app.services.chunk_service import ChunkService
from app.services.document_parser import DocumentParser
from app.services.embedding_service import EmbeddingService


def discover_books(root: Path) -> list[Path]:
    supported = {".pdf", ".epub", ".txt"}
    return sorted([p for p in root.iterdir() if p.is_file() and p.suffix.lower() in supported])


def main() -> None:
    settings = get_settings()
    source_dir = Path(settings.book_source_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Book source dir not found: {source_dir}")

    init_db()

    parser = DocumentParser()
    chunker = ChunkService(settings.chunk_size, settings.chunk_overlap)
    embedder = EmbeddingService()

    books = discover_books(source_dir)
    print(f"发现文档：{len(books)}")

    db = SessionLocal()
    try:
        for path in books:
            existing = db.scalar(select(Document).where(Document.source_path == str(path)))
            if existing:
                print(f"跳过已导入：{path.name}")
                continue

            pages = parser.parse(path)
            chunks = chunker.split_pages(pages)

            document = Document(
                title=path.stem,
                source_path=str(path),
                file_type=path.suffix.lower().lstrip("."),
            )
            db.add(document)
            db.flush()

            for idx, item in enumerate(chunks):
                embedding = embedder.embed_text(item["content"])
                db.add(
                    Chunk(
                        document_id=document.id,
                        chunk_index=idx,
                        page_label=item["page_label"],
                        content=item["content"],
                        embedding=embedding,
                    )
                )

            db.commit()
            print(f"已导入：{path.name}，chunks={len(chunks)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
