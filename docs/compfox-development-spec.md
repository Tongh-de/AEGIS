# CompFox 金融合规培训平台 — 技术规格书 V1.0

> 项目代号：CompFox（合规狐）
> 基于 ric-train 项目架构平移到金融合规行业

---

## 一、项目概述

### 1.1 定位

面向金融机构（银行/证券/保险/基金）的 **AI 合规培训与能力评估平台**，覆盖"合规题库 → 自动组卷 → 在线考核 → AI 阅卷（含主观题）→ 能力画像 → 复训推荐"全闭环。

### 1.2 核心价值

- 替代传统"发试卷-人工阅卷-统计"的低效模式
- AI 能够评判主观题（合规案例分析），传统系统做不了
- 员工能力画像驱动精准复训，替代"所有人做同一套题"

### 1.3 技术栈

| 层 | 技术 |
|:---|:---|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI + uvicorn（异步 + 同步混合） |
| 配置 | Pydantic V2 + .env |
| ORM | 自研（基于 aiomysql，PO 模型驱动，参数化查询） |
| LLM | 通义千问（qwen3-max）/ DeepSeek（deepseek-chat），支持一键切换 |
| 向量库 | Milvus（对话记忆 + 语义检索） |
| 图库 | Neo4j（法规-案例-处罚关系图谱） |
| 缓存 | Redis |
| 文件存储 | MinIO / 腾讯云 COS |
| 语音 | 通义千问 ASR（可选） |
| 部署 | Docker + docker-compose |

### 1.4 端口分配

| 端口 | 模块 |
|:---|:---|
| 8010 | Base 基础服务（Auth + AI Chat + 定时任务） |
| 8003 | CompFox 合规业务（建议 8003，区别于原 Education 的 8002） |

---

## 二、目录结构

```
CompFox/                        # 业务模块（从 Education 复制改造）
├── __init__.py
├── main.py                     # FastAPI 入口 + 路由注册 + 前端挂载
├── api/
│   ├── router.py               # 路由汇总
│   └── core/
│       ├── questionApi.py      # 合规题库 API
│       ├── paperApi.py         # 合规试卷 API
│       ├── examApi.py          # 合规考核 API
│       ├── agentChatApi.py     # 合规助手 API（Agent）
│       └── userProfileApi.py   # 员工合规画像 API
├── services/
│   ├── questionService.py      # 合规题库服务 + AI 出题 + AI 阅卷
│   ├── paperService.py         # 合规试卷服务（自动组卷 + 版本管理）
│   ├── examService.py          # 合规考核服务（开始/提交/判卷/总结/历史）
│   ├── agentChatService.py     # 合规助手服务（意图识别 + 6 意图分发）
│   └── userProfileService.py   # 员工合规画像服务
├── models/
│   └── pojo/
│       ├── questionPo.py       # 合规考题 PO 模型
│       ├── paperPo.py          # 合规试卷 PO 模型
│       ├── examPo.py           # 合规考核 PO 模型
│       ├── answerPo.py         # 答题记录 PO 模型
│       ├── userProfilePo.py    # 员工合规画像 PO 模型
│       ├── questionBo.py       # 出题/阅卷 BO 模型
│       ├── agentChatBo.py      # Agent 聊天 BO 模型
│       └── ...                 # 其他 BO/PO
├── prompts/                    # ===== 核心：行业 Prompt =====
│   ├── __init__.py
│   ├── common.py               # 通用模板渲染
│   ├── questionPrompts.py      # 出题 + 阅卷 + 导入 Prompt
│   ├── examPrompts.py          # 考试总结 + 舞弊检测 Prompt
│   └── agentPrompts.py         # Agent 6 意图 Prompt
└── frontend/                   # 前端页面（HTML 静态，FastAPI 挂载）
    ├── register.py             # 前端路由注册
    ├── doQuestion.html         # 合规考核页面
    ├── exam_result.html        # 考核结果页面
    ├── history.html            # 考核记录页面
    └── userProfile.html        # 合规画像页面
```

---

## 三、数据模型

### 3.1 核心表结构

#### questions（合规考题表）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 主键 |
| question_uuid | VARCHAR(36) | 题目 UUID |
| question_text | TEXT | 题干 |
| question_markdown | TEXT | Markdown 格式题干 |
| question_type | VARCHAR(20) | single_choice / multiple_choice / judgement / fill_blank / short_answer / essay |
| subject | VARCHAR(50) | 合规领域（aml / data_security / insider_trading / ...） |
| difficulty_level | INT | 难度等级 1-5 |
| difficulty_label | VARCHAR(20) | basic / intermediate / advanced |
| knowledge_points | VARCHAR(500) | 合规知识点（逗号分隔） |
| answer | TEXT | 标准答案 |
| analysis | TEXT | 解析 |
| ai_judge_prompt | TEXT | AI 阅卷提示词 |

> 相比教育版，改：subject 取值、knowledge_points 取值、示例数据

