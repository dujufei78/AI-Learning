# 🧠 AI 应用开发工程师知识体系

> **定位**：AI 应用开发为主线，兼顾模型微调能力。  
> **用法**：每个模块对应一个学习目录，按序递进，每模块产出一个实战项目。

---

## 📁 目录结构（直接建文件夹用）

```
AI-Learning/
├── 01_Basics/
│   ├── Python进阶/
│   ├── 数学基础/
│   ├── 工程工具/
│   ├── API调用/
│   └── 产物/
├── 02_LLM/
│   ├── 架构原理/
│   ├── 训练流程/
│   ├── 推理部署/
│   └── 产物/
├── 03_Prompt/
│   ├── 设计原则/
│   ├── 核心技巧/
│   ├── 进阶优化/
│   └── 产物/
├── 04_RAG/
│   ├── 基础RAG/
│   ├── 高级RAG/
│   └── 产物/
├── 05_Agent/
│   ├── 工具调用/
│   ├── 架构模式/
│   ├── MCP协议/
│   ├── 记忆系统/
│   └── 产物/
├── 06_Frameworks/
│   ├── LangChain/
│   ├── LlamaIndex/
│   ├── LangGraph/
│   ├── MCP/
│   └── 产物/
├── 07_FineTuning/
│   ├── 数据准备/
│   ├── PEFT训练/
│   ├── 偏好对齐/
│   └── 产物/
└── 08_Production/
    ├── 应用架构/
    ├── 可观测性/
    ├── 成本优化/
    ├── 安全评估/
    └── 产物/
```

---

## 01 · 基础储备

> 应用开发视角，**够用**为原则，不追求精通。

| 类别 | 核心内容 | 优先级 |
|------|---------|--------|
| Python进阶 | asyncio、类型注解、Pydantic、装饰器 | ⭐⭐⭐ |
| 数学 | 向量/矩阵直觉、余弦相似度、概率基础 | ⭐⭐ |
| 工程工具 | Git、Docker、conda/venv、FastAPI | ⭐⭐⭐ |
| API调用 | HTTP/SSE、流式输出、OpenAI SDK | ⭐⭐⭐ |

**产出目标**：能用 FastAPI 封装一个流式 LLM 对话接口。

---

## 02 · 大模型原理

> 不做黑盒调用者，理解"为什么这样工作"。

**核心知识点：**
- **Transformer 架构**：Self-Attention、Multi-Head Attention、KV Cache
- **LLM 工作方式**：自回归生成、Temperature/Top-P 采样、Token 化
- **训练流程**：预训练 → SFT指令微调 → RLHF/DPO 偏好对齐
- **主流模型对比**：GPT/Claude/Gemini/Qwen/DeepSeek（选型能力）
- **推理部署基础**：量化（INT4/INT8）、Ollama 本地运行、vLLM 高并发

**产出目标**：用 Ollama 本地跑通 Qwen，理解各参数含义。

---

## 03 · 提示工程

> 操控大模型的核心接口，投入产出比最高的模块。

**核心知识点：**
- **设计原则**：角色设定、任务明确化、输出格式控制（JSON/结构化）
- **核心技巧**：Few-shot、Zero-shot、思维链（CoT）、ReAct 模式
- **进阶技巧**：HyDE、Self-Consistency、Reflection（自我反思）
- **系统提示**：System Prompt 设计规范、多轮对话上下文管理
- **评估与优化**：Prompt A/B 测试、防 Prompt Injection

**产出目标**：建立一套可复用的 Prompt 模板库（含5+场景）。

---

## 04 · RAG 知识增强

> 让大模型用上"私有知识"，企业级应用必备。

### 基础 RAG
- 文档加载（PDF/Word/网页）→ 分块策略 → Embedding → 向量存储 → 检索生成

### 向量数据库选型
| 场景 | 推荐 |
|------|------|
| 学习/原型 | ChromaDB |
| 生产项目 | Qdrant |
| 已有 PostgreSQL | PGVector |

### 高级 RAG（重点）
- **查询优化**：Query Rewriting、HyDE、多查询并行
- **索引优化**：父子分块、混合检索（向量+关键词 BM25）
- **排序优化**：Reranking（BGE Reranker、Cohere）
- **评估框架**：RAGAS（忠实度、答案相关性、上下文召回率）

### 知识图谱增强
- GraphRAG 思路：实体关系抽取 + 图谱检索

**产出目标**：企业文档问答系统，支持混合检索+重排序，RAGAS 评分 > 0.8。

---

## 05 · Agent 智能体

> 从"回答问题"到"自主完成任务"，AI 应用的核心方向。

### Function Calling / Tool Use
- 工具定义（JSON Schema）、工具路由、结果处理、并行调用

### Agent 架构模式
| 模式 | 适用场景 |
|------|---------|
| ReAct | 通用工具调用Agent |
| Plan-and-Execute | 复杂多步骤任务 |
| HITL（人在回路） | 高风险业务节点 |
| Multi-Agent | 复杂任务分工协作 |

### MCP 协议（重点）
- **是什么**：AI 应用与工具/数据源的标准化接口协议（Anthropic提出）
- **核心概念**：Server（工具提供方）/ Client（AI应用方）/ Resources / Tools / Prompts
- **实践**：开发自定义 MCP Server，接入文件系统/数据库/外部API
- **生态**：Claude Desktop、Cursor、LangGraph 均已支持

