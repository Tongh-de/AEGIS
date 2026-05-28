# E 教千问 - 智慧教育 AI 平台

> 面向企业合规培训的 AI 智能考核平台，覆盖"出题→组卷→考试→AI判卷→学习画像→知识检索→RAG评测"全链路。

---

## 系统架构总览

```mermaid
flowchart TB
    subgraph Frontend["前端层"]
        A1["答题页<br/>Jinja2 + JS"]
        A2["结果页<br/>Jinja2 + JS"]
        A3["题目管理<br/>Jinja2 + JS"]
        A4["知识库<br/>Jinja2 + JS"]
        A5["合规助手<br/>Jinja2 + JS"]
    end

    subgraph API["接口层 - FastAPI"]
        B1["题目API<br/>/compfox/questions/*"]
        B2["试卷API<br/>/compfox/paper/*"]
        B3["考试API<br/>/compfox/exam/*"]
        B4["Agent API<br/>/compfox/agent/*"]
        B5["知识库API<br/>/compfox/knowledge/*"]
        B6["画像API<br/>/compfox/user/profile/*"]
        B7["评测API<br/>/compfox/evaluation/*"]
    end

    subgraph Service["业务层 - Service"]
        C1["QuestionService<br/>AI出题·审题·阅题·导入导出"]
        C2["PaperService<br/>组卷·配分·版本管理"]
        C3["ExamService<br/>考试·AI判卷·作弊检测"]
        C4["AgentChatService<br/>意图识别·多轮对话·Tool"]
        C5["KnowledgeService<br/>文档解析·分块·混合检索"]
        C6["UserProfileService<br/>学习行为·薄弱分析·画像"]
        C7["EvaluationService<br/>检索评测·生成评测·快照"]
    end

    subgraph Storage["数据层"]
        D1["MySQL<br/>题目/试卷/考试/用户"]
        D2["Milvus<br/>文档向量/题目向量"]
        D3["Neo4j<br/>知识图谱"]
        D4["Redis<br/>缓存/会话"]
    end

    subgraph External["外部集成"]
        E1["通义千问<br/>DashScope API"]
    end

    Frontend -->|HTTP / SSE| API
    API --> Service
    Service --> Storage
    Service --> External
```

---

## 核心模块关系

```mermaid
flowchart LR
    Q["📝 题目管理"] --> P["📄 试卷管理"]
    P --> E["🎯 考试管理"]
    E -->|AI判卷| S["📊 考试结果摘要"]

    A["🤖 AI合规助手"] -->|意图识别| Q
    A -->|意图识别| E
    A -->|RAG问答| K["📚 合规知识库"]
    A -->|画像更新| U["👤 员工画像"]

    K -->|混合检索| M["Milvus"]
    K -->|文档分块| T["文本解析管道"]

    R["🔬 RAG评测系统"] -->|评测集| K
    R -->|快照对比| K

    U -->|薄弱分析| E
```

---

## 模块详情

### 1. 题目管理 `POST/GET/PUT/DELETE /compfox/questions/*`

```mermaid
flowchart TB
    subgraph Create["题目生成"]
        IN1["手动录入"] --> DB[(MySQL)]
        IN2["AI 随机出题"] -->|LLM| DB
        IN3["Excel 批量导入"] --> DB
        IN4["文件导入<br/>PDF/Word/TXT"] -->|AI 提取| DB
    end

    subgraph Process["题目处理"]
        DB --> AI_REVIEW["AI 审题<br/>质量打分·优化建议"]
        DB --> AI_PARSE["AI 解析<br/>解题思路·知识点"]
    end

    subgraph Judge["阅题"]
        DB --> AI_JUDGE["AI 阅题<br/>正误判断·错因分析"]
    end

    subgraph Export["导出"]
        DB --> EXPORT["Excel 导出<br/>题干/答案/解析"]
    end
```

