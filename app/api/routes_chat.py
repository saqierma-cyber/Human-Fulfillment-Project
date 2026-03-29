import logging

from fastapi import APIRouter, Depends, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import AskRequest, AskResponse, CitationItem, StructuredAnalysis, ThemeInfo
from app.services.analysis_service import AnalysisService
from app.services.retrieval_service import RetrievalService
from app.services.theme_service import ThemeService


router = APIRouter()
logger = logging.getLogger(__name__)


def _empty_analysis(message: str, risk_note: str) -> StructuredAnalysis:
    return StructuredAnalysis(
        event_summary=message,
        key_people=[],
        decision_map=[],
        cause_analysis=[],
        core_conflicts=[],
        zeng_judgment=[],
        predictions=[],
        actions=[],
        risk_note=risk_note,
    )


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, response: Response, db: Session = Depends(get_db)) -> AskResponse:
    theme_service = ThemeService()
    theme = theme_service.classify(payload.question)
    analysis_mode = "unknown"
    analysis_reason = ""

    try:
        retrieval_service = RetrievalService(db)
        citations = retrieval_service.search(payload.question, extra_terms=theme["expanded_terms"])
    except Exception:
        analysis_mode = "retrieval_error"
        analysis_reason = "retrieval-stage-failed"
        response.headers["X-Analysis-Mode"] = analysis_mode
        response.headers["X-Analysis-Reason"] = analysis_reason
        logger.warning("analysis_mode=%s reason=%s question=%s", analysis_mode, analysis_reason, payload.question[:80])
        answer = "检索阶段发生了内部错误，当前先返回安全回退结果。"
        empty_analysis = _empty_analysis(
            message="当前检索阶段失败，暂时无法组织曾仕强视角的分析。",
            risk_note="请先重启后端再试；如果问题持续存在，需要继续检查数据库或检索逻辑。",
        )
        return AskResponse(answer=answer, theme=ThemeInfo(**theme), analysis=empty_analysis, citations=[])

    if not citations:
        analysis_mode = "no_citations"
        analysis_reason = "knowledge-not-hit"
        response.headers["X-Analysis-Mode"] = analysis_mode
        response.headers["X-Analysis-Reason"] = analysis_reason
        logger.info("analysis_mode=%s reason=%s question=%s", analysis_mode, analysis_reason, payload.question[:80])
        answer = "当前知识库里没有检索到直接对应的书中材料。这不等于没有相关观点，更可能是表达方式和书里用词没有对上。"
        empty_analysis = _empty_analysis(
            message="当前没有检索到直接对应的书中段落，建议改写成更短、更明确的人物关系和冲突句式后重试。",
            risk_note="建议把问题拆成“谁和谁的关系、冲突点是什么、你最怕什么、你想得到什么”四部分再提问。",
        )
        return AskResponse(answer=answer, theme=ThemeInfo(**theme), analysis=empty_analysis, citations=[])

    citation_items = [CitationItem(**item) for item in citations]
    try:
        analysis_service = AnalysisService()
        analysis_raw = analysis_service.analyze(payload.question, citations, theme)
        fallback_needed = analysis_service.has_markup_artifacts(analysis_raw)
        analysis = StructuredAnalysis(**analysis_raw)
        if fallback_needed or not any(
            [
                analysis.key_people,
                analysis.decision_map,
                analysis.cause_analysis,
                analysis.core_conflicts,
                analysis.zeng_judgment,
                analysis.predictions,
                analysis.actions,
            ]
        ):
            analysis_mode = "fallback"
            analysis_reason = "empty-or-markup-model-output"
            analysis = StructuredAnalysis(
                **AnalysisService.build_fallback_analysis(
                    payload.question,
                    citations,
                    theme,
                    reason="模型返回内容过空或夹带 HTML 片段，已切换为本地规则回退。",
                )
            )
        else:
            analysis_mode = "model"
            analysis_reason = "model-structured-json"
    except ValidationError:
        analysis_mode = "fallback"
        analysis_reason = "validation-error"
        analysis = StructuredAnalysis(
            **AnalysisService.build_fallback_analysis(
                payload.question,
                citations,
                theme,
                reason="模型返回了非标准结构。",
            )
        )
    except Exception:
        analysis_mode = "fallback"
        analysis_reason = "model-exception"
        analysis = StructuredAnalysis(
            **AnalysisService.build_fallback_analysis(
                payload.question,
                citations,
                theme,
                reason="模型分析阶段出错。",
            )
        )

    response.headers["X-Analysis-Mode"] = analysis_mode
    response.headers["X-Analysis-Reason"] = analysis_reason
    logger.info(
        "analysis_mode=%s reason=%s citations=%s question=%s",
        analysis_mode,
        analysis_reason,
        len(citations),
        payload.question[:80],
    )
    answer = analysis.event_summary
    return AskResponse(answer=answer, theme=ThemeInfo(**theme), analysis=analysis, citations=citation_items)
