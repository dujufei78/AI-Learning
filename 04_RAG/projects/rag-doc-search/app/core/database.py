from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.core.config import settings

# ── 引擎 & Session 工厂 ───────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── ORM Base ──────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── FastAPI 依赖注入 ───────────────────────────────────────────────────────
async def get_db():
    """每次请求创建一个 Session，请求结束后自动关闭。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ── 启动初始化 ────────────────────────────────────────────────────────────
async def init_db():
    """启动时创建 pgvector 扩展并建表（如不存在）。"""
    async with engine.begin() as conn:
        # 启用 pgvector 扩展（需要 superuser 权限，docker postgres 默认有）
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # 根据 ORM 模型自动建表
        from app.models import document  # noqa: F401 — 确保模型被注册
        await conn.run_sync(Base.metadata.create_all)