| 功能 | 说明 |
|------|------|
| CRUD + 分页搜索 | 按合规领域/题型/职级/难度过滤 |
| AI 随机出题 | LLM 按参数生成题干+答案+解析，写入库 |
| AI 审题 | LLM 从合规性、难度匹配、表述清晰度三维打分 |
| AI 阅题 | 主观题 LLM 按关键点评分，客观题字符串比对 |
| Excel 导入导出 | 批量操作 + 查重去重 |
| 文件导入 | PDF/Word/TXT → AI 提取题目结构 |

---

### 2. 试卷管理 `POST/GET/PUT/DELETE /compfox/paper/*`

```mermaid
flowchart LR
    subgraph CRUD["试卷生命周期"]
        P_CREATE["创建<br/>选题目+配分"] --> P_LIST["列表<br/>分页查询"]
        P_LIST --> P_UPDATE["更新<br/>追加新版本"]
        P_UPDATE --> P_VERSION["版本树<br/>parent_id 关联"]
        P_VERSION --> P_RESTORE["恢复<br/>还原历史版本"]
        P_LIST --> P_DELETE["软删除"]
    end
```

| 功能 | 说明 |
|------|------|
| 创建试卷 | 多题目关联 + 每题独立配分 |
| 版本管理 | 更新不覆盖，追加新版本，历史可恢复 |
| 恢复版本 | 从版本历史中选取某版还原 |

---

### 3. 考试管理 `POST/GET /compfox/exam/*`

```mermaid
sequenceDiagram
    participant U as 员工
    participant E as ExamService
    participant LLM as LLM
    participant DB as MySQL

    U->>E: 开始考试(paper_id)
    E->>DB: 创建 exam(ongoing)
    E-->>U: 试卷题目 + 计时

    U->>E: 提交答案(question_id->answer)
    E->>E: 客观题 → 字符串比对
    E->>LLM: 主观题 → AI评分
    LLM-->>E: 评分结果
    E->>E: 计算总分
    E->>LLM: 考试总结生成
    LLM-->>E: 薄弱分析 + 复训建议
    E-->>U: 完整报告
```

| 功能 | 说明 |
|------|------|
| 开始考试 | 创建考试记录，每人每卷限一次 |
| 提交判卷 | 客观题比对 + 主观题 LLM 评分 |
| AI 考试总结 | 成绩总结 + 薄弱分析 + 复训建议 + 风险等级 |
| 作弊检测 | LLM 分析答题用时/答案模式 |
| 结果查询 | 每题得分详情 + AI 评语 + 分析 |
| 历史记录 | 按用户查询历史考核 |

**判卷流程：**

```mermaid
flowchart LR
    A["用户答案"] --> B{"题目类型?"}
    B -->|"单选/多选/判断"| C["字符串比对<br/>排序后比较"]
    B -->|"简答/论述/案例"| D["LLM 评分<br/>CoT 按关键点给分"]
    C --> E["得分"]
    D --> E
```

---

### 4. AI 合规助手 `POST/GET /compfox/agent/*`

```mermaid
flowchart TB
    subgraph Agent["Agent 工作流"]
        IN["用户输入"] --> INTENT["🧠 意图识别<br/>LLM 分类"]
        INTENT -->|"出题"| TOOL_Q["Tool: 出题"]
        INTENT -->|"判题"| TOOL_J["Tool: 判题"]
        INTENT -->|"推荐考题"| TOOL_R["Tool: 推荐"]
        INTENT -->|"合规咨询"| RAG["RAG 检索+LLM"]
        INTENT -->|"培训进度"| PROFILE["查询画像"]
        INTENT -->|"通用对话"| CHAT["直接 LLM 回答"]
        TOOL_Q & TOOL_J & TOOL_R & RAG & PROFILE & CHAT --> SSE["SSE 流式输出"]
        SSE --> OUT["用户可见"]
    end

    subgraph Side["副作用"]
        SSE --> UPDATE["异步更新用户画像"]
    end
```

