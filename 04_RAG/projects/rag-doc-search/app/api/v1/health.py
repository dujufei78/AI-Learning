"""
健康检查接口：
  GET /api/v1/health   返回服务状态、版本信息及数据库连接状态
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="服务健康检查")
async def health_check(db: AsyncSession = Depends(get_db)):
    # 检测数据库连通性
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status":   "ok",
        "app":      settings.APP_NAME,
        "version":  settings.APP_VERSION,
        "database": db_status,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_model":    settings.EMBEDDING_MODEL,
        "llm_model":          settings.LLM_MODEL,
    }

