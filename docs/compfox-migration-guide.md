# CompFox 金融合规培训平台 — 平移改造指南

> 基于现有 `ric-train/Education` 模块平移到金融合规行业
> 项目名：CompFox（合规狐）

---

## 一、平移总览

| 原 Education 概念 | 平移后 CompFox 概念 | 改动量 |
|:---|:---|:---:|
| 学生 / 用户 | 员工 / 从业人员 | 极小 |
| 科目（math/chinese/...） | 合规领域（反洗钱/数据安全/内幕交易/...） | 配置 |
| 知识点（函数/冠词/...） | 合规知识点（AML 条例/客户识别/KYC/...） | 配置 |
| 年级（小学/初中/高中） | 职级（初级/中级/高级/管理层） | 配置 |
| 题目 | 合规考题 | 主体复用 |
| 试卷 | 合规考试卷 | 主体复用 |
| 考试 | 合规考核 | 主体复用 |
| AI 阅卷 | AI 评卷（判断+主观题评分） | Prompt 换 |
| 用户画像（学习能力） | 员工画像（合规能力/风险意识） | 逻辑微调 |
| Agent 聊天（学习助手） | 合规助手（法规查询/案例检索） | Prompt 换 |
| 学习推荐 | 针对弱项的复训推荐 | 逻辑复用 |

---

## 二、不改的层（100% 复用，零改动）

### 2.1 Base 层 — 整个不动

| 模块 | 作用 | 操作 |
|:---|:---|:---:|
| `Base/Config/setting.py` | 环境变量配置（MySQL/Redis/Milvus/Neo4j/LLM） | 直接使用 |
| `Base/Config/logConfig.py` | 日志系统 | 直接使用 |
| `Base/Client/*` | MySQL/Redis/Milvus/MinIO/TencentCOS/Neo4j/ASR/TTS | 直接使用 |
| `Base/Ai/llms/*` | DeepSeek / 通义千问 LLM | 直接使用 |
| `Base/Ai/base/*` | LLM 抽象层、Message、Agent、Tool | 直接使用 |
| `Base/Repository/*` | ORM 层、连接管理器、数据源路由 | 直接使用 |
| `Base/Models/*` | 基础模型（Params/User/Token/Session/Conversation） | 直接使用 |
| `Base/Service/*` | Auth/ASR/Email/Keyword/LLM / MemoryV1 | 直接使用 |
| `Base/RicUtils/*` | 工具类（路径/日期/文件/HTTP/Excel/PDF/Redis） | 直接使用 |
| `Base/Api/*` | Auth API / AI Chat API | 直接使用 |

### 2.2 数据模型层 — 只改表名和字段名

PO 模型继承 `DefaultDbModel`，ORM 逻辑不变，只需改 `table_alias` + `create_table_sql`。

### 2.3 API 路由层 — 只改 prefix 和 tag

FastAPI `APIRouter` 结构不变，只改 `prefix=` 和 `tags=` 的标签文案。

---

## 三、要改的层（详细清单）

### 3.1 配置数据（DB 中的参数表）

`BaseParamsModel` 表中的参数数据需要替换：

| 参数 | 原值（教育） | 新值（金融合规） |
|:---|:---|:---|
| `edu_subject` | math, chinese, english, ... | aml（反洗钱）, data_security（数据安全）, insider_trading（内幕交易）, market_manipulation（市场操纵）, investor_protection（投资者保护）, compliance_management（合规管理） |
| `edu_question_type` | single_choice, multiple_choice, judgement, fill_blank, short_answer, essay | 不变（题型通用） |
| `edu_difficulty_label` | easy, medium, hard | 不变，或改为：basic, intermediate, advanced |
| `edu_knowledge_point` | 函数、冠词、时态... | 按合规领域拆：AML_UED, AML_CDD, AML_STR, DS_Classification, DS_Encryption... |

> **注意**：`KnowledgeService.get_knowledge_points()` 中用 `grade_subject` 做 code，金融场景应改为 `level_field`（如 `intermediate_aml`）。

### 3.2 Prompt 层 — 核心改动

| 文件 | 改动内容 |
|:---|:---|
| `Education/prompts/questionPrompts.py` | 出题 Prompt 中 "科目/年级" → "合规领域/职级"；示例题目从数学题改为合规案例题 |
| `Education/prompts/examPrompts.py` | 阅卷 Prompt 中 "学生/学习建议" → "员工/合规改进建议"；总结 Prompt 语气从"鼓励学习"改为"风险提示+改进方向" |
| `Education/prompts/agentPrompts.py` | Agent 意图识别 + 6 个处理器 Prompt 全部改行业语境 |
| `Education/prompts/common.py` | 通用 Prompt 模板（如有行业相关占位符） |