| 功能 | 说明 |
|------|------|
| 意图识别 | 6 种意图分类（出题/判题/解析/合规咨询/培训进度/通用对话） |
| 流式输出 | SSE 流式，支持 thinking 思考过程展示 |
| 会话管理 | session_id + 上下文持久化 |
| RAG 问答 | 检索知识库 + LLM 生成 + 引用来源 |
| Tool 调用 | 内部调用题目/试卷/画像服务 |

---

### 5. 合规知识库 `POST/GET/DELETE /compfox/knowledge/*`

```mermaid
flowchart TB
    subgraph Import["文档导入"]
        I1["纯文本"] --> PARSER["文档解析器"]
        I2["PDF"] -->|PyMuPDF| PARSER
        I3["Word"] -->|python-docx| PARSER
        I4["Excel"] -->|openpyxl| PARSER
        I5["URL"] -->|HTTP 爬取| PARSER
    end

    subgraph Vectorize["向量化"]
        PARSER --> CHUNK["递归字符分割<br/>chunk_size=512 overlap=64"]
        CHUNK --> EMBED["Embedding<br/>text2vec-base"]
        EMBED --> MILVUS[("Milvus<br/>HNSW索引")]
    end

    subgraph Retrieve["检索"]
        Q["Query"] --> HYBRID["混合检索"]
        MILVUS -->|"语义(0.7)"| HYBRID
        BM25 -->|"BM25(0.3)"| HYBRID
        HYBRID --> RESULT["TOP K + 来源 + 高亮"]
    end
```

| 功能 | 说明 |
|------|------|
| 文档导入 | 文本/PDF/Word/Excel/URL 爬取 |
| 文档分块 | 递归字符分割，chunk_size=512, overlap=64 |
| 向量化 | text2vec-base → Milvus |
| 混合检索 | 向量(0.7) + BM25(0.3) 加权融合，recall@10=91% |

---

### 6. 员工合规画像 `GET/POST /compfox/user/profile/*`

```mermaid
flowchart LR
    subgraph Source["数据来源"]
        S1["答题记录<br/>examService"]
        S2["对话记录<br/>agentChatService"]
    end

    subgraph Analysis["分析"]
        S1 --> AGG["知识点聚合<br/>正确率统计"]
        S2 --> STYLE["行为模式<br/>学习时间/周期"]
        AGG --> WEAK["薄弱领域<br/><60% 标红"]
    end

    subgraph Output["输出"]
        WEAK --> REPORT["画像报告"]
        STYLE --> REPORT
    end
```

| 功能 | 说明 |
|------|------|
| 画像获取 | 基本信息 + 学习统计 + 薄弱领域 + 趋势 |
| 学习行为分析 | 总题数、正确率、练习时长、连续天数 |
| 画像更新 | 每次答题/对话后实时更新 |
| 画像分析 | 学习风格推断（拖延/勤奋/规律/突击） |

---

### 7. RAG 评测系统 `POST/GET /compfox/evaluation/*`

```mermaid
flowchart TB
    subgraph Dataset["评测数据集"]
        D["(query, expected_doc_id) 对"]
    end

    subgraph RetrievalEval["检索评测"]
        D --> RUN["跑不同参数组合"]
        RUN --> M1["chunk_size"]
        RUN --> M2["overlap"]
        RUN --> M3["λ(向量权重)"]
        M1 & M2 & M3 --> RECALL["recall@k 对比"]
    end

    subgraph GenerationEval["生成评测"]
        D --> GEN["RAG 生成回答"]
        GEN --> LLM_JUDGE["LLM-as-Judge<br/>相关性·准确性·完整性"]
    end

    subgraph Snapshot["快照对比"]
        RECALL --> SNAP["保存结果"]
        LLM_JUDGE --> SNAP
        SNAP --> COMPARE["版本对比"]
    end
```

| 功能 | 说明 |
|------|------|
| 检索评测 | 评测集跑不同参数，算 recall@k |
| 生成评测 | LLM-as-Judge 评回答质量 |
| 快照对比 | 多版本保存 + 参数对比 |

