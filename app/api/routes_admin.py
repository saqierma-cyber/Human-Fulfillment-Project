from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal


router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "book_source_dir": settings.book_source_dir,
        "llm_base_url": settings.llm_base_url,
        "chat_model": settings.llm_chat_model,
    }


@router.get("/stats")
def stats() -> dict:
    db: Session = SessionLocal()
    try:
        document_count = db.scalar(select(func.count(Document.id))) or 0
        chunk_count = db.scalar(select(func.count(Chunk.id))) or 0
    finally:
        db.close()

    return {
        "documents": document_count,
        "chunks": chunk_count,
        "book_source_exists": Path(get_settings().book_source_dir).exists(),
    }

