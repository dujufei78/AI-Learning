"""
RAG 语义检索接口：
  POST /api/v1/search/query   输入自然语言问题，返回 AI 生成的答案 + 引用来源
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.document import SearchRequest, SearchResponse, SourceChunk
from app.services.rag_service import rag_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "/query",
    response_model=SearchResponse,
    summary="RAG 语义检索问答",
    description=(
        "输入自然语言问题，系统会从已索引文档中检索最相关的内容片段，"
        "再由 LLM 根据这些片段生成准确答案，并附上引用来源。"
    ),
)
async def query(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    result = await rag_service.query(db, request.query, request.top_k)
    return SearchResponse(
        query=request.query,
        answer=result["answer"],
        model=result["model"],
        sources=[SourceChunk(**s) for s in result["sources"]],
    )

