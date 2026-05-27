"""
为用户画像测试造数据：生成答题记录并更新画像
"""
import random
from datetime import datetime, timedelta
from CompFox.models.pojo.questionPo import QuestionPo
from CompFox.models.pojo.answerPo import AnswerPo
from CompFox.services.userProfileService import get_user_profile_service

service = get_user_profile_service()

# 测试用户列表
users = [
    ("zhangsan", "张三", "高级", 3),
    ("lisi", "李四", "中级", 2),
    ("wangwu", "王五", "初级", 1),
    ("test_user_001", "测试员", "高级", 3),
]

# 获取所有题目
all_questions = QuestionPo.get_all(limit=1000)
print(f"题库共 {len(all_questions)} 道题")

# 为每个用户生成答题记录
now = datetime.now()
records_created = 0

for user_id, nickname, grade_type, grade_level in users:
    print(f"\n--- 用户 {nickname} ({user_id}) ---")

    # 更新基础信息
    profile = service.get_profile(user_id)
    profile.nickname = nickname
    profile.grade_type = grade_type
    profile.grade_level = grade_level
    profile.save()

    # 随机选 8-15 道题作为答题记录
    sample_questions = random.sample(all_questions, min(random.randint(8, 15), len(all_questions)))

    for q in sample_questions:
        # 随机生成得分（0-1），偏正态分布
        score = round(random.uniform(0, 1), 2)
        is_correct = score >= 0.6

        # 创建答题记录（过去 14 天内随机时间）
        days_ago = random.randint(0, 14)
        hours_ago = random.randint(0, 23)
        created_at = now - timedelta(days=days_ago, hours=hours_ago)

        answer = AnswerPo(
            user_id=user_id,
            question_id=q.id,
            score=score,
            user_answer=f"用户答案-{random.choice(['A', 'B', 'C', 'D'])}",
            source=random.choice(['daily_question', 'exam', 'homework', 'practice']),
            created_at=created_at,
        )
        answer.save()

        # 根据答题记录更新画像
        knowledge_points = []
        if q.knowledge_points:
            knowledge_points = [kp.strip() for kp in q.knowledge_points.split(',')]

        profile.update_practice_stats(
            subject=q.subject,
            is_correct=is_correct,
            knowledge_points=knowledge_points,
            score=score,
        )
        records_created += 1

    # 生成常见聊天意图
    for intent, question in [
        ("generate_question", f"帮我出一道{random.choice(['反洗钱','数据安全','内控'])}题"),
        ("judge_answer", "这道题我选A对吗"),
        ("explain_question", "帮我解析一下这个知识点"),
        ("recommend_questions", "推荐一些练习题"),
    ]:
        profile.update_chat_profile(intent=intent, question=question)

    print(f"  答题记录: {len(sample_questions)} 条")
    print(f"  总正确率: {profile.overall_correct_rate:.1%}")
    print(f"  薄弱点: {profile.weak_points_list}")

print(f"\n共生成 {records_created} 条答题记录")
print("数据准备完成，可以启动服务测试 Swagger 了")
