# AEGIS 项目概述

> AI 驱动的企业级培训考核平台

---

## 一、项目介绍

AEGIS 是一个 AI 驱动的企业级培训考核平台，采用 monorepo 架构，包含三个核心模块：

| 模块 | 定位 | 端口 |
|:---|:---|:---:|
| **Base** | 通用基础框架（LLM 抽象、ORM、客户端封装、认证、调度） | 8010 |
| **CompFox**（合规狐） | 金融合规培训与能力评估平台 | 8003 |
| **Education**（E教千问） | 智能教育 AI 平台（题库/考试/AI 阅卷/学情画像） | 8002 |

**CompFox** 是核心交付物——面向银行、证券、保险、基金等金融机构，覆盖"**合规题库 → 自动组卷 → 在线考核 → AI 阅卷（含主观题）→ 员工合规画像 → 复训推荐**"全闭环。解决传统金融合规培训中"发试卷-人工阅卷-手工统计"的低效问题，AI 能评判主观题（合规案例分析），这是传统系统做不了的。

---

## 二、项目背景

金融机构对从业人员有严格的合规培训与考核要求（反洗钱、数据安全、内幕交易、投资者保护、合规管理、行为准则等），传统模式依赖线下考试 + 人工阅卷，存在三大痛点：

- **效率低**：出题、组卷、阅卷、统计全靠人工，周期长
- **标准不统一**：主观题（合规案例分析）的评分依赖于阅卷人经验，缺乏一致性
- **缺乏个性化**：全员同一套题，无法针对个人薄弱环节精准复训

项目从 Education（通用智能教育平台）平行改造而来：将"科目"映射为"合规领域"，"年级"映射为"职级"，"学生"映射为"员工"，"学习画像"映射为"合规能力画像"。在保留成熟架构的基础上完成行业适配。

核心业务流程：

```
合规题库（AI生成 + 人工录入 + Excel批量导入）
    → 自动组卷（题型/难度/知识点三维约束）
    → 在线考核（限时答题，一人一卷防作弊）
    → AI 阅卷（客观题规则匹配 + 主观题 LLM 评判 + RAG 法规对照）
    → 员工画像（合规能力雷达图 + 薄弱知识点识别 + 行为分析）
    → 复训推荐（针对弱项的个性化题目推荐）
```

---

## 三、项目技术栈

| 层级 | 技术选型 |
|:---|:---|
| 语言 | Python 3.13 |
| Web 框架 | FastAPI + Uvicorn（异步 + 同步混合，SSE 流式响应） |
| 配置管理 | Pydantic V2 Settings + `.env` 文件 |
| ORM 层 | **自研**（基于 PyMySQL + DBUtils 连接池，Pydantic 驱动 PO 模型，参数化查询防 SQL 注入） |
| LLM 层 | 通义千问 qwen3-max / DeepSeek deepseek-chat，OpenAI SDK 统一接口，支持一键切换 |
| Agent 框架 | 自研 ReAct / CoT / Plan-and-Execute 多范式，支持 Tool 注册与 Memory 管理 |
| 向量数据库 | Milvus（1024 维稠密向量 + BM25 稀疏向量混合检索） |
| 图数据库 | Neo4j（法规-案例-处罚关系图谱） |
| 关系数据库 | MySQL（InnoDB，utf8mb4） |
| 缓存 | Redis（LLM 结果缓存、会话上下文、关键词索引） |
| 对象存储 | MinIO / 腾讯云 COS |
| 语音 | 通义千问 ASR（语音转文字）/ TTS（文字转语音） |
| 定时任务 | APScheduler（MySQL 持久化 JobStore） |
| 中文分词 | Jieba（TF-IDF / TextRank 关键词提取） |
| 前端 | 原生 HTML + Vanilla JS + Jinja2 模板渲染 |
| 部署 | Docker + docker-compose |

### 架构总览

