"""
RAG 服务：检索相关文本块 → 拼接 Context → 调用 LLM 生成答案。
"""
from typing import Any, Dict, List

import openai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.vector_service import vector_service

# Prompt 模板
_SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Answer questions **only** based on the provided document excerpts. "
    "If the answer cannot be found in the excerpts, explicitly say so. "
    "Keep your answer concise and accurate."
)

_USER_PROMPT_TMPL = """\
Below are relevant excerpts from the documents:

{context}

---
Question: {question}

Answer:"""


class RAGService:
    def __init__(self):
        self._client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL or None,
        )

    async def query(
        self,
        db: AsyncSession,
        question: str,
        top_k: int | None = None,
    ) -> Dict[str, Any]:
        # 1. 向量检索
        chunks = await vector_service.similarity_search(db, question, top_k)
        if not chunks:
            return {
                "answer":  "未在已索引的文档中找到相关内容，请先上传相关文档。",
                "sources": [],
                "model":   settings.LLM_MODEL,
            }

        # 2. 构建 Context
        context_parts = [
            f"[来源: {c['document_name']}"
            + (f", 第 {c['page_number']} 页" if c["page_number"] else "")
            + f", 相似度: {c['similarity']}]\n{c['content']}"
            for c in chunks
        ]
        context = "\n\n---\n\n".join(context_parts)

        # 3. 调用 LLM
        user_prompt = _USER_PROMPT_TMPL.format(context=context, question=question)
        response = await self._client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.1,
        )

        return {
            "answer":  response.choices[0].message.content,
            "sources": chunks,
            "model":   settings.LLM_MODEL,
        }


rag_service = RAGService()

