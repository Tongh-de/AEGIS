# 用户画像表设计文档

## 表结构概述

**表名**: `user_profiles`

**用途**: 存储用户的学习画像，包括基础信息、学习统计、能力维度、聊天画像等

## 字段设计

### 1. 核心 ID 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT UNSIGNED | 主键 ID |
| user_id | VARCHAR(50) | 用户 ID（唯一索引） |
| profile_uuid | VARCHAR(36) | 画像 UUID |

### 2. 基础信息

| 字段 | 类型 | 说明 |
|------|------|------|
| nickname | VARCHAR(100) | 用户昵称 |
| avatar_url | VARCHAR(500) | 头像 URL |
| grade_type | VARCHAR(20) | 年级类型（小学/初中/高中） |
| grade_level | TINYINT | 具体年级（1-12） |
| preferred_subject | VARCHAR(200) | 偏好科目（逗号分隔） |

### 3. 学习统计

| 字段 | 类型 | 说明 |
|------|------|------|
| total_questions | INT UNSIGNED | 累计做题数 |
| total_correct | INT UNSIGNED | 累计正确数 |
| overall_correct_rate | DECIMAL(5,4) | 总体正确率（0-1） |
| total_practice_time | INT UNSIGNED | 累计练习时长（分钟） |
| continuous_days | INT UNSIGNED | 连续学习天数 |
| last_practice_date | DATE | 最后练习日期 |

### 4. JSON 字段（核心画像数据）

#### subject_stats - 各科目统计
```json
{
  "math": {
    "count": 100,
    "correct": 85,
    "correct_rate": 0.85,
    "weak_points": ["函数", "几何"]
  },
  "english": {
    "count": 50,
    "correct": 40,
    "correct_rate": 0.8,
    "weak_points": ["从句"]
  }
}
```

#### knowledge_mastery - 知识点掌握情况
```json
{
  "math_函数": {
    "mastery": 0.8,
    "question_count": 20,
    "last_review": "2025-01-01T10:00:00"
  },
  "math_几何": {
    "mastery": 0.6,
    "question_count": 15,
    "last_review": "2025-01-02T10:00:00"
  }
}
```

#### chat_profile - 聊天画像
```json
{
  "total_chats": 100,
  "common_questions": ["出题", "解析", "判题"],
  "interaction_score": 0.8
}
```

#### intent_stats - 意图使用统计
```json
{
  "generate_question": 50,
  "judge_answer": 30,
  "explain_question": 20,
  "chat": 10
}
```

#### ability_dimensions - 能力维度评估
```json
{
  "logical_thinking": 0.7,
  "calculation": 0.8,
  "memory": 0.6,
  "analysis": 0.75,
  "reading_comprehension": 0.65
}
```

#### weak_points - 薄弱知识点
```json
["三角函数", "数列", "定语从句"]
```

#### recommend_pool - 推荐题目池
```json
[
  {
    "question_id": 123,
    "reason": "薄弱点强化",
    "priority": 0.9
  }
]
```

### 5. 学习特征

| 字段 | 类型 | 说明 |
|------|------|------|
| learning_style | VARCHAR(50) | 学习风格（visual/auditory/reading/kinesthetic） |
| practice_frequency | VARCHAR(20) | 练习频率（daily/weekly/irregular） |
| preferred_difficulty | TINYINT | 偏好难度（1-5） |
| average_response_time | INT | 平均答题时长（秒） |

### 6. 学习目标

| 字段 | 类型 | 说明 |
|------|------|------|
| learning_goal | VARCHAR(500) | 学习目标 |
| target_score | DECIMAL(5,4) | 目标正确率 |

### 7. AI 画像总结

| 字段 | 类型 | 说明 |
|------|------|------|
| ai_summary | TEXT | AI 生成的画像总结 |
| ai_model | VARCHAR(50) | AI 模型名称 |
| ai_prompt | TEXT | 生成画像使用的 prompt |

