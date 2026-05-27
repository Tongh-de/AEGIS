import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel

from CompFox.models.pojo.userProfilePo import UserProfilePo
from CompFox.models.pojo.answerPo import AnswerPo
from CompFox.models.pojo.questionPo import QuestionPo
from CompFox.services.questionService import get_question_service

logger = logging.getLogger(__name__)


class UserProfileService(BaseModel):
    """
    用户画像服务
    负责用户画像的自动更新、分析、总结生成
    """

    def get_profile(self, user_id: str) -> UserProfilePo:
        """
        获取用户画像

        Args:
            user_id: 用户 ID

        Returns:
            用户画像对象
        """
        return UserProfilePo.get_or_create(user_id)

    def update_profile_from_practice(self, user_id: str, answer_id: int = None,
                                     question_id: str = None, is_correct: bool = None):
        """
        根据答题记录更新用户画像

        Args:
            user_id: 用户 ID
            answer_id: 答题记录 ID（如果传入则从数据库获取答题信息）
            question_id: 题目 ID（与 answer_id 二选一）
            is_correct: 是否正确（与 answer_id 二选一）
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)

            # 如果传入 answer_id，从数据库获取答题信息
            if answer_id:
                answer = AnswerPo.get_by_id(answer_id)
                if not answer:
                    logger.warning(f"答题记录不存在：answer_id={answer_id}")
                    return

                question_id = answer.question_id
                is_correct = (answer.score or 0) >= 0.8

            # 获取题目信息
            if question_id:
                question = QuestionPo.get_by_id(question_id)
                if question:
                    # 解析知识点
                    knowledge_points = []
                    if question.knowledge_points:
                        knowledge_points = [kp.strip() for kp in question.knowledge_points.split(',')]

                    # 更新画像
                    profile.update_practice_stats(
                        subject=question.subject,
                        is_correct=is_correct,
                        knowledge_points=knowledge_points,
                        score=answer.score if answer_id else None
                    )
                    logger.info(f"用户画像已更新：user_id={user_id}, subject={question.subject}")
                else:
                    logger.warning(f"题目不存在：question_id={question_id}")
            else:
                logger.warning("未提供题目 ID")

        except Exception as e:
            logger.error(f"更新用户画像失败：{str(e)}")

    def update_profile_from_chat(self, user_id: str, intent: str, question: str = None):
        """
        根据聊天记录更新用户画像

        Args:
            user_id: 用户 ID
            intent: 意图类型
            question: 用户问题
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)
            profile.update_chat_profile(intent=intent, question=question)
            logger.info(f"用户聊天画像已更新：user_id={user_id}, intent={intent}")
        except Exception as e:
            logger.error(f"更新聊天画像失败：{str(e)}")

    def refresh_ai_summary(self, user_id: str) -> str:
        """
        刷新 AI 画像总结

        Args:
            user_id: 用户 ID

        Returns:
            AI 生成的画像总结
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)
            summary = profile.generate_ai_summary()
            logger.info(f"AI 画像总结已生成：user_id={user_id}")
            return summary
        except Exception as e:
            logger.error(f"生成 AI 画像总结失败：{str(e)}")
            return f"生成画像总结失败：{str(e)}"

    def get_learning_report(self, user_id: str, time_range: str = '本周') -> Dict:
        """
        生成培训报告

        Args:
            user_id: 用户 ID
            time_range: 时间范围（今天 | 本周 | 本月 | 全部）

        Returns:
            培训报告字典
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)

            # 计算时间范围
            now = datetime.now()
            if time_range == '今天':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == '本周':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == '本月':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = None

            # 查询答题记录
            if start_date:
                answers = AnswerPo.find_by(
                    user_id=str(user_id),
                    condition="created_at >= %s",
                    params=(start_date,),
                    limit=1000
                )
            else:
                answers = AnswerPo.find_by(user_id=str(user_id), limit=1000)

            # 统计答题情况
            total = len(answers)
            correct = sum(1 for a in answers if (a.score or 0) >= 0.8)
            correct_rate = correct / total if total > 0 else 0

            # 按合规领域统计
            subject_stats = {}
            for answer in answers:
                question = QuestionPo.get_by_id(answer.question_id)
                if question:
                    subject = question.subject
                    if subject not in subject_stats:
                        subject_stats[subject] = {'total': 0, 'correct': 0}
                    subject_stats[subject]['total'] += 1
                    if (answer.score or 0) >= 0.8:
                        subject_stats[subject]['correct'] += 1

            # 计算各科正确率
            for subject in subject_stats:
                stats = subject_stats[subject]
                stats['correct_rate'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0

            # 计算连续培训天数
            continuous_days = self._calculate_continuous_days(user_id)

            return {
                'user_id': user_id,
                'time_range': time_range,
                'total_questions': total,
                'correct_count': correct,
                'correct_rate': round(correct_rate, 2),
                'subject_stats': subject_stats,
                'continuous_days': continuous_days,
                'profile': profile.mini_dict
            }

        except Exception as e:
            logger.error(f"生成培训报告失败：{str(e)}")
            return {'error': str(e)}

    def _calculate_continuous_days(self, user_id: str) -> int:
        """
        计算连续培训天数

        Args:
            user_id: 用户 ID

        Returns:
            连续培训天数
        """
        try:
            # 查询用户所有答题记录的日期
            answers = AnswerPo.find_by(user_id=str(user_id), order_by="created_at", order="DESC", limit=365)
            if not answers:
                return 0

            # 去重获取日期列表
            dates = set()
            for answer in answers:
                date_str = answer.created_at.strftime('%Y-%m-%d')
                dates.add(date_str)

            if not dates:
                return 0

            # 转换为日期对象并排序
            date_list = sorted([datetime.strptime(d, '%Y-%m-%d').date() for d in dates], reverse=True)

            # 计算连续天数
            today = datetime.now().date()
            continuous = 0

            for i, date in enumerate(date_list):
                if i == 0:
                    # 检查是否有今天的记录
                    if date == today:
                        continuous = 1
                    elif date == today - timedelta(days=1):
                        continuous = 1
                    else:
                        return 0
                else:
                    # 检查是否连续
                    if date_list[i - 1] - date == timedelta(days=1):
                        continuous += 1
                    else:
                        break

            return continuous

        except Exception as e:
            logger.error(f"计算连续培训天数失败：{str(e)}")
            return 0

    def get_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        获取个性化推荐

        Args:
            user_id: 用户 ID
            limit: 推荐数量

        Returns:
            推荐题目列表
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)
            weak_points = profile.weak_points_list

            recommendations = []

            # 根据薄弱知识点推荐题目
            if weak_points:
                for weak_point in weak_points[:3]:  # 最多取 3 个薄弱点
                    # 查询相关题目
                    questions = QuestionPo.get_random_question(
                        subject=self._guess_subject_from_kp(weak_point),
                        num=2
                    )
                    if questions:
                        if not isinstance(questions, list):
                            questions = [questions]
                        for q in questions:
                            recommendations.append({
                                'question_id': q.id,
                                'question_text': q.question_text[:100],
                                'knowledge_points': q.knowledge_points,
                                'difficulty_level': q.difficulty_level,
                                'recommend_reason': f'薄弱点强化：{weak_point}'
                            })

            # 如果推荐不足，随机补充
            while len(recommendations) < limit:
                questions = QuestionPo.get_random_question(num=limit - len(recommendations))
                if questions:
                    if not isinstance(questions, list):
                        questions = [questions]
                    for q in questions:
                        recommendations.append({
                            'question_id': q.id,
                            'question_text': q.question_text[:100],
                            'knowledge_points': q.knowledge_points,
                            'difficulty_level': q.difficulty_level,
                            'recommend_reason': '综合练习'
                        })
                else:
                    break

            return recommendations[:limit]

        except Exception as e:
            logger.error(f"生成推荐失败：{str(e)}")
            return []

    def _guess_subject_from_kp(self, knowledge_point: str) -> Optional[str]:
        """
        根据知识点猜测合规领域

        Args:
            knowledge_point: 知识点名称

        Returns:
            合规领域代码
        """
        kp_lower = knowledge_point.lower()

        # 数学相关
        math_keywords = ['函数', '几何', '代数', '方程', '数列', '概率', '统计', '三角', '微积分']
        for kw in math_keywords:
            if kw in kp_lower:
                return 'math'

        # 英语相关
        english_keywords = ['语法', '时态', '从句', '单词', '阅读', '写作', '听力']
        for kw in english_keywords:
            if kw in kp_lower:
                return 'english'

        # 语文相关
        chinese_keywords = ['古诗', '文言文', '修辞', '作文', '阅读', '拼音', '汉字']
        for kw in chinese_keywords:
            if kw in kp_lower:
                return 'chinese'

        # 物理相关
        physics_keywords = ['力学', '电学', '光学', '热学', '磁场', '电路']
        for kw in physics_keywords:
            if kw in kp_lower:
                return 'physics'

        # 化学相关
        chemistry_keywords = ['化学式', '反应', '元素', '溶液', '酸碱', '氧化']
        for kw in chemistry_keywords:
            if kw in kp_lower:
                return 'chemistry'

        return None

    def analyze_user_behavior(self, user_id: str) -> Dict:
        """
        分析用户行为特征

        Args:
            user_id: 用户 ID

        Returns:
            行为分析结果
        """
        try:
            profile = UserProfilePo.get_or_create(user_id)

            # 获取答题记录
            answers = AnswerPo.find_by(user_id=str(user_id), order_by="created_at", order="DESC", limit=100)

            if not answers:
                return {'error': '无答题记录'}

            # 分析答题时间偏好
            hour_distribution = {}
            for answer in answers:
                hour = answer.created_at.hour
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1

            # 找出活跃时段
            peak_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3]

            # 分析练习频率
            dates = set(a.created_at.strftime('%Y-%m-%d') for a in answers)
            practice_days = len(dates)

            # 判断练习频率类型
            if practice_days >= 20:
                frequency = 'daily'
            elif practice_days >= 7:
                frequency = 'weekly'
            else:
                frequency = 'irregular'

            # 分析偏好题型
            question_type_stats = {}
            for answer in answers:
                question = QuestionPo.get_by_id(answer.question_id)
                if question:
                    q_type = question.question_type
                    question_type_stats[q_type] = question_type_stats.get(q_type, 0) + 1

            preferred_type = max(question_type_stats.items(), key=lambda x: x[1])[0] if question_type_stats else None

            # 分析平均答题时长（如果有数据）
            response_times = []
            for answer in answers:
                if answer.ai_result:
                    # 尝试从 AI 结果中提取答题时长（如果有）
                    pass

            return {
                'user_id': user_id,
                'practice_frequency': frequency,
                'practice_days': practice_days,
                'peak_hours': peak_hours,
                'preferred_question_type': preferred_type,
                'total_practice_count': len(answers),
                'learning_style': self._infer_learning_style(answers, profile)
            }

        except Exception as e:
            logger.error(f"分析用户行为失败：{str(e)}")
            return {'error': str(e)}

    def _infer_learning_style(self, answers: List[AnswerPo], profile: UserProfilePo) -> str:
        """
        推断培训风格

        培训风格分类：
        - visual: 视觉型（偏好图表、公式）
        - auditory: 听觉型（偏好讲解、音频）
        - reading: 阅读型（偏好文字、阅读）
        - kinesthetic: 实践型（偏好练习、实操）

        Args:
            answers: 答题记录列表
            profile: 用户画像

        Returns:
            培训风格
        """
        # 根据练习频率和正确率推断
        total = len(answers)
        if total == 0:
            return 'unknown'

        correct_rate = sum(1 for a in answers if (a.score or 0) >= 0.8) / total

        # 如果练习量大且正确率高，可能是实践型
        if total >= 50 and correct_rate >= 0.8:
            return 'kinesthetic'

        # 如果偏好简答题/论述题，可能是阅读型
        question_types = {}
        for answer in answers:
            question = QuestionPo.get_by_id(answer.question_id)
            if question:
                q_type = question.question_type
                question_types[q_type] = question_types.get(q_type, 0) + 1

        if question_types.get('essay', 0) + question_types.get('short_answer', 0) > total * 0.3:
            return 'reading'

        # 默认返回实践型（大多数用户）
        return 'kinesthetic'


# 全局服务实例
user_profile_service = UserProfileService()


def get_user_profile_service():
    """获取用户画像服务实例"""
    return user_profile_service


if __name__ == '__main__':
    # 测试
    service = get_user_profile_service()

    # 获取用户画像
    profile = service.get_profile('test_user_001')
    print(f"用户画像：{profile.mini_dict}")

    # 生成培训报告
    report = service.get_learning_report('test_user_001', '本周')
    print(f"培训报告：{report}")

    # 获取推荐
    recommendations = service.get_recommendations('test_user_001')
    print(f"推荐题目：{recommendations}")

    # 分析用户行为
    behavior = service.analyze_user_behavior('test_user_001')
    print(f"行为分析：{behavior}")
