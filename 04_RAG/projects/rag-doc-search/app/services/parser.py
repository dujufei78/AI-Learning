"""
文档解析器：将 PDF / Word / Excel 提取为带元数据的文本块列表。

返回格式（每个 chunk 是一个字典）：
  {
      "content"     : str,          # 文本内容
      "chunk_index" : int,          # 全局块序号
      "page_number" : int | None,   # PDF 页码，其他类型为 None
      "metadata"    : dict,         # 扩展信息（source / sheet / row …）
  }
"""
from pathlib import Path
from typing import Any, Dict, List, Optional


class DocumentParser:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ── 统一入口 ──────────────────────────────────────────────────────────

    def parse(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        dispatch = {
            "pdf":  self._parse_pdf,
            "docx": self._parse_word,
            "doc":  self._parse_word,
            "xlsx": self._parse_excel,
            "xls":  self._parse_excel,
            "csv":  self._parse_csv,
        }
        handler = dispatch.get(file_type.lower())
        if not handler:
            raise ValueError(f"不支持的文件类型：{file_type}")
        return handler(file_path)

    # ── PDF ───────────────────────────────────────────────────────────────

    def _parse_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        import fitz  # PyMuPDF

        chunks: List[Dict[str, Any]] = []
        doc = fitz.open(file_path)
        try:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                if not text:
                    continue
                for chunk_text in self._split_text(text):
                    chunks.append({
                        "content":     chunk_text,
                        "chunk_index": len(chunks),
                        "page_number": page_num,
                        "metadata":    {"source": "pdf", "page": page_num},
                    })
        finally:
            doc.close()
        return chunks

    # ── Word ──────────────────────────────────────────────────────────────

    def _parse_word(self, file_path: str) -> List[Dict[str, Any]]:
        from docx import Document  # python-docx

        doc = Document(file_path)
        full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [
            {
                "content":     chunk,
                "chunk_index": i,
                "page_number": None,
                "metadata":    {"source": "word"},
            }
            for i, chunk in enumerate(self._split_text(full_text))
        ]

    # ── Excel ─────────────────────────────────────────────────────────────

    def _parse_excel(self, file_path: str) -> List[Dict[str, Any]]:
        import pandas as pd

        chunks: List[Dict[str, Any]] = []
        xl = pd.ExcelFile(file_path)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name, dtype=str).fillna("")
            for row_idx, row in df.iterrows():
                row_text = " | ".join(
                    f"{col}: {val}" for col, val in row.items() if val.strip()
                )
                if row_text.strip():
                    chunks.append({
                        "content":     row_text,
                        "chunk_index": len(chunks),
                        "page_number": None,
                        "metadata":    {"source": "excel", "sheet": sheet_name, "row": row_idx},
                    })
        return chunks

    # ── CSV ───────────────────────────────────────────────────────────────

    def _parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        import pandas as pd

        df = pd.read_csv(file_path, dtype=str).fillna("")
        chunks: List[Dict[str, Any]] = []
        for row_idx, row in df.iterrows():
            row_text = " | ".join(
                f"{col}: {val}" for col, val in row.items() if val.strip()
            )
            if row_text.strip():
                chunks.append({
                    "content":     row_text,
                    "chunk_index": len(chunks),
                    "page_number": None,
                    "metadata":    {"source": "csv", "row": row_idx},
                })
        return chunks

    # ── 文本切分 ──────────────────────────────────────────────────────────

    def _split_text(self, text: str) -> List[str]:
        """将长文本切分为带重叠的块，优先在句子/段落边界断开。"""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]

            # 非最后一块时，尝试在语义边界断开
            if end < len(text):
                for sep in ["\n\n", "\n", "。", ".", " "]:
                    idx = chunk.rfind(sep)
                    if idx > self.chunk_size // 2:
                        chunk = chunk[: idx + len(sep)]
                        end = start + len(chunk)
                        break

            stripped = chunk.strip()
            if stripped:
                chunks.append(stripped)
            start = end - self.chunk_overlap

        return chunks