```
┌─────────────────────────────────────────────────┐
│                    FastAPI 入口                   │
│         CompFox:8003   Education:8002            │
│              Base Auth API:8010                  │
├─────────────────────────────────────────────────┤
│               API 路由层（RESTful）              │
├─────────────────────────────────────────────────┤
│               Service 业务逻辑层                  │
├──────────────┬──────────────────┬───────────────┤
│   PO 模型层   │   VDB 向量模型层   │   Prompt 层   │
│ (MySQL ORM)  │ (Milvus ORM)     │ (Jinja2模板)  │
├──────────────┴──────────────────┴───────────────┤
│           Base 基础能力复用层                     │
│  Client（Redis/Neo4j/MinIO/COS/ASR/TTS）        │
│  Repository（自研 ORM + 连接管理 + 多库路由）     │
│  Ai（LLM 抽象 + Agent + Memory + Tool）           │
│  Config（Pydantic Settings + 日志）               │
│  RicUtils（HTTP/缓存/文件/PDF/Excel/音频）        │
└─────────────────────────────────────────────────┘
```

---

## 四、个人职责

以下基于代码库实际内容梳理，涵盖从基础架构到业务交付的完整范围：

### 4.1 基础框架设计（Base 模块）

- **自研 ORM 框架**：基于 PyMySQL + Pydantic + DBUtils 实现完整的 Repository 层。支持参数化查询（防 SQL 注入）、自动 CRUD 生成、多数据库连接切换（3 级优先级：实例 → 类 → 全局默认）、连接池健康检查与自动恢复、事务上下文管理器。同时为 Milvus 实现了一套并行的 VDB ORM（自动 Schema 推导、混合检索封装）
- **LLM 统一抽象层**：通过 OpenAI SDK 兼容接口统一通义千问和 DeepSeek 的调用，封装同步/异步/流式/thinking mode 四种调用模式，抽象 OCR、ASR、Embedding 等能力差异。业务代码无需感知底层模型切换
- **Agent 框架**：实现 ReAct（Reason + Act 循环）、CoT（Chain of Thought 单次推理）、Plan-and-Execute（规划→执行→综合）三种 Agent 范式，配套 Tool 注册机制（`@tool` 装饰器 + Pydantic args_schema 自动生成 OpenAI function-calling schema）和 Memory 管理（InMemory 列表 + DB 持久化双模式）
- **统一配置体系**：基于 Pydantic V2 Settings 实现分层配置（30+ 环境变量，按模块分 prefix），`.env` 文件自动加载

### 4.2 业务模块全栈开发（CompFox & Education）

- **题库系统**：CRUD + AI 智能生成（随机参数 + 知识点采样 + 类型格式化）+ AI 文本/文件批量导入 + Excel 导入导出 + UUID 与整数 ID 双模式检索
- **试卷管理**：题型/难度/知识点三维约束自动组卷，版本控制（`parent_id` 关联 + 版本历史 + 版本回滚），发布/归档状态流转
- **考试系统**：限时作答 + 一人一卷约束（唯一索引）+ 客观题规则匹配 + 主观题 AI 评判 + 考试成绩 AI 总结（薄弱点分析 + 复训建议 + 风险等级评估）
- **AI Agent 对话系统**：6 意图识别（出题/判题/解析/问答/推荐/进度查询）+ 流式 SSE 响应 + thinking mode + 会话上下文（30min TTL）+ 异步画像更新（ThreadPoolExecutor）
- **知识库 RAG**：PDF/DOCX/TXT/Excel/URL 多格式文档导入，中文递归分块，Milvus 向量化存储，混合检索注入 LLM Prompt
- **员工合规画像**：自动更新（练习数据 + 聊天数据），学习报告（按日/周/月/全部），个性化推荐（薄弱知识点驱动），行为分析（时段分布/频次分类/偏好评判），AI 画像摘要生成
- **题库特征工程**：50+ 维特征宽表（统计特征/干预特征/知识图谱特征/运维特征），题目质量熔断机制（低质量题自动冻结）