#### papers（合规试卷表）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 主键 |
| paper_name | VARCHAR(200) | 试卷名称，如"2025 反洗钱合规年度考核-A卷" |
| subject | VARCHAR(50) | 合规领域 |
| question_ids | TEXT | 题目 ID 列表（逗号分隔） |
| scores | TEXT | 每题分值（逗号分隔） |
| duration_minutes | INT | 考试时长 |
| total_score | DECIMAL | 总分 |
| pass_score | DECIMAL | **合格线（新增，教育版不需要）** |
| status | VARCHAR(20) | draft / published / archived |
| version | INT | 版本号 |

> 相比教育版，新增 `pass_score` 字段

#### exams（合规考核记录表）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | BIGINT PK | 主键 |
| exam_uuid | VARCHAR(36) | 考核 UUID |
| paper_id | BIGINT | 试卷 ID |
| user_id | VARCHAR(50) | 员工 ID（工号） |
| answers | JSON | 答卷 |
| total_score | DECIMAL | 总得分 |
| score_details | JSON | 每题得分详情 |
| ai_summary | TEXT | AI 评估总结 |
| ai_scoring_basis | TEXT | AI 评分依据 |
| passed | TINYINT | **是否合格（新增）** |
| status | VARCHAR(20) | ongoing / submitted / graded |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 提交时间 |

> 相比教育版，新增 `passed` 字段

#### user_profiles（员工合规画像表）

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| user_id | VARCHAR(50) | 员工 ID |
| total_exams | INT | 累计考核次数 |
| total_correct_rate | DECIMAL | 总体合规掌握率 |
| subject_stats | JSON | 各合规领域统计 |
| knowledge_mastery | JSON | 合规知识点掌握情况 |
| compliance_risk_level | VARCHAR(20) | **合规风险等级（新增）：low / medium / high** |
| weak_points | JSON | 薄弱合规知识点 |
| last_exam_date | DATE | 最近考核日期 |
| retrain_count | INT | **复训次数（新增）** |
| ai_summary | TEXT | AI 合规能力评估总结 |

> 相比教育版，新增：`compliance_risk_level`、`retrain_count`；改：字段注释

---

## 四、API 接口清单

### 4.1 合规题库 APIs（/compfox/question）

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| POST | /compfox/question/generate | AI 生成合规考题 |
| POST | /compfox/question/import | 批量导入合规考题 |
| GET | /compfox/question/random | 随机抽题 |
| GET | /compfox/question/search | 搜索合规考题 |
| GET | /compfox/question/detail | 获取题目详情 |
| POST | /compfox/question/judge | AI 阅卷单题 |

### 4.2 合规试卷 APIs（/compfox/paper）

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| POST | /compfox/paper/create | 创建合规试卷 |
| PUT | /compfox/paper/update | 更新试卷 |
| GET | /compfox/paper/detail | 获取试卷详情 |
| POST | /compfox/paper/publish | 发布试卷 |
| GET | /compfox/paper/list | 试卷列表 |

### 4.3 合规考核 APIs（/compfox/exam）

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| POST | /compfox/exam/start | 开始考核 |
| POST | /compfox/exam/{exam_id}/submit | 提交答卷 |
| GET | /compfox/exam/result | 查看考核结果 |
| GET | /compfox/exam/history | 考核历史记录 |
| POST | /compfox/exam/{exam_id}/grade | 手动判卷 |

### 4.4 合规助手 APIs（/compfox/agent）

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| POST | /compfox/agent/chat | 合规助手对话（含意图识别） |
| POST | /compfox/agent/chat/stream | 流式对话 |

### 4.5 员工合规画像 APIs（/compfox/user/profile）

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| GET | /compfox/user/profile | 获取员工画像 |
| POST | /compfox/user/profile/refresh | 刷新 AI 画像总结 |
| GET | /compfox/user/profile/report | 获取合规培训报告 |
| GET | /compfox/user/profile/recommendations | 获取复训推荐 |
| GET | /compfox/user/profile/behavior | 获取行为分析 |

> 相比教育版，prefix 从 `/education/` 改为 `/compfox/`，tags 文案调整

---

## 五、Prompt 改写方案（核心工作量）

### 5.1 出题 Prompt（questionPrompts.py）

**改**：行业语境、示例题目、题型说明

```python
# 关键替换点
{{subject}}        # 取值：aml / data_security / insider_trading / ...
{{question_type}}  # 不变：single_choice / multiple_choice / ...
```

**示例题目改造**：

```
# 原（数学题）
HTTP 协议默认使用的端口号是？(   )
A. 21  B. 443  C. 80  D. 8080

# 改（合规题）
根据《金融机构反洗钱规定》，客户身份资料在业务关系结束后应至少保存多少年？(   )
A. 3年  B. 5年  C. 10年  D. 永久
```

### 5.2 阅卷 Prompt（examPrompts.py）

**改**：角色从"阅卷老师"改为"合规评审专家"，评分标准增加"风险点遗漏扣分"

