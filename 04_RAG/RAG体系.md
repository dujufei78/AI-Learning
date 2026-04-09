RAG体系
一.RAG介绍
RAG：Retrieval-Augmented Generation(检索增强生成) 。
为什么需要RAG: LLM训练数据有时间限制，不知道新发生的事情，并且公司内部的私有文件，LLM无法拿去做训练。那么我如何根据这些私密资料继续检索呢？
RAG做法：先把文件切成块，存进向量数据库，用户提问时先检索这些相关的文本块，再将问题和文本块，交给LLM进行生成答案。

二.RAG全流程
全流程分为两块：提前建库 + 实时问答
建库阶段：文档加载 → 文档切块（chunking） → 向量化(Embedding) → 向量数据库（Vector Database）
问答阶段：查询优化 → 混合检索 → Reranking重排序 → 组装Prompt交给LLM → RAGAS评估

Step1.文档加载(Document Loading)
做什么：将各种格式文件统一为文本
支持格式：支持PDF、Word、Excel、CSV等多种格式，提取文本内容。
使用工具：Langchain/Llamaindex的 Document Loaders系列组件，或开源库如 PyMuPDF、python-docx、pandas 等。
高阶做法：使用OCR技术 + LLM + Prompt 做文本识别，处理表格等复杂结构，提升文本提取质量。

Step2.文档切块 (Chunking)
做什么：将长文本切分为小块，因为大模型上下文窗口有限，不能全部丢给大模型
切块重要性：快太小，没有上下文，模型回答不好；块太大，噪音多，检索不准，浪费Token
切块策略：固定长度切块、语义切块、父子分块、滑动窗口
切块策略详情：
- 固定长度切块：按固定Token数或字符数切分，简单高效，比如 500
- 语义切块：基于文本语义边界切分，按段落、章节、标题切分，保持信息完整性
- 父子切块（Parent-Child Chunking）：小块256字，用于检索，命中后返回对应的大块1024字。
- 滑动窗口切块：固定长度切块基础上，增加重叠部分（比如 100 字），提升检索召回率。

Step3.向量化 (Embedding)
做什么：将文本块转换为向量，便于语义检索
Embedding模型：
BGE（BAAI General Embedding，北京智源通用向量模型）  本地    中文效果最好，免费
text2vec  本地  轻量，适合资源少的环境
OpenAI text-embedding-3  API  效果好，收费
Cohere Embed  API  多语言强

BGE 是北京人工智能研究院（BAAI，Beijing Academy of Artificial Intelligence）开源的，中文场景首选。




Step4.向量数据库 (Vector Database)



Step5.查询优化 (Query Optimization)



Step6.混合检索 (Hybrid Retrieval)





Step7.Reranking重排序 (Reranking)



Step8.组装Prompt交给LLM (Prompt Assembly)



Step9.RAGAS评估 (RAGAS Evaluation)



三.进阶