### 4.3 RAG 评测体系

- 自建评测数据集格式规范（queries + relevant_doc_ids）
- 检索评测：Precision@k / Recall@k / Hit@k / MRR / NDCG@k（支持文档级和 Chunk 级粒度）
- 生成评测：LLM-as-Judge（忠实度/相关性/正确性 1-3 分）
- 快照对比：多次评测结果归档与横向对比

### 4.4 前端页面群

纯 HTML + Vanilla JS + Jinja2 模板，共 9 个功能页面：刷题练习 / 在线考试 / 考试结果 / 历史查询 / 题库管理 / 试卷管理 / AI 助手对话 / 知识库管理 / 合规问答游戏

---

## 五、项目难点与亮点

### 难点

**1. 自研 ORM 框架的安全性与易用性平衡**

没有依赖 SQLAlchemy 等成熟 ORM，而是基于 PyMySQL + Pydantic + DBUtils 从零构建。核心挑战在于：参数化查询强制防 SQL 注入（不允许裸字符串拼接）、多数据库连接的三级优先级路由（实例级 > 类级 > 全局默认）、连接池健康检查与自动恢复、DDL 自动生成（从 Pydantic Field 推导列类型）。在保持底层灵活性的同时，让业务代码只用 `MyModel.find_by(xxx=value)` 即可完成查询。

**2. 主观题 AI 阅卷的可靠性**

合规案例分析等主观题无法靠规则匹配评分。解决方案：设计三层评判架构——(1) 题目自带 `ai_judge_prompt` 定义评分标准；(2) RAG 检索法规原文作为评判上下文；(3) LLM 输出结构化 JSON（score: 0-1 + 详细评判理由）。需要处理 LLM 输出不稳定（JSON 解析容错）、上下文长度控制（RAG 检索结果截断策略）、评分一致性校准等问题。

**3. 混合检索参数调优与评测闭环**

知识库检索质量直接影响 AI 回答准确性。实现了 Milvus 稠密向量（70%）+ BM25 稀疏向量（30%）的混合检索，但权重分配、Chunk 大小、Embedding 维度等参数需要数据驱动优化。为此建立了一整套评测流程：构造评测数据集 → 跑检索评测 → 生成评测（LLM-as-Judge）→ 快照对比 → 参数迭代。这套闭环在业务项目中较少见。

**4. Agent 多意图异步协调**

Agent 需要在单次请求中完成：意图识别 LLM 调用 → 处理器执行（可能涉及 2-3 次 LLM 调用 + 数据库查询 + RAG 检索）→ SSE 流式推送给前端 → 会话持久化到 MySQL + VDB → 异步画像更新。挑战在于：同步/异步边界处理（fastapi 同步路由 vs async generator yield）、SSE 流不能中断（异常吞噬 + 错误事件）、会话缓存在 30 分钟 TTL 内正确维护追问上下文。

**5. 中文知识库分块策略**

通用英文分块（按 `\n\n` 分割）在中文场景效果差。设计了递归分块策略，按分隔符优先级逐级尝试：段落（双换行）→ 单换行 → 中文句号 → 感叹号 → 问号 → 分号 → 逗号 → 通用分隔符 → 空格 → 单字符。同时支持 chunk_overlap 保持语义连贯，chunk 过大时进行二级切分。这个策略直接影响 RAG 检索质量。

### 亮点

**1. 分层架构与行业平移能力**

Base 模块提供 100% 可复用的基础能力（Repository / LLM / Client / Config / Utils），业务模块（CompFox / Education）只关注领域模型和 Prompt。Education（通用教育）→ CompFox（金融合规）的行业平移过程中，架构代码零改动，只换了：数据库表名和字段名、Prompt 文案、配置参数（合规领域/职级/知识点字典）。这种架构设计使得未来扩展到其他行业（医疗、法律、制造）的成本极低。