### 8. 画像版本

| 字段 | 类型 | 说明 |
|------|------|------|
| profile_version | INT UNSIGNED | 画像版本号 |
| last_updated_type | VARCHAR(50) | 最后更新类型（chat/practice/manual） |

### 9. 时间戳

| 字段 | 类型 | 说明 |
|------|------|------|
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 索引设计

```sql
PRIMARY KEY (`id`)
UNIQUE KEY `uk_user_id` (`user_id`)
KEY `idx_grade_type` (`grade_type`)
KEY `idx_grade_level` (`grade_level`)
KEY `idx_created_at` (`created_at`)
KEY `idx_updated_at` (`updated_at`)
KEY `idx_last_practice` (`last_practice_date`)
```

## 使用方法

### 1. 创建表
```python
from Education.models.pojo.userProfilePo import UserProfilePo

po = UserProfilePo()
po.create_table()
```

### 2. 获取或创建用户画像
```python
profile = UserProfilePo.get_or_create('user_123')
```

### 3. 更新练习统计
```python
profile.update_practice_stats(
    subject='math',
    is_correct=True,
    knowledge_points=['函数', '一次函数'],
    score=0.8
)
```

### 4. 更新聊天画像
```python
profile.update_chat_profile(
    intent='generate_question',
    question='帮我出一道数学题'
)
```

### 5. 生成 AI 画像总结
```python
ai_summary = profile.generate_ai_summary()
```

## API 接口

### 获取用户画像
```
GET /edu/user/profile?user_id=xxx
```

### 获取画像详情
```
GET /edu/user/profile/detail?user_id=xxx
```

### 获取学习报告
```
GET /edu/user/profile/report?user_id=xxx&time_range=本周
```

### 获取推荐题目
```
GET /edu/user/profile/recommendations?user_id=xxx&limit=5
```

### 获取用户行为分析
```
GET /edu/user/profile/analysis?user_id=xxx
```

### 刷新 AI 画像总结
```
POST /edu/user/profile/refresh-summary?user_id=xxx
```

### 更新用户画像（练习）
```
POST /edu/user/profile/update/practice?user_id=xxx&answer_id=123
```

### 更新用户画像（聊天）
```
POST /edu/user/profile/update/chat?user_id=xxx&intent=generate_question&question=xxx
```

## 画像更新机制

### 自动更新时机

1. **练习后更新**
   - 用户完成答题后调用 `update_profile_from_practice`
   - 更新科目统计、知识点掌握、薄弱点等

2. **聊天后更新**
   - 用户与 Agent 聊天后调用 `update_profile_from_chat`
   - 更新聊天画像、意图统计等

3. **定期更新**
   - 连续学习天数每日更新
   - AI 画像总结定期刷新

### 薄弱点识别算法

```python
# 知识点掌握度 < 0.6 识别为薄弱点
if mastery_score < 0.6:
    add_to_weak_points(knowledge_point)
```

### 能力维度推断

根据用户的：
- 答题正确率 → 推断计算能力、逻辑思维
- 题目类型偏好 → 推断阅读理解能力
- 答题时长 → 推断反应速度

## 数据来源

| 数据维度 | 数据来源 |
|----------|----------|
| 学习统计 | answers 答题记录表 |
| 科目统计 | answers + questions 表关联 |
| 知识点掌握 | questions.knowledge_points + answers.score |
| 聊天画像 | base_llm_conversation 对话记录表 |
| 意图统计 | base_llm_conversation.ai_agent 或独立记录 |

## 扩展建议

1. **增加用户等级系统**
   - 根据学习时长和正确率计算用户等级
   - 设置勋章/成就系统

2. **增加学习路径规划**
   - 根据薄弱点生成学习计划
   - 推荐学习资源

3. **增加社交功能**
   - 学习排行榜
   - 学习小组/PK

4. **增加可视化报告**
   - 生成周报/月报
   - 图表展示学习趋势
