from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "曾仕强视角分析智能体"
    app_env: str = "local"
    debug: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/zeng_agent"

    llm_api_key: str = ""
    llm_base_url: str = "https://api.minimaxi.com/v1"
    llm_chat_model: str = ""
    llm_embedding_model: str = ""
    embedding_dimensions: int = 1536

    book_source_dir: str = "/Users/binggan/Desktop/曾仕强/电子书籍"
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 8
    retrieval_candidate_limit: int = 120
    retrieval_max_per_document: int = 2
    ocr_enabled: bool = False
    ocr_language: str = "chi_sim+eng"
    ocr_pdf_zoom: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