**2. LLM 供应商抽象**

通过 OpenAI SDK 兼容接口统一了通义千问（DashScope）和 DeepSeek 两个异构 LLM。核心设计：BaseLlm 定义标准接口（chat / achat / invoke / ainvoke / embedding / ocr / asr），通过 capability flags（`supports_ocr` / `supports_asr` / `supports_embedding`）声明能力矩阵，子类只负责设置自己的 api_key / base_url / model。业务代码无需 if-else 判断模型类型。

**3. 对话记忆系统（DB + VDB 混合记忆）**

- MySQL 存储结构化对话记录（精确时间线、session 归属、user_id 关联）
- Milvus VDB 存储对话 Embedding（语义相似度检索）
- 记忆检索：当前 Session 摘要 + VDB 语义相似历史对话（去重 + 相似度阈值过滤）+ DB 最近 N 轮对话
- 解决了纯 DB 方案无法语义检索、纯 VDB 方案丢失精确时间线的问题

**4. 题目质量全生命周期管理**

构建了 50+ 维特征工程宽表，覆盖 5 大类指标：
- **统计特征**：答题次数、正确率、平均分、标准差、区分度
- **干预特征**：干扰项效力（每个错误选项的选择率）、速杀比例（30 秒内做完的占比）、难度漂移（实际难度 vs 预期难度）
- **知识图谱特征**：根因深度、前置知识点缺失率、知识混淆度
- **运维特征**：P99 延迟、AI 置信度均值、数据一致性错误数
- **熔断机制**：加权评分（速杀比 + 难度漂移 + 投诉率），自动流转 Normal → L1 观察 → L2 干预 → L3 冻结（冻结题目不出现在随机出题中）

**5. 试卷版本控制**

修改试卷不覆盖原有记录，而是通过 `parent_id` 创建新版本。支持：版本历史完整追溯、任意历史版本回滚恢复、当前版本发布/归档状态管理。这对金融合规审计至关重要——每次考核的试卷版本可追溯、不可篡改。

**6. Redis 语义缓存链**

对 LLM 的 Embedding、OCR、ASR 调用结果做 Redis 缓存：
- `@cache_with_params` 装饰器，基于函数名 + 参数值自动生成缓存 Key
- 支持自定义 TTL 和序列化格式（JSON/Pickle）
- 缓存命中跳过 API 调用，直接降级读缓存——在 Embedding 场景下命中率极高（相同文本不重复请求 API）
- Redis 不可用时自动降级，不阻塞主流程

**7. 前端零框架依赖**

9 个功能页面全部使用原生 HTML + Vanilla JS + Jinja2 模板，未引入 React/Vue 等前端框架。好处：零构建步骤、部署极简（直接 serve 静态文件）、页面加载快（无 JS bundle 下载解析开销）。代价是复杂交互（如 AI 助手 SSE 流式对话）需要手写 EventSource 处理逻辑。

---

## 六、目录结构

