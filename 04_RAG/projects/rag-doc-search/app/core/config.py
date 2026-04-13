from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────────────────
    APP_NAME: str = "RAG Document Search"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ragdb"

    # ── OpenAI / LLM ──────────────────────────────────────────────────────
    OPENAI_API_KEY: str = "sk-xxxx"
    OPENAI_BASE_URL: Optional[str] = None  # 自定义 Base URL，如阿里云 / Azure

    # ── Embedding ─────────────────────────────────────────────────────────
    # Provider: "openai" 或 "local"（sentence-transformers）
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # openai 默认 1536 维
    EMBEDDING_DIM: int = 1536                         # local 模型改为 768

    # ── LLM 生成 ──────────────────────────────────────────────────────────
    LLM_MODEL: str = "gpt-4o-mini"

    # ── RAG 参数 ──────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 500       # 每个文本块最大字符数
    CHUNK_OVERLAP: int = 50     # 块间重叠字符数
    TOP_K: int = 5              # 检索返回 Top-K 相似块

    # ── 文件上传 ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()