```python
# 关键改动
"你是一位严格的金融合规评审专家"  # 替代 "你是一位公正严谨的阅卷老师"
"对于案例分析题，请特别关注答案中是否遗漏了：\n1. 关键风险识别\n2. 法规依据引用\n3. 处置措施完整性"  # 新增
```

### 5.3 考试总结 Prompt（examPrompts.py）

**改**：从"学习建议"改为"复训建议"，增加"风险等级判定"

```python
# 关键改动
"1. 成绩总结：总分、合格/不合格判定、合规风险等级评估（高/中/低）"
"2. 薄弱环节分析：该员工在哪些合规领域存在知识盲区"
"3. 复训建议：针对薄弱领域给出具体培训建议，标注紧急程度（urgent/normal）"
```

### 5.4 Agent 意图识别 Prompt（agentPrompts.py）

**改**：意图类型不变（generate_question / judge_answer / explain / chat / recommend / progress），但识别的上下文关键词变了

```python
# 识别关键词对照
原： "出一道题" "讲一下这道题" "帮我判卷" "推荐练习"
新： "出一道合规题" "解释一下反洗钱条例" "帮我评卷" "推荐复训内容"
```

---

## 六、配置清单

### 6.1 .env 新增配置

```
# CompFox 模块
COMPFOX_DB_NAME=compfox_db

# 或者在现有的基础上直接用 Education 的配置
# 建议单独建库 compfox_db，跟教育数据隔离
```

### 6.2 参数表初始化数据

| 参数 code | 参数值 |
|:---|:---|
| `compfox_subject` | aml (反洗钱), data_security (数据安全), insider_trading (内幕交易), market_manipulation (市场操纵), investor_protection (投资者保护), compliance_management (合规管理), code_of_conduct (行为准则) |
| `compfox_question_type` | single_choice, multiple_choice, judgement, fill_blank, short_answer, essay |
| `compfox_difficulty_label` | basic, intermediate, advanced |
| `compfox_knowledge_point` | aml_ued (客户尽职调查), aml_str (可疑交易报告), aml_sanctions (制裁合规), ds_classification (数据分级), ds_encryption (加密要求), it_insider (内幕信息界定), it_tipping (泄密防范)... |

---

## 七、可扩展能力（MVP 后考虑）

### 7.1 案例库检索

基于 Milvus 向量检索 + Neo4j 知识图谱，支持：

- **输入**："客户频繁大额转账到境外账户"
- **输出**：相似案例 + 监管处罚依据 + 合规处置建议

### 7.2 动态合规监测

定时任务 + LLM，自动跟踪监管法规更新，把新规转为考题：

```
cron: 每月1号
1. LLM 读取最新监管发文
2. 自动生成 3-5 道新规相关考题
3. 推送到题库
```

### 7.3 培训进度仪表盘

前端聚合：整体培训完成率、各部门对比、风险等级分布、复训率

### 7.4 多租户

金融行业不同客户（工行/招行/平安）需要数据隔离。基于 `ConnectionManager` 实现多数据源路由：

```
每个租户一个独立 MySQL 数据库
通过 token 中的 tenant_id 路由到对应数据库
```

---

## 八、开发步骤

```
Phase 1 - 骨架搭建（1天）
  ├── 复制 Education 目录为 CompFox
  ├── 改 main.py（端口 8003 + 路由前缀 compfox）
  ├── 改所有 PO 模型表名（questions → compfox_questions）
  └── 初始化 MySQL 数据库 + 参数表数据

Phase 2 - Prompt 改写（2天）
  ├── questionPrompts.py（出题 + 阅卷 + 导入）
  ├── examPrompts.py（总结 + 舞弊检测）
  └── agentPrompts.py（6 意图 + 识别）

Phase 3 - Service 调整（1天）
  ├── QuestionService.get_knowledge_points() 参数调整
  ├── ExamService 增加合格判定
  └── UserProfileService 增加风险等级

Phase 4 - API + 前端文案（0.5天）
  ├── 改所有 api 的 prefix 和 tag
  └── 改前端 HTML 文案

Phase 5 - 验证（0.5天）
  ├── 导入测试（所有模块可导入）
  ├── 路由注册验证（所有 API 可访问）
  ├── AI 出题测试（验证 Prompt 效果）
  └── AI 阅卷测试（验证合规评判质量）
```

---

## 九、与教育版共存方案

原有教育版 (`:8002`) 和新合规版 (`:8003`) 可以**完全共存**，共享同一套 `Base/` 基础设施：

```
同一个 fastapi 进程：不可以（因为 Education 和 CompFox 是不同的 FastAPI app）
同一个服务器 + 不同端口：可以
同一个 MySQL：可以（不同 database 或不同表前缀）
同一个 Redis/Milvus/Neo4j：可以
同一个 .env：可以（共用数据库配置）
```

如果想合并在一个进程，也可以改 `Base/main.py` 同时注册两套路由：

```python
# Base/main.py
from Education.api.router import router_register as edu_router
from CompFox.api.router import router_register as compfox_router

app = FastAPI()
edu_router(app)       # /education/* 
compfox_router(app)   # /compfox/*
```
