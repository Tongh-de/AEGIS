<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python" alt="Python 3.13">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LLM-Qwen%20%7C%20DeepSeek-orange" alt="LLM: Qwen | DeepSeek">
  <img src="https://img.shields.io/badge/Vector-Milvus-00A1EA?logo=milvus" alt="Milvus">
  <img src="https://img.shields.io/badge/Graph-Neo4j-008CC1?logo=neo4j" alt="Neo4j">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

# AEGIS — AI 驱动的企业级培训考核平台

> AI-powered Enterprise Training & Assessment Platform with full lifecycle coverage.

---

## Monorepo 架构总览

```mermaid
flowchart TB
    subgraph Base["Base 基础框架（端口 8010）"]
        direction TB
        B1["自研 ORM<br/>BaseDBModel + BaseVDBModel"]
        B2["LLM 抽象层<br/>BaseLlm ↔ QwenLlm / DeepSeekLlm"]
        B3["Agent 框架<br/>ReAct / CoT / Plan-and-Execute"]
        B4["客户端封装<br/>Redis / Neo4j / Milvus / MinIO / COS / TTS/ASR"]
        B5["工具库<br/>HTTP / 缓存 / PDF / Excel / 音频"]
    end

    subgraph CompFox["CompFox·合规狐（端口 8003）"]
        direction TB
        C_API["API 层<br/>7 个路由模块"]
        C_SVC["Service 层<br/>7 个业务服务"]
        C_PO["MySQL PO<br/>8 张业务表"]
        C_VDB["Milvus 集合<br/>知识向量 + 题目向量"]
        C_PROMPT["Prompt 层<br/>Jinja2 模板"]
        C_FE["前端层<br/>9 个 HTML 页面"]
    end

    subgraph Education["Education·E教千问（端口 8002）"]
        direction TB
        E_API["API 层<br/>5 个路由模块"]
        E_SVC["Service 层<br/>5 个业务服务"]
        E_PO["MySQL PO<br/>业务表"]
        E_VDB["Milvus 集合"]
        E_PROMPT["Prompt 层"]
        E_FE["前端层<br/>8 个 HTML 页面"]
    end

    CompFox -->|"继承/复用"| Base
    Education -->|"继承/复用"| Base
```

---

## 模块定位

| 模块 | 定位 | 端口 | 说明 |
|:---|:---|:---:|:---|
| **Base** | 通用基础框架 | 8010 | ORM、LLM 抽象、Agent、客户端封装、工具库 |
| **CompFox（合规狐）** | 金融合规培训与能力评估 | 8003 | 面向银行/证券/保险的合规考核平台 |
| **Education（E教千问）** | 智能教育 AI 平台 | 8002 | 面向学校的 AI 教学辅助平台 |

---

## 核心业务流程

```mermaid
flowchart LR
    Q["📝 合规题库<br/>AI生成 + 人工 + Excel导入"] --> P["📄 自动组卷<br/>题型/难度/知识点约束"]
    P --> E["🎯 在线考核<br/>限时答题 · 一人一卷"]
    E --> J["🤖 AI 阅卷<br/>客观规则 + 主观LLM + RAG对照"]
    J --> U["👤 员工画像<br/>雷达图 · 薄弱分析 · 行为"]
    U --> R["🎯 复训推荐<br/>个性化题目推荐"]
```

---

## 技术栈

