# RAG Document Search 📄🔍

> **RAG（检索增强生成）文档问答系统** — 上传 PDF / Word / Excel，用自然语言提问，AI 给出精准答案并标注来源。

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![pgvector](https://img.shields.io/badge/pgvector-0.7-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📤 **多格式文档上传** | 支持 PDF、Word（docx）、Excel（xlsx）、CSV |
| ⚡ **异步向量化** | 上传后台自动切块 → 生成 Embedding → 存入 pgvector |
| 🔎 **语义相似度检索** | 基于 pgvector 余弦距离，精准召回相关片段 |
| 🤖 **LLM 生成答案** | 支持 OpenAI / 阿里云通义千问等兼容接口 |
| 📝 **来源引用** | 答案附带文档名、页码、相似度分数 |
| 🔌 **双 Embedding 模式** | OpenAI API 或 sentence-transformers 本地推理，.env 一键切换 |
| 📖 **Swagger UI** | 内置交互式 API 文档，`http://localhost:8000/docs` |

---

## 🏗️ 系统架构

```
用户请求
   │
   ▼
┌─────────────────────────────────────────────┐
│              FastAPI  (port 8000)            │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │documents │  │  search  │  │  health   │  │
│  └────┬─────┘  └────┬─────┘  └───────────┘  │
│       │              │                        │
│  ┌────▼─────┐  ┌────▼──────────────────────┐ │
│  │  Parser  │  │        RAG Service        │ │
│  │PDF/Word/ │  │  检索 → Context → LLM    │ │
│  │Excel/CSV │  └────────────┬──────────────┘ │
│  └────┬─────┘               │                │
│       │              ┌──────▼──────┐          │
│  ┌────▼─────────────►│VectorService│          │
│  │  EmbeddingService │ similarity  │          │
│  │  OpenAI / Local   │  search     │          │
│  └───────────────────└──────┬──────┘          │
└─────────────────────────────┼───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  PostgreSQL + pgvector│
                    │  documents 表         │
                    │  document_chunks 表   │
                    │  (含 vector 列)       │
                    └──────────────────────┘
```

---

## 📁 项目结构

```
rag-doc-search/
├── app/
│   ├── main.py                  # FastAPI 入口，挂载路由
│   ├── api/v1/
│   │   ├── documents.py         # 文档上传 / 列表 / 删除
│   │   ├── search.py            # RAG 问答接口
│   │   └── health.py            # 健康检查
│   ├── core/
│   │   ├── config.py            # 从 .env 读取配置（pydantic-settings）
│   │   ├── database.py          # SQLAlchemy async 引擎 & 初始化
│   │   └── embeddings.py        # Embedding 封装（OpenAI / 本地）
│   ├── models/
│   │   └── document.py          # ORM 模型（documents & document_chunks）
│   ├── schemas/
│   │   └── document.py          # Pydantic 请求/响应 Schema
│   └── services/
│       ├── parser.py            # PDF / Word / Excel / CSV 解析 & 切块
│       ├── vector_service.py    # 向量写入 & pgvector 相似度检索
│       └── rag_service.py       # RAG 流程（检索 → LLM 生成）
├── uploads/                     # 上传文件存储目录（已 gitignore）
├── .env.example                 # 配置模板（提交到 Git）
├── .env                         # 实际配置（已 gitignore，不提交！）
├── requirements.txt
├── docker-compose.yml           # PostgreSQL 16 + pgvector 一键启动
├── .gitignore
└── README.md
```

---

## 🚀 快速开始

### 前置条件

- Python 3.11+
- Docker & Docker Compose（推荐）或 本地 PostgreSQL 16 + pgvector 扩展

### Step 1：克隆项目

```bash
git clone https://github.com/your-username/rag-doc-search.git
cd rag-doc-search
```

### Step 2：配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，**至少需要填写**：

```dotenv
OPENAI_API_KEY=sk-xxxxxxxx   # 你的 OpenAI Key
```

其余参数保持默认即可，详见 [配置说明](#⚙️-配置说明)。

### Step 3：启动 PostgreSQL（Docker）

```bash
docker compose up -d
```

等待约 10 秒，确认数据库就绪：

```bash
docker compose ps   # Status 应显示 healthy
```

### Step 4：安装 Python 依赖

```bash
# 推荐使用虚拟环境
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS/Linux

# 使用清华镜像加速（国内环境）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### Step 5：启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

打开浏览器访问：

| 地址 | 说明 |
|------|------|
| `http://localhost:8000/docs` | **Swagger UI**（推荐调试） |
| `http://localhost:8000/redoc` | ReDoc 文档 |
| `http://localhost:8000/api/v1/health` | 健康检查 |

---

## ⚙️ 配置说明

所有配置通过根目录 `.env` 文件管理：

```dotenv
# ── App ───────────────────────────────────────────────────────────
APP_NAME=RAG Document Search
APP_VERSION=1.0.0
DEBUG=false

# ── Database ──────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ragdb

# ── OpenAI ────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-xxxx

# 使用阿里云通义千问（DashScope 兼容 OpenAI 接口）时：
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# LLM_MODEL=qwen-plus

# ── Embedding ─────────────────────────────────────────────────────
EMBEDDING_PROVIDER=openai          # openai 或 local
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# ── RAG 参数 ──────────────────────────────────────────────────────
CHUNK_SIZE=500      # 每块最大字符数
CHUNK_OVERLAP=50    # 块间重叠字符数（保证上下文连贯）
TOP_K=5             # 检索返回的最相似块数量

# ── 文件上传 ──────────────────────────────────────────────────────
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
```

### 使用阿里云通义千问（国内无需翻墙）

```dotenv
OPENAI_API_KEY=sk-xxx           # DashScope API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=text-embedding-v3
EMBEDDING_DIM=1024
LLM_MODEL=qwen-plus
```

### 使用本地 Embedding（无需 API Key）

```dotenv
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5   # 首次运行自动下载
EMBEDDING_DIM=512
```

安装本地推理依赖：
```bash
pip install sentence-transformers
```

> ⚠️ 注意：切换 Embedding 模型后，向量维度改变，需要重建数据库（删除并重新创建 `ragdb`），否则会报类型不兼容错误。

---

## 📡 API 接口

### 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/documents/upload` | 上传文档（multipart/form-data） |
| `GET` | `/api/v1/documents` | 获取所有文档列表 |
| `GET` | `/api/v1/documents/{id}` | 获取单个文档详情 |
| `DELETE` | `/api/v1/documents/{id}` | 删除文档及其向量 |

**上传示例（curl）**：
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@./your_document.pdf"
```

**响应**：
```json
{
  "id": 1,
  "uuid": "3fa85f64-...",
  "original_filename": "your_document.pdf",
  "file_type": "pdf",
  "file_size": 102400,
  "total_chunks": 0,
  "status": "processing",
  "created_at": "2026-04-07T08:00:00"
}
```

> 文档上传后状态为 `processing`，后台异步索引完成后变为 `ready`，可再次查询确认。

---

### RAG 问答

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/search/query` | 输入问题，返回 AI 答案 + 来源 |

**请求**：
```json
{
  "query": "患者的血红蛋白检测结果是多少？",
  "top_k": 5
}
```

**响应**：
```json
{
  "query": "患者的血红蛋白检测结果是多少？",
  "answer": "根据检验报告，患者血红蛋白（HGB）为 128 g/L，在参考范围 115-150 g/L 内，属于正常水平。",
  "model": "gpt-4o-mini",
  "sources": [
    {
      "content": "HGB 128 g/L | 参考范围: 115-150",
      "document_name": "lab_report_2025.pdf",
      "page_number": 2,
      "similarity": 0.9312
    }
  ]
}
```

---

### 健康检查

```bash
GET /api/v1/health
```

```json
{
  "status": "ok",
  "app": "RAG Document Search",
  "version": "1.0.0",
  "database": "ok",
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small",
  "llm_model": "gpt-4o-mini"
}
```

---

## 🧩 核心概念

### RAG 工作流程

```
1. 上传文档
       │
       ▼
2. 文档解析（PDF/Word/Excel → 纯文本）
       │
       ▼
3. 文本切块（Chunking）
   按 CHUNK_SIZE 切割，块间保留 CHUNK_OVERLAP 字符重叠
       │
       ▼
4. 向量化（Embedding）
   每块文本 → 高维向量（如 1536 维）
       │
       ▼
5. 存储到 PostgreSQL + pgvector
       │
       ┌─────────────────────────────────────────┐
       │         用户提问时                        │
       └─────────────────────────────────────────┘
       │
6. 问题向量化
       │
       ▼
7. pgvector 余弦相似度检索（Top-K）
       │
       ▼
8. 拼接 Context → LLM 生成答案
```

### pgvector 余弦距离

pgvector 使用 `<=>` 运算符计算余弦距离（0 = 完全相同，2 = 完全相反），相似度 = `1 - 余弦距离`：

```sql
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM document_chunks
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

---

## 🛠️ 开发指南

### 本地数据库管理

```bash
# 进入 PostgreSQL 容器
docker exec -it rag_postgres psql -U postgres -d ragdb

# 查看表结构
\dt

# 查看向量列
SELECT id, original_filename, total_chunks, status FROM documents;

# 停止数据库
docker compose down

# 完全清空数据（重建数据库）
docker compose down -v
docker compose up -d
```

### 添加新的文件格式支持

在 `app/services/parser.py` 中：
1. 在 `ALLOWED_EXTENSIONS`（`documents.py`）中添加新扩展名
2. 在 `DocumentParser.parse()` 的 `dispatch` 字典中注册新方法
3. 实现对应的 `_parse_xxx()` 方法，返回统一格式的 chunk 列表

---

## 📦 部署

### 生产环境建议

1. **环境变量**：使用 Kubernetes Secret 或云服务的 Secret Manager，而不是 `.env` 文件
2. **CORS**：修改 `main.py` 中 `allow_origins` 为具体域名
3. **数据库连接池**：按并发量调整 `pool_size` 和 `max_overflow`
4. **pgvector 索引**：数据量 > 10 万条时，为向量列添加 HNSW 索引提升检索速度：

```sql
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## 📄 License

MIT License — 自由使用，欢迎 Star ⭐ 和 PR！