### 记忆系统
- 短期记忆（Context Window）、长期记忆（向量库）、会话持久化

**产出目标**：带工具调用 + 记忆 + HITL 的 ReAct Agent，可完成多步骤真实任务。

---

## 06 · 开发框架

> 站在巨人肩上，快速构建。**重点掌握 LangGraph，其他按需学习。**

### LangChain（基础，快速过）
- LCEL 链式表达式、Prompt Template、Output Parser
- Memory 管理、LangSmith 调试追踪

### LlamaIndex（RAG专项）
- Document Loader、Node Parser、Index 类型
- QueryEngine、SubQuestion、RouterQueryEngine

### LangGraph ⭐（重点，主力框架）
- **核心概念**：State 状态图、Node 节点、Edge 条件路由
- **关键能力**：有状态、可持久化（Checkpoint）、支持循环、支持HITL
- **实战**：用 LangGraph 重构 Agent，实现多轮对话+工具调用+断点恢复

### MCP（标准化工具接入）
- MCP Server 开发（Python SDK）
- 自定义 Tool / Resource / Prompt 实现

### 框架选型速查
```
简单对话/原型          → LangChain 基础链
复杂 RAG 系统         → LlamaIndex
生产级 Agent 工作流    → LangGraph
标准化工具集成         → MCP
多 Agent 协作         → LangGraph + AutoGen/CrewAI
```

**产出目标**：用 LangGraph 实现一个多 Agent 协作的智能分析工作流。

---

## 07 · 模型微调

> 应用工程师必备进阶能力，让模型更懂你的业务场景。

### 微调路径选择
```
业务数据 < 1K 条    → 优化 Prompt / RAG，不建议微调
业务数据 1K~10K 条  → LoRA / QLoRA 微调
业务数据 > 10K 条   → 考虑全量微调
```

### 核心知识点

**数据准备**
- 指令数据格式（Alpaca / ShareGPT 格式）
- 数据清洗、去重、质量评估
- 合成数据：用强模型生成训练数据（Self-Instruct）

**高效微调（PEFT）**
- **LoRA 原理**：低秩矩阵分解，只训练少量参数（必须理解）
- **QLoRA**：量化 + LoRA，4bit 显存友好，消费级 GPU 可跑
- **训练框架**：LLaMA-Factory（推荐）、Unsloth（加速）、Axolotl

**微调后处理**
- 模型合并（LoRA → 完整权重）
- 微调评估：业务指标 + 通用基准（不能只看Loss）
- 灾难性遗忘问题与缓解策略

**偏好对齐（进阶）**
- DPO（Direct Preference Optimization）：比 RLHF 更简单实用

**产出目标**：用 LLaMA-Factory + QLoRA 微调一个垂直领域模型，并完成评估对比。

---

## 08 · 工程化落地

> 从 Demo 到生产的最后一公里，也是最容易被忽视的一环。

### 应用架构
- FastAPI 异步后端 + 流式输出（SSE/WebSocket）
- 多会话管理、上下文窗口控制
- 任务队列（Celery）处理耗时任务

### 可观测性
- **追踪工具**：LangSmith / LangFuse（推荐开源自部署）
- **关键指标**：首 Token 延迟、总耗时、Token 消耗、调用成功率
- 结构化日志 + 链路追踪

### 成本与性能优化
- **模型路由**：简单任务 → 小模型（Qwen2.5-7B），复杂任务 → 大模型
- **缓存策略**：语义缓存（相似问题复用答案）、KV Cache 复用
- **Token 控制**：上下文压缩、摘要滚动、动态截断

### 安全合规
- Prompt Injection 防御
- 输出敏感信息过滤
- 私有化部署方案（数据不出域）

### 评估体系
- **自动评估**：RAGAs、LLM-as-Judge
- **业务评估**：任务完成率、用户满意度
- A/B 测试机制

**产出目标**：生产可用的 AI 应用后端，含监控看板、成本统计、安全防护。

---

## 🗺️ 学习路径

```
阶段一（1-2月）入门打通
01基础储备 → 03提示工程 → 04RAG基础 → 06LangChain入门
目标：跑通端到端问答应用

阶段二（2-4月）系统深化  
02大模型原理 → 04高级RAG → 05Agent+MCP → 06LangGraph
目标：独立开发生产级 Agent 应用

阶段三（4-6月）进阶拓展
07模型微调 → 08工程化落地 → 选定垂直领域深耕
目标：具备从需求到上线的完整交付能力
```

---

## 📋 里程碑自查

- [ ] 用 FastAPI + LangChain 实现流式对话接口
- [ ] 搭建支持混合检索+Reranking 的 RAG 系统，RAGAS 评分达标
- [ ] 用 LangGraph 实现带 HITL 的多工具 Agent
- [ ] 开发一个自定义 MCP Server 并接入 Claude/Cursor
- [ ] 用 QLoRA 微调一个垂直领域模型并完成评估
- [ ] 部署带 LangFuse 监控的生产级 AI 应用

---

*最后更新：2026-04-08*