```mermaid
flowchart LR
    subgraph Lang["语言 & 框架"]
        L1["Python 3.13"]
        L2["FastAPI + Uvicorn"]
    end

    subgraph DB["数据层"]
        D1["MySQL<br/>InnoDB utf8mb4"]
        D2["Milvus<br/>1024维 + BM25 混合"]
        D3["Neo4j<br/>法规-案例-处罚图谱"]
        D4["Redis<br/>缓存/会话"]
        D5["MinIO / COS<br/>对象存储"]
    end

    subgraph AI["AI 层"]
        A1["通义千问 Qwen3-Max"]
        A2["DeepSeek Chat"]
        A3["自研 Agent<br/>ReAct/CoT/P&E"]
        A4["自研 RAG<br/>稠密+稀疏混合"]
    end

    subgraph Front["前端"]
        F1["原生 HTML + Vanilla JS"]
        F2["Jinja2 模板"]
    end

    subgraph Dep["部署"]
        P1["Docker"]
        P2["docker-compose"]
    end

    DB --> Lang
    AI --> Lang
    Front --> Lang
    Lang --> Dep
```

| 层级 | 技术选型 |
|:---|:---|
| 语言 | Python 3.13 |
| Web 框架 | FastAPI + Uvicorn（异步 + 同步混合，SSE 流式响应） |
| ORM | **自研**（PyMySQL + Pydantic + DBUtils，参数化查询防 SQL 注入） |
| LLM | 通义千问 Qwen3-Max / DeepSeek Chat，OpenAI SDK 统一接口，一键切换 |
| Agent 框架 | **自研** ReAct / CoT / Plan-and-Execute 多范式，Tool 注册 + Memory 管理 |
| 向量数据库 | Milvus（1024 维稠密向量 + BM25 稀疏向量混合检索） |
| 图数据库 | Neo4j（法规-案例-处罚关系图谱） |
| 关系数据库 | MySQL（InnoDB, utf8mb4） |
| 缓存 | Redis（LLM 结果缓存、会话上下文） |
| 对象存储 | MinIO / 腾讯云 COS |
| 语音 | 通义千问 ASR（语音转文字）/ TTS（文字转语音） |
| 前端 | 原生 HTML + Vanilla JS + Jinja2 模板渲染 |
| 部署 | Docker + docker-compose |

---

## 核心亮点

### 1. 自研 ORM 框架

```mermaid
flowchart LR
    P["PyMySQL<br/>连接池"] --> S["SQL 生成器<br/>参数化查询"]
    S --> T["类型映射<br/>Pydantic ↔ MySQL"]
    T --> R["三级路由<br/>实例>类>全局"]
    R --> H["健康检查<br/>自动恢复"]
```

不依赖 SQLAlchemy，从零构建。参数化查询强制防 SQL 注入，三级优先级数据库路由（实例级 > 类级 > 全局默认），连接池健康检查与自动恢复，DDL 自动生成。

### 2. AI Agent 多范式框架

```mermaid
flowchart TB
    subgraph Paradigms["三种 Agent 范式"]
        REACT["ReAct<br/>Reason → Act → Loop"]
        COT["CoT<br/>Chain of Thought"]
        PNE["Plan-and-Execute<br/>分步执行"]
    end

    subgraph Tools["Tool 注册"]
        T1["@tool 装饰器"]
        T2["自动 Schema 生成"]
        T3["Tool 选择器"]
    end

    subgraph Features["业务能力"]
        F1["6 意图识别"]
        F2["SSE 流式响应"]
        F3["思考过程可视化"]
    end

    Paradigms --> Tools --> Features
```

实现 ReAct、CoT、Plan-and-Execute 三种 Agent 范式，`@tool` 装饰器自动注册机制。业务中实现 6 意图识别 + SSE 流式响应 + 思考过程可视化的对话系统。

### 3. 主观题 AI 阅卷

```mermaid
flowchart TB
    A["用户答案"] --> S["三步评判"]
    S --> L1["① 题目自带评分标准 Prompt"]
    S --> L2["② RAG 检索法规原文"]
    S --> L3["③ LLM 输出结构化 JSON"]
    L3 --> O["score + 评判理由"]
```

三层评判架构，解决合规案例分析类主观题的自动评分难题。

### 4. RAG 混合检索与评测闭环

