"""
文档管理接口：
  POST   /api/v1/documents/upload   上传并异步索引文档
  GET    /api/v1/documents          列举所有已索引文档
  GET    /api/v1/documents/{id}     查询单个文档详情
  DELETE /api/v1/documents/{id}     删除文档（含向量数据）
"""
import os
import uuid

import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_db
from app.models.document import Document
from app.schemas.document import DeleteResponse, DocumentListResponse, DocumentResponse
from app.services.parser import DocumentParser
from app.services.vector_service import vector_service

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "xlsx", "xls", "csv"}

_parser = DocumentParser(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
)


# ── 后台任务：解析 & 向量化 ────────────────────────────────────────────────

async def _index_document(document_id: int, file_path: str, file_type: str):
    """在后台完成文档解析和向量写入，并更新文档状态。"""
    async with AsyncSessionLocal() as db:
        doc = await db.get(Document, document_id)
        try:
            chunks = _parser.parse(file_path, file_type)
            count = await vector_service.store_chunks(db, document_id, chunks)
            doc.status = "ready"
            doc.total_chunks = count
        except Exception as exc:
            doc.status = "failed"
            print(f"[ERROR] 文档 {document_id} 索引失败：{exc}")
        finally:
            await db.commit()


# ── 路由 ──────────────────────────────────────────────────────────────────

@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
    summary="上传文档并异步建立索引",
    description="支持 PDF、Word（docx）、Excel（xlsx）、CSV 格式，最大 50 MB。",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 校验扩展名
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"不支持的文件类型 .{ext}，支持：{', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 读取文件内容并检查大小
    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"文件超过限制（{settings.MAX_FILE_SIZE_MB} MB）",
        )

    # 保存到磁盘（使用 UUID 避免重名）
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 创建数据库记录
    doc = Document(
        uuid=str(uuid.uuid4()),
        filename=unique_name,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(content),
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 异步后台索引
    background_tasks.add_task(_index_document, doc.id, file_path, ext)

    return doc


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="获取所有已上传文档列表",
)
async def list_documents(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(Document.id)))
    total = total_result.scalar_one()

    docs_result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    docs = docs_result.scalars().all()
    return {"total": total, "documents": docs}


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="获取单个文档详情",
)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.delete(
    "/{document_id}",
    response_model=DeleteResponse,
    summary="删除文档及其向量数据",
)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除磁盘文件
    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    await db.delete(doc)  # cascade 会自动删除关联的 chunks
    await db.commit()
    return {"message": f"文档 '{doc.original_filename}' 已删除", "document_id": document_id}

