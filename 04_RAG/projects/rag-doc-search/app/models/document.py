import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.core.database import Base


class Document(Base):
    """
    文档主表：记录每个上传文件的元信息。
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)          # 磁盘存储的文件名（唯一）
    original_filename = Column(String(255), nullable=False) # 用户上传的原始文件名
    file_type = Column(String(50), nullable=False)          # pdf / docx / xlsx …
    file_size = Column(Integer)                             # 文件大小（字节）
    total_chunks = Column(Integer, default=0)               # 切分后的块总数
    status = Column(String(50), default="processing")       # processing / ready / failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    """
    文档切块表：存储文本块及其向量。
    embedding 列使用 pgvector，维度由 .env 中 EMBEDDING_DIM 决定。
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)   # 块在文档中的顺序编号
    content = Column(Text, nullable=False)           # 原始文本内容
    page_number = Column(Integer)                    # PDF 页码（其他文件类型为 None）
    chunk_metadata = Column(Text)                    # JSON 字符串，存扩展信息（如 sheet 名）
    embedding = Column(Vector(settings.EMBEDDING_DIM))  # 向量列
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