```mermaid
flowchart LR
    subgraph Ret["混合检索"]
        R1["稠密向量<br/>Milvus 0.7"]
        R2["稀疏向量<br/>BM25 0.3"]
        R1 --> W["加权融合"]
        R2 --> W
    end

    subgraph Eval["评测"]
        E1["Precision@k"]
        E2["Recall@k"]
        E3["NDCG@k"]
        E4["LLM-as-Judge"]
    end

    subgraph Iter["迭代"]
        I1["chunk_size 调优"]
        I2["overlap 调优"]
        I3["λ 权重调优"]
    end

    Ret --> Eval --> Iter --> Ret
```

Milvus 稠密向量（70%）+ BM25 稀疏向量（30%）混合检索，中文递归分块策略。自建评测数据集，快照对比驱动参数迭代。

### 5. 试卷版本控制

```mermaid
flowchart LR
    V1["v1<br/>id=1"] --> V2["v2<br/>id=2, parent=1"]
    V2 --> V3["v3<br/>id=3, parent=1"]
    V3 --> V4["v4<br/>id=4, parent=1"]
    V2 -.->|"恢复"| V5["v5<br/>id=5, parent=1"]
```

修改不覆盖，`parent_id` 创建新版本。支持版本历史追溯与回滚，满足金融合规审计要求。

### 6. 题目质量全生命周期管理

```
50+ 维特征宽表：
  - 统计特征：正确率、区分度
  - 干预特征：干扰项效力
  - 知识图谱特征
  - 运维特征

熔断状态机：Normal → L1观察 → L2干预 → L3冻结
```

### 7. 行业平移能力

```mermaid
flowchart TB
    subgraph SRC["Education（通用教育）"]
        S_MODEL["数据模型"]
        S_PROMPT["Prompt 文案"]
        S_CONFIG["配置参数"]
    end

    subgraph COMMON["Base 基础框架（零改动）"]
        CODE["ORM / LLM / Agent / Client<br/>100% 复用"]
    end

    subgraph DST["CompFox（金融合规）"]
        D_MODEL["数据模型 ✅ 替换"]
        D_PROMPT["Prompt 文案 ✅ 替换"]
        D_CONFIG["配置参数 ✅ 替换"]
    end

    SRC --> COMMON
    COMMON --> DST
```

Education（通用教育）→ CompFox（金融合规）的行业平移过程中，架构代码零改动，只换了数据模型、Prompt 文案和配置参数。

---

## 项目目录

```
D:\AEGIS/
├── Base/                          # 通用基础框架
│   ├── Ai/                        #   LLM 抽象 + Agent 框架 + Prompt
│   │   ├── base/                  #   BaseLlm / BaseAgent / BaseTool / BaseMemory
│   │   ├── llms/                  #   QwenLlm / DeepSeekLlm
│   │   └── agents/                #   NL2CypherAgent
│   ├── Api/                       #   Auth API / Chat API
│   ├── Client/                    #   Redis / Neo4j / Milvus / MinIO / COS / TTS
│   ├── Config/                    #   Pydantic V2 Settings / 日志配置
│   ├── Models/                    #   User / Session / Conversation
│   ├── Repository/                #   自研 ORM（BaseDBModel / BaseVDBModel）
│   ├── Service/                   #   Auth / Email / ASR / TTS / Memory
│   ├── RicUtils/                  #   HTTP / RedisCache / PDF / Excel / Audio
│   └── main.py                    #   FastAPI 入口（端口 8010）
│
├── CompFox/                       # 金融合规培训平台
│   ├── api/core/                  #   7 个 API 路由
│   ├── services/                  #   7 个业务服务
│   ├── models/pojo/               #   MySQL PO 模型（8 个表）
│   ├── models/vdb/                #   Milvus VDB 模型
│   ├── prompts/                   #   Jinja2 Prompt 模板
│   ├── db/                        #   初始化 / Mock 数据 / 测试脚本
│   ├── frontend/                  #   9 个 HTML 页面 + static
│   └── main.py                    #   FastAPI 入口（端口 8003）
│
├── Education/                     # 智能教育 AI 平台
│   ├── api/core/                  #   5 个 API 路由
│   ├── services/                  #   5 个业务服务
│   ├── models/                    #   PO 模型 + VDB 模型
│   ├── prompts/                   #   Prompt 模板
│   ├── db/                        #   初始化 + Mock 数据
│   ├── frontend/                  #   8 个 HTML 页面 + static
│   └── main.py                    #   FastAPI 入口（端口 8002）
│
├── docs/                          # 项目文档
├── logs/                          # 日志输出
├── .env.template                  # 环境变量模板
├── .env.docker                    # Docker 部署环境变量
├── requirements.txt               # 依赖清单
└── docker-compose.yml             # Docker 编排
```

