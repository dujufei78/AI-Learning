from typing import List

import openai

from app.core.config import settings


class EmbeddingService:
    """
    向量化服务。
    支持两种 Provider：
      - openai  : 调用 OpenAI / 兼容接口（如阿里云通义 text-embedding）
      - local   : 使用 sentence-transformers 本地推理（无需 API Key）
    通过 .env 中 EMBEDDING_PROVIDER 切换。
    """

    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self._local_model = None  # 懒加载，避免未安装时��错

        if self.provider == "openai":
            self._client = openai.AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL or None,
            )

    # ── 公开接口 ──────────────────────────────────────────────────────────

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文本 → 向量列表。"""
        if self.provider == "openai":
            return await self._openai_embed(texts)
        return self._local_embed(texts)

    async def embed_text(self, text: str) -> List[float]:
        """单条文本 → 向量。"""
        results = await self.embed_texts([text])
        return results[0]

    # ── 内部实现 ──────────────────────────────────────────────────────────

    async def _openai_embed(self, texts: List[str]) -> List[List[float]]:
        response = await self._client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _local_embed(self, texts: List[str]) -> List[List[float]]:
        """使用 sentence-transformers 本地推理（同步，小模型可接受）。"""
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        embeddings = self._local_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


# 全局单例
embedding_service = EmbeddingService()

