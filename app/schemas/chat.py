from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: int | None = None


class CitationItem(BaseModel):
    document_title: str
    page_label: str | None = None
    content: str


class ThemeInfo(BaseModel):
    primary_theme: str
    secondary_themes: list[str]
    matched_terms: list[str]
    expanded_terms: list[str]
    actor_tags: list[str]
    zeng_lens: str


class ActorItem(BaseModel):
    name: str
    role: str
    state: str
    motive: str


class DecisionEdge(BaseModel):
    from_actor: str
    to_actor: str
    relation: str
    tension: str
    note: str


class AnalysisPoint(BaseModel):
    title: str
    detail: str


class PredictionItem(BaseModel):
    trend: str
    probability: str
    signal: str


class ActionItem(BaseModel):
    priority: str
    action: str
    reason: str
    avoid: str


class StructuredAnalysis(BaseModel):
    event_summary: str
    key_people: list[ActorItem]
    decision_map: list[DecisionEdge]
    cause_analysis: list[AnalysisPoint]
    core_conflicts: list[AnalysisPoint]
    zeng_judgment: list[AnalysisPoint]
    predictions: list[PredictionItem]
    actions: list[ActionItem]
    risk_note: str


class AskResponse(BaseModel):
    answer: str
    theme: ThemeInfo
    analysis: StructuredAnalysis
    citations: list[CitationItem]