---

## 快速启动

### 前置依赖

- Python 3.13+
- MySQL 8.0+
- Redis
- Milvus 2.4+
- Neo4j（可选）
- MinIO（可选）

### 1. 克隆 & 配置

```bash
git clone https://github.com/<your-username>/AEGIS.git
cd AEGIS

# 复制环境变量模板并填入真实值
cp .env.template .env
```

### 2. 安装依赖

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS for_student CHARACTER SET utf8mb4;"

# 初始化 CompFox 题库表
python CompFox/db/questionDbInit.py
```

### 4. 启动服务

```bash
# 方式一：单模块启动
uvicorn CompFox.main:app --host 0.0.0.0 --port 8003 --reload

# 方式二：Docker 部署
docker-compose up -d
```

### 5. 访问

| 服务 | 地址 |
|:---|:---|
| CompFox | http://localhost:8003 |
| Education | http://localhost:8002 |
| API 文档 | http://localhost:8003/docs |

---

## 端口分配

| 端口 | 模块 | 说明 |
|:---:|:---|:---|
| 8003 | CompFox | 金融合规培训全业务 |
| 8002 | Education | 智能教育全业务 |
| 8010 | Base | Auth 认证 + AI Chat + 定时任务 |

---

## 核心数据表

### CompFox（合规培训）

| 表名 | 说明 | 关键特性 |
|:---|:---|:---|
| `compfox_questions` | 合规题库 | 30+ 字段，3 种格式支持，AI 元数据，版本控制，软删除 |
| `compfox_papers` | 合规试卷 | `parent_id` 版本控制，三维约束组卷 |
| `compfox_exams` | 考试记录 | JSON 答案+分数详情，一人一卷，AI 总结 |
| `compfox_answers` | 答题记录 | 按题记录，含 AI 评判完整 trace |
| `compfox_user_profiles` | 员工合规画像 | JSON 统计/掌握度/弱点/行为分析/AI 摘要 |
| `question_feature_engineering` | 题目特征工程 | 50+ 维特征，熔断状态机 |

### Milvus 向量集合

| 集合名 | 说明 | 维度 |
|:---|:---|:---:|
| `compliance_knowledge` | 合规知识 Chunk | 1024 稠密 + BM25 稀疏 |
| `question` | 题目语义向量 | 1024 稠密 + BM25 稀疏 |

---

## RAG 评测结果

| 配置 | Precision@3 | Recall@5 | MRR | NDCG@5 |
|:---|:---:|:---:|:---:|:---:|
| Chunk 300, Overlap 50 | 0.73 | 0.72 | 0.80 | 0.70 |
| Chunk 500, Overlap 80 | 0.60 | 0.65 | 0.72 | 0.62 |

---

## 文档

- [项目概述](docs/AEGIS-项目概述.md) — 整体介绍、架构、技术选型
- [CompFox 技术规格书](docs/compfox-development-spec.md) — 详细设计与开发规范
- [行业迁移指南](docs/compfox-migration-guide.md) — Education → CompFox 改造记录

---

## 许可

本项目基于 [MIT License](LICENSE) 开源。

---

<p align="center">
  Built with ❤️ and Python
</p>