#### 改动示例：出题 Prompt

```python
# 原（教育）
SM_QUESTION_GENERATE_PROMPT = """
## 背景
你是一个题目生成器，你需要根据用户的要求以 JSON 形式生成一道题目。

## 输出格式
- subject: 科目（{{subject}}）
- grade: 年级（1-12）
- knowledge_points: 知识点
"""

# 改后（合规）
SM_QUESTION_GENERATE_PROMPT = """
## 背景
你是一个金融合规考题生成器，你需要根据合规考核要求以 JSON 形式生成一道考题。

## 输出格式
- subject: 合规领域（{{subject}}）
- grade: 职级（1=初级, 2=中级, 3=高级, 4=管理层）
- knowledge_points: 合规知识点
"""
```

#### 改动示例：阅卷 Prompt

```python
# 原（教育）
EXAM_AI_JUDGE_PROMPT = """
## 角色
你是一位公正严谨的阅卷老师，需要根据题目要求和参考答案评判学生的答案。
"""

# 改后（合规）
EXAM_AI_JUDGE_PROMPT = """
## 角色
你是一位严格的金融合规评审专家，需要根据监管法规要求和标准答案评判从业人员的答案。
对于合规风险判断类题目，特别关注答案中是否遗漏关键风险点。
"""
```

#### 改动示例：考试总结 Prompt

```python
# 原（教育）
EXAM_AI_SUMMARY_PROMPT = """
## 任务
1. 成绩总结：总分、得分率、表现评价（鼓励性语言）
2. 知识点梳理：本题考查的核心知识点，学生掌握情况分析
3. 学习建议：针对薄弱环节给出 2-3 条具体可执行的建议
"""

# 改后（合规）
EXAM_AI_SUMMARY_PROMPT = """
## 任务
1. 成绩总结：总分、合格/不合格判定、合规风险等级评估
2. 薄弱环节分析：识别该员工在哪些合规领域存在知识盲区或风险认知不足
3. 复训建议：针对薄弱领域给出 2-3 条具体的培训建议，并标注风险等级（高/中/低）
"""
```

### 3.3 Service 层 — 少量逻辑调整

#### QuestionService

| 方法 | 改动 |
|:---|:---|
| `get_subjects()` | 不改（仍然是读参数表，数据变了就行） |
| `get_knowledge_points(grade, subject)` | 参数名从 `grade` 改为 `level`，内部 code 格式从 `grade_subject` 改为 `level_subject` |
| `random_generate_question()` | 改一个字典映射：`difficulty_label` 的 easy/medium/hard 如果是合规场景改成 basic/intermediate/advanced（可选） |
| `judge_question()` | 调用 LLM 的 Prompt 变了，方法签名不用改 |

> 纯加分项：在 `judge_question` 中增加 **合规评分规则**，比如"漏掉一个关键风险点扣 50% 分"这种，可以在 Prompt 里描述，不需要改代码。

#### ExamService

| 方法 | 改动 |
|:---|:---|
| `start_exam()` | 不改 |
| `submit_exam()` | 不改 |
| `grade_exam()` | 调用 LLM 的 Prompt 变了，方法不动 |
| `get_exam_result()` | 不改 |
| `get_user_history()` | 不改 |
| `judge_single_question()` | 调用 LLM 的 Prompt 变了 |

> 可加：`pass_exam()` 方法，判断是否达到合格线（金融合规有合格/不合格一说，不像教育有分数段）

#### UserProfileService

| 方法 | 改动 |
|:---|:---|
| `get_profile()` | 不改 |
| `update_profile_from_practice()` | 不改 |
| `get_learning_report()` | 改内部调用 `generate_ai_summary()` 的 Prompt 为合规语境 |
| `get_recommendations()` | 不改（推荐逻辑通用） |

> 可加：`get_compliance_risk_level()` 方法，根据画像评估员工合规风险等级

#### AgentChatService

这个改动稍大，因为 6 个意图处理器都跟行业强相关：

| 意图 | 原行为 | 新行为 |
|:---|:---|:---|
| `generate_question` | 出学科题 | 出合规案例题（基于真实监管案例） |
| `judge_answer` | 判学科答案 | 判合规答案 + 风险点标注 |
| `explain_question` | 讲解解题思路 | 解释法规条款 + 合规要点 |
| `chat` | 通用学习聊天 | 合规知识问答 + 法规检索 |
| `recommend_questions` | 推荐学科练习 | 推荐合规复训题目 |
| `learning_progress` | 查询学习进度 | 查询合规培训进度 + 合规积分 |

