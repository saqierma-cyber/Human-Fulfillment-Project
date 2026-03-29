import httpx
from openai import OpenAI

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.llm_embedding_model
        self.enabled = bool(settings.llm_api_key and settings.llm_embedding_model)
        self.client = None
        if self.enabled:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                http_client=httpx.Client(timeout=120.0, trust_env=False),
            )

    def embed_text(self, text: str) -> list[float] | None:
        if not self.enabled or self.client is None:
            return None

        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding
