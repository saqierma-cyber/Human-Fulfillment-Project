from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal, init_db
from app.services.chunk_service import ChunkService
from app.services.document_parser import DocumentParser
from app.services.embedding_service import EmbeddingService


def main() -> None:
    settings = get_settings()
    init_db()

    parser = DocumentParser()
    chunker = ChunkService(settings.chunk_size, settings.chunk_overlap)
    embedder = EmbeddingService()

    db = SessionLocal()
    try:
        docs = db.execute(
            select(Document)
            .outerjoin(Chunk, Chunk.document_id == Document.id)
            .group_by(Document.id)
            .having(func.count(Chunk.id) == 0)
        ).scalars().all()

        print(f"待补录 zero-chunk 文档：{len(docs)}")

        for document in docs:
            path = Path(document.source_path)
            if not path.exists():
                print(f"跳过不存在文件：{document.source_path}")
                continue

            pages = parser.parse(path)
            chunks = chunker.split_pages(pages)
            if not chunks:
                print(f"OCR 后仍无文本：{path.name}")
                continue

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
            print(f"已补录：{path.name}，chunks={len(chunks)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