### 3.4 前端层 — 纯文案

| 文件 | 改动 |
|:---|:---|
| `Education/frontend/doQuestion.html` | 标题/标签文案："练习"→"合规考核" |
| `Education/frontend/exam_result.html` | "学习建议"→"合规改进建议" |
| `Education/frontend/history.html` | "学习记录"→"培训记录" |
| `Education/frontend/userProfile.html` | "学习画像"→"合规能力画像" |
| 其他 HTML | 同理，换标签名 |

---

## 四、可新增的功能（加分项，非必须）

### 4.1 合格/不合格判定

金融合规考试通常有合格线（如 80 分），低于合格线需要复训。可以加：

```python
# ExamService 新增
@staticmethod
def check_pass(exam_id: int, pass_rate: float = 0.8) -> dict:
    exam = ExamPo.get_by_id(exam_id)
    if not exam:
        raise ValueError(f"考试记录不存在：{exam_id}")
    
    passed = (exam.total_score / exam.max_score) >= pass_rate
    return {
        'exam_id': exam.id,
        'passed': passed,
        'score_rate': exam.total_score / exam.max_score,
        'pass_rate': pass_rate,
        'need_retrain': not passed,
        'retrain_suggestions': [] if passed else ["请复训后重新参加考试"]
    }
```

### 4.2 合规风险等级画像

```python
# UserProfileService 新增
def get_compliance_risk_level(self, user_id: str) -> str:
    """
    评估员工合规风险等级
    返回：low / medium / high
    """
    profile = UserProfilePo.get_or_create(user_id)
    correct_rate = profile.overall_correct_rate
    
    if correct_rate >= 0.9:
        return 'low'
    elif correct_rate >= 0.7:
        return 'medium'
    else:
        return 'high'
```

### 4.3 案例库检索

利用已有的 Milvus 向量检索，加一个合规案例库，支持"输入场景描述→匹配相似案例→给出判罚依据"：

```python
# 新增 CompFox/services/caseRetrievalService.py
# 复用 Base/Client/milvusClient.py
# 复用 Base/Ai/llms/qwenLlm.py 的 embedding 能力
```

---

## 五、不改的部分

| 内容 | 原因 |
|:---|:---|
| `Education/api/core/*Api.py` 的所有路由注册代码 | API 路由结构通用，只改里面调用的 Service（但 Service 签名没变） |
| `Education/api/router.py` | 路由注册逻辑通用 |
| `Education/main.py` | 启动逻辑通用 |
| `.env` 配置项 | MySQL/Redis/LLM 等基础设施配置不变 |
| Dockerfile / docker-compose | 部署方式不变 |
| `Base/` 所有代码 | 完全不解耦，是整个项目的地基 |

---

## 六、改造步骤建议（按顺序）

```
Step 1: 复制 Education → CompFox （目录复制）
Step 2: 改 .env 添加 COMPFOX_ 前缀的配置（如 COMPFOX_DB_NAME）
Step 3: 改 CompFox/models/pojo/*.py 的表名和字段注释（不改字段逻辑）
Step 4: 初始化 DB 参数表数据（合规领域/职级/合规知识点）
Step 5: 改 CompFox/prompts/*.py（核心，投入最多时间）
Step 6: 改 CompFox/services/*Service.py（对照上面的改动清单）
Step 7: 改 CompFox/api/*Api.py 中的 prefix 和 tag
Step 8: 改 CompFox/frontend/*.html 的文案
Step 9: 编译测试，一条条调通
```

---

## 七、Prompts 改写对照表（金融合规术语映射）

| 教育术语 | 合规术语 |
|:---|:---|
| 学生 / 同学 | 员工 / 从业人员 |
| 老师 / 阅卷 | 评审专家 / 合规官 |
| 学习 / 练习 | 培训 / 考核 |
| 知识点 | 合规知识点 / 监管要求 |
| 解题思路 | 合规分析思路 |
| 得分率 | 合规掌握率 |
| 薄弱环节 | 风险盲区 |
| 学习建议 | 复训建议 / 整改建议 |
| 鼓励性语言 | 风险提示 + 改进方向 |
| 进阶学习 | 高级合规培训 |
| 科目 | 合规领域 |
| 年级 | 职级 |
| 考试 | 合规考核 |
| 成绩单 | 合规评估报告 |
| 掌握情况分析 | 合规能力评估 |
| 学习报告 | 合规培训报告 |
