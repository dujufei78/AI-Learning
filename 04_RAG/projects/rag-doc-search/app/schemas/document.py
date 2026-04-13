from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Document ─────────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    """文档上传/查询的响应体。"""
    id: int
    uuid: str
    original_filename: str
    file_type: str
    file_size: Optional[int] = None
    total_chunks: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class DeleteResponse(BaseModel):
    message: str
    document_id: int


# ── Search ────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="自然语言问题")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="返回的相似块数量（覆盖默认值）")


class SourceChunk(BaseModel):
    content: str
    document_name: str
    page_number: Optional[int] = None
    similarity: float


class SearchResponse(BaseModel):
    query: str
    answer: str
    model: str
    sources: List[SourceChunk]

