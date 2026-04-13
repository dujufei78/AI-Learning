"""
FastAPI 应用入口。
访问 http://localhost:8000/docs 查看 Swagger UI。
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import documents, health, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期：
    - 启动时：初始化数据库（建表、启用 pgvector 扩展）、创建上传目录
    - 关闭时：（可在此处释放资源）
    """
    await init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## RAG Document Search API 📄🔍

将 **PDF / Word / Excel** 文档向量化存储，支持用自然语言进行语义检索问答。

### 功能
- 📤 **文档管理**：上传、列举、删除文档，后台异步建立索引
- 🔎 **语义检索**：基于 pgvector 余弦相似度召回最相关内容
- 🤖 **RAG 问答**：LLM 根据检索结果生成准确答案，并附上引用来源

### 快速开始
1. 启动 PostgreSQL（`docker compose up -d`）
2. ��传文档 → `POST /api/v1/documents/upload`
3. 等待状态变为 `ready` → `GET /api/v1/documents`
4. 提问 → `POST /api/v1/search/query`
""",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS（生产环境请缩小 allow_origins 范围）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(health.router,    prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router,    prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} 🚀", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

