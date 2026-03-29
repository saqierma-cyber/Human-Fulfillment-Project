import re
from collections import defaultdict

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Chunk, Document, RetrievalLog
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()

    def search(self, question: str, top_k: int | None = None, extra_terms: list[str] | None = None) -> list[dict]:
        top_k = top_k or self.settings.top_k
        query_embedding = self.embedding_service.embed_text(question)
        used_embedding = query_embedding is not None

        if used_embedding:
            stmt: Select = (
                select(Chunk, Document)
                .join(Document, Document.id == Chunk.document_id)
                .where(Chunk.embedding.is_not(None))
                .order_by(Chunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
        else:
            keywords = self._build_search_terms(question, extra_terms or [])
            conditions = [Chunk.content.ilike(f"%{kw[:20]}%") for kw in keywords[:8]]
            conditions.extend([Document.title.ilike(f"%{kw[:20]}%") for kw in keywords[:6]])
            stmt = (
                select(Chunk, Document)
                .join(Document, Document.id == Chunk.document_id)
                .where(or_(*conditions))
                .limit(self.settings.retrieval_candidate_limit)
            )

        rows = self.db.execute(stmt).all()
        if not used_embedding and not rows and extra_terms:
            fallback_terms = self._theme_fallback_terms(question, extra_terms)
            fallback_conditions = [Chunk.content.ilike(f"%{kw[:20]}%") for kw in fallback_terms[:8]]
            fallback_conditions.extend([Document.title.ilike(f"%{kw[:20]}%") for kw in fallback_terms[:6]])
            fallback_stmt = (
                select(Chunk, Document)
                .join(Document, Document.id == Chunk.document_id)
                .where(or_(*fallback_conditions))
                .limit(self.settings.retrieval_candidate_limit)
            )
            rows = self.db.execute(fallback_stmt).all()
        self.db.add(RetrievalLog(query_text=question, used_embedding=used_embedding))
        self.db.commit()

        if used_embedding:
            ranked = rows[:top_k]
        else:
            ranked = self._rerank_keyword_results(question, rows, top_k, extra_terms or [])

        return [
            {
                "document_title": document.title,
                "page_label": chunk.page_label,
                "content": chunk.content,
            }
            for chunk, document in ranked
        ]

    def _build_search_terms(self, question: str, extra_terms: list[str]) -> list[str]:
        extracted = self._extract_keywords(question)
        prioritized: list[str] = []

        # 先把主题扩展词放到前面，避免被长句片段挤掉。
        for term in extra_terms:
            term = term.strip()
            if 2 <= len(term) <= 12:
                prioritized.append(term)

        # 再放更适合检索的短中文词。
        for term in extracted:
            if 2 <= len(term) <= 6:
                prioritized.append(term)

        # 最后补少量更长的片段，用于兜底。
        for term in extracted:
            if 7 <= len(term) <= 12:
                prioritized.append(term)

        if not prioritized:
            prioritized.append(question[:20])

        deduped: list[str] = []
        seen = set()
        for term in prioritized:
            if term in seen:
                continue
            seen.add(term)
            deduped.append(term)

        return deduped[:24]

    def _theme_fallback_terms(self, question: str, extra_terms: list[str]) -> list[str]:
        fallback_terms = list(extra_terms)
        fallback_terms.extend(self._extract_keywords(question)[:8])
        deduped: list[str] = []
        seen = set()
        for term in fallback_terms:
            if len(term) < 2 or term in seen:
                continue
            seen.add(term)
            deduped.append(term)
        return deduped[:16]

    def _extract_keywords(self, question: str) -> list[str]:
        stop_terms = {
            "怎么", "如何", "为什么", "是不是", "这个", "那个", "这样", "那样",
            "事情", "自己", "我们", "他们", "你们", "然后", "现在", "已经", "如果",
            "应该", "可以", "一个", "一些", "因为", "所以", "就是", "但是", "还是",
            "什么", "时候", "一下", "一种", "用户", "分析", "后续", "视角",
            "虽然", "还是", "但是", "觉得", "不知道", "什么都", "现在虽然", "想按自己",
        }

        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", question.lower())
        terms: list[str] = []

        ascii_terms = re.findall(r"[a-z0-9_]{2,}", normalized)
        terms.extend(ascii_terms)

        chinese_spans = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
        for span in chinese_spans:
            if span not in stop_terms and len(span) <= 12:
                terms.append(span)

            max_n = min(4, len(span))
            for n in range(2, max_n + 1):
                for idx in range(0, len(span) - n + 1):
                    token = span[idx : idx + n]
                    if token not in stop_terms:
                        terms.append(token)

        deduped: list[str] = []
        seen = set()
        for term in sorted(terms, key=lambda item: (-len(item), item)):
            if len(term) < 2:
                continue
            if term in seen:
                continue
            seen.add(term)
            deduped.append(term)

        return deduped[:24]

    def _rerank_keyword_results(
        self,
        question: str,
        rows: list[tuple[Chunk, Document]],
        top_k: int,
        extra_terms: list[str],
    ) -> list[tuple[Chunk, Document]]:
        keywords = self._extract_keywords(question)
        keywords.extend(extra_terms)
        keywords = list(dict.fromkeys(keywords))
        scored: list[tuple[float, Chunk, Document]] = []

        for chunk, document in rows:
            score = self._score_keyword_match(question, keywords, chunk.content, document.title)
            if score > 0:
                scored.append((score, chunk, document))

        scored.sort(key=lambda item: item[0], reverse=True)

        per_doc_count: dict[int, int] = defaultdict(int)
        selected: list[tuple[Chunk, Document]] = []
        for _, chunk, document in scored:
            if per_doc_count[document.id] >= self.settings.retrieval_max_per_document:
                continue
            selected.append((chunk, document))
            per_doc_count[document.id] += 1
            if len(selected) >= top_k:
                break

        return selected

    def _score_keyword_match(self, question: str, keywords: list[str], content: str, title: str) -> float:
        score = 0.0
        content_lower = content.lower()
        title_lower = title.lower()
        question_lower = question.lower().strip()

        if question_lower and question_lower in content_lower:
            score += 20.0

        for term in keywords:
            title_hits = title_lower.count(term)
            content_hits = content_lower.count(term)
            if not title_hits and not content_hits:
                continue

            score += title_hits * (6.0 + len(term) * 0.5)
            score += min(content_hits, 3) * (2.0 + len(term) * 0.35)

        # 适度压低“全集/合集/套装”类大文档，避免长期盖过单本书
        if any(flag in title for flag in ("全集", "合集", "套装", "全23册", "共27册")):
            score *= 0.75

        if len(content) < 80:
            score *= 0.6

        return score
