 Education Exam 模块开发计划

 背景

 用户计划开发 Education 模块的完整功能，包括：
 1. 试卷表实体类设计 - 支持手动指定题目 ID 或随机出题
 2. 简易前端 - 根据试卷表 ID 渲染题目，学生输入名字即可答题
 3. 考试表设计 - 用于提交试卷答案，支持固定逻辑判卷和 AI 判卷

 ---
 已确认的需求细节

 1. 试卷表设计

 ┌───────────┬─────────────────────────────────────────────────────────────────────────────────────┐
 │  需求点   │                                      确认方案                                       │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 出题方式  │ 手动指定题目 ID（逗号分隔，有序）或 随机规则出题                                    │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 分值设置  │ 支持手动指定（逗号分隔，与题目对应），提供默认分值逻辑（每题 1 分），需保持可扩展性 │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 总分字段  │ 不需要，根据每题分值计算                                                            │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 版本控制  │ 需要，通过 parent_id 绑定初始试卷，按 created_at 排序查看修改记录                   │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 审核流程  │ 保留字段，暂不实现逻辑                                                              │
 ├───────────┼─────────────────────────────────────────────────────────────────────────────────────┤
 │ 公开/私有 │ 保留字段，暂不实现逻辑                                                              │
 └───────────┴─────────────────────────────────────────────────────────────────────────────────────┘

 2. 前端设计

 ┌──────────┬───────────────────────────────────────────────────────────────────────────────────────────┐
 │  需求点  │                                         确认方案                                          │
 ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ 用户角色 │ 仅需学生视图                                                                              │
 ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ 认证方式 │ 简化处理，学生输入名字即可                                                                │
 ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ 技术栈   │ 纯 HTML + 原生 JS（参考 doQuestion.html）                                                 │
 ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ 功能页面 │ 1. 试卷详情页（答题界面）2. 考试结果页（成绩 + AI 总结）3. 历史答题查询页（输入名字查询） │
 └──────────┴───────────────────────────────────────────────────────────────────────────────────────────┘

 3. 考试表设计

 ┌──────────┬──────────────────────────────────────────────────┐
 │  需求点  │                     确认方案                     │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 限时功能 │ 需要，默认 30 分钟，前端实现倒计时和超时自动交卷 │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 多次考试 │ 仅限一次                                         │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 交卷方式 │ 手动交卷 + 前端超时自动交卷                      │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 判卷方式 │ 固定逻辑判客观题，AI 判主观题，整卷统一 AI 总结  │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 人工复核 │ 保留字段（教师复核意见），暂不实现逻辑           │
 ├──────────┼──────────────────────────────────────────────────┤
 │ 记录信息 │ 仅记录 IP 地址                                   │
 └──────────┴──────────────────────────────────────────────────┘

 4. AI 判卷设计

 ┌──────────┬──────────────────────────────────────────┐
 │  需求点  │                 确认方案                 │
 ├──────────┼──────────────────────────────────────────┤
 │ 判卷范围 │ 整张试卷统一判卷，遍历每题逐一判题       │
 ├──────────┼──────────────────────────────────────────┤
 │ 持久化   │ 每道题的 AI 评判得分依据需持久化         │
 ├──────────┼──────────────────────────────────────────┤
 │ AI 总结  │ 包含：考试成绩总结、知识点梳理、学习建议 │
 └──────────┴──────────────────────────────────────────┘

 5. 代码复用

 ┌─────────────┬──────────────────────────────────┐
 │   需求点    │             确认方案             │
 ├─────────────┼──────────────────────────────────┤
 │ AnswerPo 表 │ 尽量复用或扩展                   │
 ├─────────────┼──────────────────────────────────┤
 │ AI 判题接口 │ 保持逐一判题，最后持久化判题记录 │
 └─────────────┴──────────────────────────────────┘

 6. 数据库规范

 ┌────────────┬──────────────────────────────────────────────────┐
 │   需求点   │                     确认方案                     │
 ├────────────┼──────────────────────────────────────────────────┤
 │ 数据库连接 │ 与本模块其他 models 类保持一致（默认数据库连接） │
 ├────────────┼──────────────────────────────────────────────────┤
 │ 表名前缀   │ 与本模块其他 models 类保持一致（无特殊前缀）     │
 └────────────┴──────────────────────────────────────────────────┘

 ---
 最终技术方案

 1. 数据库表设计

 1.1 试卷表 (papers)

 CREATE TABLE `papers` (
     `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '试卷 ID',
     `paper_uuid` VARCHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '试卷 UUID',
     `parent_id` BIGINT UNSIGNED COMMENT '父版本 ID（用于版本控制）',

     -- 试卷基本信息
     `paper_name` VARCHAR(200) NOT NULL COMMENT '试卷名称',
     `description` TEXT COMMENT '试卷描述',
     `subject` VARCHAR(50) COMMENT '科目',

     -- 题目配置
     `question_ids` VARCHAR(500) NOT NULL COMMENT '题目 ID 列表（逗号分隔，有序）',
     `scores` VARCHAR(500) COMMENT '每题分值（逗号分隔，为空则使用默认分值）',
     `default_score_type` VARCHAR(50) DEFAULT 'uniform_1' COMMENT '默认分值类型：uniform_1=每题 1 分',

     -- 考试配置
     `duration_minutes` INT DEFAULT 30 COMMENT '考试时长（分钟）',

     -- 状态管理
     `status` VARCHAR(20) DEFAULT 'draft' COMMENT '状态：draft|published|archived',
     `is_public` TINYINT DEFAULT 1 COMMENT '是否公开：0-私有，1-公开',

     -- 审计字段
     `created_by` BIGINT UNSIGNED NOT NULL COMMENT '创建者 ID',
     `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

     PRIMARY KEY (`id`),
     KEY `idx_paper_uuid` (`paper_uuid`),
     KEY `idx_parent_id` (`parent_id`),
     KEY `idx_subject` (`subject`),
     KEY `idx_status` (`status`),
     KEY `idx_created_at` (`created_at`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷表';

 1.2 考试记录表 (exams)

 CREATE TABLE `exams` (
     `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '考试记录 ID',
     `exam_uuid` VARCHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '考试 UUID',

     -- 关联信息
     `paper_id` BIGINT UNSIGNED NOT NULL COMMENT '试卷 ID',
     `user_id` VARCHAR(100) NOT NULL COMMENT '考生姓名/ID',

     -- 考试过程
     `start_time` DATETIME COMMENT '开始答题时间',
     `end_time` DATETIME COMMENT '交卷时间',
     `user_ip` VARCHAR(45) COMMENT '用户 IP 地址',

     -- 答案信息
     # 答案存储方案：使用 JSON 格式存储每题答案，避免逗号冲突问题
     # 格式示例：{"1":"A", "2":"A,C", "3":"北京", "4":"简述..."}
     # key: question_id (字符串), value: 用户答案 (字符串)
     `answers` JSON COMMENT '用户答案（JSON 格式，key 为题目 ID，value 为用户答案）',

     -- 成绩信息
     `total_score` DECIMAL(5,2) COMMENT '总分',
     `score_details` JSON COMMENT '得分详情（JSON 格式，每题得分）',

     -- AI 评判
     `ai_summary` TEXT COMMENT 'AI 考试总结（含学习建议）',
     `ai_scoring_basis` TEXT COMMENT 'AI 打分依据',
     `teacher_review` TEXT COMMENT '教师复核意见（保留字段）',

     -- 状态
     `status` VARCHAR(20) DEFAULT 'ongoing' COMMENT '状态：ongoing|submitted|graded',
     `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

     PRIMARY KEY (`id`),
     KEY `idx_exam_uuid` (`exam_uuid`),
     KEY `idx_paper_id` (`paper_id`),
     KEY `idx_user_id` (`user_id`),
     KEY `idx_status` (`status`),
     UNIQUE KEY `uk_paper_user` (`paper_id`, `user_id`) COMMENT '限制每人每卷只能考一次'
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试记录表';

 2. 实体类设计

 2.1 PaperPo - 试卷实体类

 位置：Education/models/pojo/paperPo.py

 class PaperPo(DefaultDbModel):
     table_alias: ClassVar[str] = 'papers'
     # 字段：
     # id, paper_uuid, parent_id
     # paper_name, description, subject
     # question_ids (str: "1,2,3"), scores (str: "2,3,2")
     # default_score_type (str: "uniform_1")
     # duration_minutes, status, is_public
     # created_by, created_at

 2.2 ExamPo - 考试记录实体类

 位置：Education/models/pojo/examPo.py

 class ExamPo(DefaultDbModel):
     table_alias: ClassVar[str] = 'exams'
     # 字段：
     # id, exam_uuid, paper_id, user_id
     # start_time, end_time, user_ip
     # answers (JSON), total_score, score_details (JSON)
     # ai_summary, ai_scoring_basis, teacher_review
     # status, created_at

 3. Service 层设计

 3.1 PaperService - 试卷服务

 位置：Education/services/paperService.py

 class PaperService:
     # 创建试卷（支持手动选题和随机选题）
     def create_paper(self, paper_name, question_ids, scores=None, ...)

     # 计算总分
     def calculate_total_score(self, question_ids, scores)

     # 获取试卷详情（含题目信息）
     def get_paper_detail(paper_id)

     # 获取试卷版本历史
     def get_paper_versions(parent_id)

 3.2 ExamService - 考试服务

 位置：Education/services/examService.py

 class ExamService:
     # 开始考试
     def start_exam(paper_id, user_id, user_ip)

     # 提交试卷
     def submit_exam(exam_id, user_answers)

     # 判卷（固定逻辑 + AI）
     def grade_exam(exam_id)

     # 获取考试结果
     def get_exam_result(exam_id)

     # 查询用户历史考试
     def get_user_history(user_id)

 4. API 接口设计

 位置：Education/api/core/paperApi.py 和 Education/api/core/examApi.py

 # 试卷接口
 GET    /education/paper/{paper_id}          - 获取试卷详情（学生答题用）
 POST   /education/paper                     - 创建试卷
 GET    /education/paper/{paper_id}/versions - 获取版本历史

 # 考试接口
 POST   /education/exam/start                - 开始考试
 POST   /education/exam/{exam_id}/submit     - 提交试卷
 GET    /education/exam/{exam_id}/result     - 获取考试结果
 GET    /education/exam/history              - 查询历史答题

 5. 前端页面

 位置：Education/frontend/

 ┌────────┬──────────────────┬────────────────────────────────────────┐
 │  页面  │       文件       │                  功能                  │
 ├────────┼──────────────────┼────────────────────────────────────────┤
 │ 答题页 │ exam.html        │ 根据试卷 ID 渲染题目，倒计时，提交答案 │
 ├────────┼──────────────────┼────────────────────────────────────────┤
 │ 结果页 │ exam_result.html │ 显示成绩、AI 总结、学习建议            │
 ├────────┼──────────────────┼────────────────────────────────────────┤
 │ 历史页 │ history.html     │ 输入名字查询历史答题记录               │
 └────────┴──────────────────┴────────────────────────────────────────┘

 6. Prompt 设计

 位置：Education/prompts/examPrompts.py

 EXAM_AI_SUMMARY_PROMPT = """
 ## 角色
 你是一位专业的教育评估专家。

 ## 任务
 根据学生的考试成绩和答题情况，提供：
 1. 成绩总结：总分、得分率、表现评价
 2. 知识点梳理：本题考查的核心知识点
 3. 学习建议：针对薄弱环节给出具体建议

 ## 输入
 - 试卷名称：{paper_name}
 - 科目：{subject}
 - 总分：{total_score}
 - 学生得分：{user_score}
 - 各题得分详情：{score_details}
 - 题目知识点：{knowledge_points}

 ## 输出
 请以 JSON 格式输出：
 {
     "summary": "成绩总结（100 字以内）",
     "knowledge_points": "知识点梳理（200 字以内）",
     "suggestions": ["建议 1", "建议 2", ...]
 }
 """

 ---
 实施步骤

 - [x] 1. 创建实体类 - PaperPo, ExamPo ✅
 - [x] 2. 创建 Service 层 - PaperService, ExamService ✅
 - [x] 3. 创建 API 接口 - paperApi.py, examApi.py ✅
 - [x] 4. 创建 Prompt - examPrompts.py ✅
 - [x] 5. 创建前端页面 - exam.html, exam_result.html, history.html ✅
 - [x] 6. 注册路由 - 更新 router.py, frontend/register.py ✅
 - [x] 7. 测试验证 - 语法检查通过 ✅

 ---
 ## 完成状态

 所有核心功能已开发完成，详见 `DEVELOPMENT_SUMMARY.md`