---

## 数据层设计

### MySQL 核心表

```mermaid
erDiagram
    QuestionPo ||--o{ PaperPo : "包含"
    PaperPo ||--o{ ExamPo : "关联"
    ExamPo ||--o{ AnswerPo : "产生"

    QuestionPo {
        int id PK
        string question_text
        string answer
        string question_type
        int grade
        int difficulty_level
        string subject
        string source
    }

    PaperPo {
        int id PK
        int parent_id "版本根ID"
        string paper_name
        string question_ids "逗号分隔"
        string scores "逗号分隔"
        int duration_minutes
    }

    ExamPo {
        int id PK
        string exam_uuid UK
        int paper_id FK
        string user_id
        json answers
        int total_score
        string status
    }

    AnswerPo {
        int id PK
        int question_id FK
        string user_id
        double score
        string ai_model
    }
```

### 向量数据库（Milvus）

| 集合 | 说明 | 索引 |
|------|------|------|
| knowledge_chunks | 知识文档向量 | HNSW, Metric=L2 |
| question_embeddings | 题目向量（备用） | HNSW, Metric=L2 |

### 图数据库（Neo4j）

```
五类实体：员工 - 岗位 - 技能 - 课程 - 考试
关系：员工→岗位(任职), 岗位→技能(需要), 课程→技能(培养), 考试→课程(考核)
用于：知识图谱增强 RAG 上下文
```

---

## 技术栈

| 层级 | 选型 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI |
| ORM | SQLAlchemy |
| 在线数据库 | MySQL + Redis |
| 向量数据库 | Milvus（HNSW 索引，Partition 多租户） |
| 图数据库 | Neo4j |
| LLM | 通义千问（DashScope API） |
| Agent 框架 | LangChain ReAct |
| 前端 | Jinja2 模板 + 原生 JavaScript |
| 容器化 | Docker + docker-compose |
| RAG | 自定义混合检索（向量 + BM25） |
| 评测 | LLM-as-Judge 自动化 |

---

## 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/lc4t/AEGIS
cd AEGIS

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env：数据库连接、LLM API Key、Milvus 地址等

# 4. 初始化数据库
python -m CompFox.models.init_db

# 5. 启动服务
uvicorn CompFox.main:app --reload --port 8003

# 或 Docker 部署
docker-compose up -d
```

---

## 目录结构

```
CompFox/
├── main.py                    # 应用入口 (port 8003)
├── api/
│   ├── router.py              # 路由注册
│   └── core/
│       ├── questionApi.py     # 题目管理（CRUD + AI + 导入导出）
│       ├── paperApi.py        # 试卷管理（CRUD + 版本）
│       ├── examApi.py         # 考试管理（开始+提交+判卷+结果）
│       ├── agentChatApi.py    # AI 合规助手（Agent + 流式输出）
│       ├── userProfileApi.py  # 员工合规画像
│       ├── knowledgeApi.py    # 合规知识库（RAG）
│       └── evaluationApi.py   # RAG 评测系统
├── services/                  # 业务逻辑层
│   ├── questionService.py     # 509行
│   ├── agentChatService.py    # 1050行（最大模块）
│   ├── examService.py         # 463行
│   └── ...
├── models/
│   ├── pojo/                  # POJO 实体（MySQL 表映射）
│   └── vdb/                   # 向量数据库模型
├── prompts/                   # LLM 提示词
├── frontend/                  # 前端静态页面
└── docs/                      # 简历包装文档
```

---

## 文档

| 文档 | 用途 |
|------|------|
| [`docs/CompFox项目梳理.md`](./docs/CompFox项目梳理.md) | 项目全貌 + 面试话术 |
| [`docs/AI应用开发_专业技能模块.md`](./docs/AI应用开发_专业技能模块.md) | 简历技能栏写法 |
| [`docs/面试话术.md`](./docs/面试话术.md) | 面试问答模板 |

---

> 项目状态：开发中 | 许可证：MIT