```
D:\AEGIS/
├── Base/                          # 通用基础框架
│   ├── Ai/                        #   LLM 抽象 + Agent 框架 + Prompt
│   │   ├── base/                  #   BaseLlm / BaseAgent / BaseTool / BaseMemory
│   │   ├── llms/                  #   QwenLlm / DeepSeekLlm
│   │   └── agents/                #   NL2CypherAgent
│   ├── Api/                       #   Auth API / Chat API
│   ├── Client/                    #   Redis / Neo4j / Milvus / MinIO / COS / ASR / TTS / Jieba
│   ├── Config/                    #   Pydantic Settings / 日志配置
│   ├── Models/                    #   User / Session / Conversation / Email / Keyword
│   ├── Repository/                #   自研 ORM（BaseDBModel / BaseVDBModel）
│   ├── Service/                   #   Auth / Email / ASR / TTS / Memory / Scheduler / Neo4j
│   ├── RicUtils/                  #   HTTP / RedisCache / Decorator / File / PDF / Excel / Audio
│   ├── Meta/                      #   SingletonMeta
│   ├── DataSet/                   #   ML 数据集工具
│   └── main.py                    #   FastAPI 入口（端口 8010）
│
├── CompFox/                       # 金融合规培训平台
│   ├── api/core/                  #   7 个 API 路由（题目/试卷/考试/Agent/画像/知识库/评测）
│   ├── services/                  #   7 个业务服务
│   ├── models/pojo/               #   MySQL PO 模型（8 个表）
│   ├── models/vdb/                #   Milvus VDB 模型（知识库 + 题目向量）
│   ├── prompts/                   #   Jinja2 Prompt 模板
│   ├── db/                        #   初始化脚本 / Mock 数据 / 测试脚本
│   ├── frontend/                  #   9 个 HTML 页面 + static
│   └── main.py                    #   FastAPI 入口（端口 8003）
│
├── Education/                     # 智能教育 AI 平台（通用教育版）
│   ├── api/core/                  #   5 个 API 路由
│   ├── services/                  #   5 个业务服务
│   ├── models/                    #   PO 模型 + VDB 模型
│   ├── prompts/                   #   Prompt 模板
│   ├── db/                        #   初始化 + Mock 数据
│   ├── frontend/                  #   8 个 HTML 页面 + static（含掘金小游戏）
│   └── main.py                    #   FastAPI 入口（端口 8002）
│
├── docs/                          # 文档
│   ├── compfox-development-spec.md
│   ├── compfox-migration-guide.md
│   └── AEGIS-项目概述.md          # ← 本文档
│
├── logs/                          # 日志输出（按天轮转 + 错误分离）
├── .env                           # 环境变量（30+ 配置项）
├── requirements.txt               # 依赖清单（140+ 包）
└── venv/                          # Python 虚拟环境
```

---

## 七、端口分配

| 端口 | 模块 | 说明 |
|:---:|:---|:---|
| 8010 | Base | Auth 认证 + AI Chat 通用接口 + 定时任务调度 |
| 8003 | CompFox | 金融合规培训全业务 |
| 8002 | Education | 通用教育全业务 |

---

## 八、核心数据表

### CompFox（合规培训）

| 表名 | 说明 | 关键特性 |
|:---|:---|:---|
| `compfox_questions` | 合规题库 | 30+ 字段，支持 text/html/markdown 三种格式，AI 元数据，版本控制，软删除 |
| `compfox_papers` | 合规试卷 | parent_id 版本控制，三维约束组卷，逗号分隔题号+分数 |
| `compfox_exams` | 考试记录 | JSON 答案+分数详情，一人一卷唯一约束，AI 总结 |
| `compfox_answers` | 答题记录 | 按题记录，含 AI 评判完整 trace，source 分类 |
| `compfox_user_profiles` | 员工合规画像 | JSON 字段存储：科目统计/知识掌握度/能力维度/弱点/行为分析/AI 摘要 |
| `compfox_knowledge_document` | 知识文档 | 多格式来源，Chunk 数统计，版本和生效日期，软删除 |
| `question_feature_engineering` | 题目特征工程 | 50+ 维特征宽表，熔断状态机 |

### Milvus 向量集合

| 集合名 | 说明 | 维度 |
|:---|:---|:---:|
| `compliance_knowledge` | 合规知识 Chunk | 1024 稠密 + BM25 稀疏 |
| `question` | 题目语义向量 | 1024 稠密 + BM25 稀疏 |

### Base（基础模块）

| 表名 | 说明 |
|:---|:---|
| `base_user` | 用户账号（argon2 密码哈希） |
| `base_user_token` | JWT Token 存储 |
| `base_llm_conversation` | LLM 对话日志 |
| `base_llm_session` | LLM 会话记录 |
| `base_agent_call_log` | Agent 调用审计 |
| `base_agent_tool_call_log` | Agent 工具调用审计 |
