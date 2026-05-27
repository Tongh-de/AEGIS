import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

from Base.Ai.base import SystemMessages, UserMessages
from Base.Ai.llms.qwenLlm import get_default_qwen_llm
from Education.prompts.examPrompts import EXAM_AI_SUMMARY_PROMPT, EXAM_AI_JUDGE_PROMPT
from Education.models.pojo.paperPo import PaperPo
from Education.models.pojo.examPo import ExamPo
from Education.models.pojo.questionPo import QuestionPo
from Education.models.pojo.answerPo import AnswerPo
from Education.services.questionService import get_question_service

logger = logging.getLogger(__name__)


class ExamService(BaseModel):
    """
    考试服务类
    """

    @staticmethod
    def start_exam(paper_id: int, user_id: str, user_ip: Optional[str] = None) -> dict:
        """
        开始考试

        Args:
            paper_id: 试卷 ID
            user_id: 用户 ID
            user_ip: 用户 IP 地址

        Returns:
            包含考试信息的字典

        Raises:
            ValueError: 如果试卷不存在或用户已参加过考试
        """
        # 检查试卷是否存在
        paper = PaperPo.get_by_id(paper_id)
        if not paper:
            raise ValueError(f"试卷不存在：{paper_id}")

        # 检查用户是否已经参加过考试
        if ExamPo.check_user_exam_exists(paper_id, user_id):
            raise ValueError(f"用户已参加过该试卷的考试，不能重复参加")

        # 创建考试记录
        exam = ExamPo(
            paper_id=paper_id,
            user_id=user_id,
            start_time=datetime.now(),
            user_ip=user_ip,
            status='ongoing'
        )
        exam.save()

        return {
            'exam_id': exam.id,
            'exam_uuid': exam.exam_uuid,
            'paper_name': paper.paper_name,
            'duration_minutes': paper.duration_minutes,
            'question_ids': paper.get_question_id_list,
            'start_time': exam.start_time.isoformat() if exam.start_time else None
        }

    @staticmethod
    def submit_exam(exam_id: int, user_answers: Dict[str, str]) -> dict:
        """
        提交试卷

        Args:
            exam_id: 考试记录 ID
            user_answers: 用户答案字典 {question_id: answer}

        Returns:
            判卷结果
        """
        # 获取考试记录
        exam = ExamPo.get_by_id(exam_id)
        if not exam:
            raise ValueError(f"考试记录不存在：{exam_id}")

        if exam.status != 'ongoing':
            raise ValueError(f"考试状态不正确：{exam.status}")

        # 更新考试记录
        exam.answers = user_answers
        exam.end_time = datetime.now()
        exam.status = 'submitted'
        exam.save()

        # 开始判卷
        return ExamService.grade_exam(exam_id)

    @staticmethod
    def grade_exam(exam_id: int) -> dict:
        """
        判卷（固定逻辑 + AI）

        Args:
            exam_id: 考试记录 ID

        Returns:
            判卷结果
        """
        # 获取考试记录
        exam = ExamPo.get_by_id(exam_id)
        if not exam:
            raise ValueError(f"考试记录不存在：{exam_id}")

        # 获取试卷信息
        paper = PaperPo.get_by_id(exam.paper_id)
        if not paper:
            raise ValueError(f"试卷不存在：{exam.paper_id}")

        question_ids = paper.get_question_id_list
        user_answers = exam.get_answers_dict

        # 存储每题的判卷结果
        score_details = {}
        answer_records = []  # 存储答题记录用于 AI 总结

        total_score = 0
        max_score = paper.total_score

        # 遍历每题进行判卷
        for idx, q_id in enumerate(question_ids):
            question = QuestionPo.get_by_id(q_id)
            if not question:
                logger.warning(f"题目不存在：{q_id}")
                continue

            user_answer = user_answers.get(str(q_id), '')
            expected_score = paper.get_score_for_question(idx)

            # 判卷
            judge_result = ExamService.judge_single_question(
                question=question,
                user_answer=user_answer,
                expected_score=expected_score
            )

            # 记录得分
            score_details[str(q_id)] = {
                'score': judge_result['score'],
                'max_score': expected_score,
                'result': judge_result['result'],
                'ai_result': judge_result.get('ai_result', '')
            }

            total_score += judge_result['score']

            # 创建答题记录
            answer_record = AnswerPo(
                question_id=q_id,
                user_id=exam.user_id,
                user_answer=user_answer,
                score=judge_result['score'] / expected_score if expected_score > 0 else 0,
                ai_model=judge_result.get('ai_model'),
                ai_prompt=judge_result.get('ai_prompt'),
                ai_result=judge_result.get('ai_result', ''),
                source='exam',
                connection_id=str(exam_id)
            )
            answer_record.save()
            answer_records.append(answer_record)

        # 生成 AI 总结
        ai_summary_result = ExamService.generate_ai_summary(
            paper=paper,
            total_score=total_score,
            max_score=max_score,
            score_details=score_details,
            answer_records=answer_records
        )

        # 更新考试记录
        exam.total_score = total_score
        exam.score_details = score_details
        exam.ai_summary = json.dumps(ai_summary_result, ensure_ascii=False) if ai_summary_result else None
        exam.ai_scoring_basis = json.dumps(score_details, ensure_ascii=False)
        exam.status = 'graded'
        exam.save()

        return {
            'exam_id': exam_id,
            'total_score': total_score,
            'max_score': max_score,
            'score_rate': total_score / max_score if max_score > 0 else 0,
            'score_details': score_details,
            'ai_summary': ai_summary_result
        }

    @staticmethod
    def judge_single_question(question: QuestionPo, user_answer: str, expected_score: float) -> dict:
        """
        判单道题

        Args:
            question: 题目对象
            user_answer: 用户答案
            expected_score: 期望得分（满分）

        Returns:
            判卷结果
        """
        question_type = question.question_type

        # 客观题使用固定逻辑判卷
        if question_type in ['single_choice', 'multiple_choice', 'judgement']:
            from Education.models.pojo.questionBo import AiJudgeQuestionBo
            params = AiJudgeQuestionBo(
                question_id=question.id,
                answer=user_answer
            )
            judge_result = get_question_service().judge_question(params)
            score = judge_result['score'] * expected_score
            return {
                'score': score,
                'result': judge_result['ai_result'],
                'ai_model': None,
                'ai_prompt': None,
                'ai_result': judge_result['ai_result']
            }
        else:
            # 主观题使用 AI 判卷
            from Education.models.pojo.questionBo import AiJudgeQuestionBo
            params = AiJudgeQuestionBo(
                question_id=question.id,
                answer=user_answer,
                source='exam',
                user_id='exam_grading'
            )
            judge_result = get_question_service().ai_judge_question(params)
            score = judge_result['score'] * expected_score
            return {
                'score': score,
                'result': judge_result['ai_result'],
                'ai_model': 'qwen',
                'ai_prompt': None,
                'ai_result': judge_result['ai_result']
            }

    @staticmethod
    def generate_ai_summary(
            paper: PaperPo,
            total_score: float,
            max_score: float,
            score_details: dict,
            answer_records: List[AnswerPo]
    ) -> dict:
        """
        生成 AI 考试总结

        Args:
            paper: 试卷对象
            total_score: 总分
            max_score: 满分
            score_details: 得分详情
            answer_records: 答题记录列表

        Returns:
            AI 总结结果
        """
        try:
            # 收集知识点
            knowledge_points = []
            for record in answer_records:
                question = QuestionPo.get_by_id(record.question_id)
                if question and question.knowledge_points:
                    knowledge_points.extend(question.knowledge_points.split(','))

            knowledge_points_str = ','.join(list(set(knowledge_points)))

            # 构建 prompt
            user_prompt = f"""
试卷名称：{paper.paper_name}
科目：{paper.subject or '未知'}
总分：{total_score:.2f}
满分：{max_score:.2f}
得分率：{(total_score / max_score * 100) if max_score > 0 else 0:.1f}%

得分详情：{json.dumps(score_details, ensure_ascii=False)}
知识点：{knowledge_points_str}

请根据以上信息生成考试总结。
"""

            llm = get_default_qwen_llm()
            messages = [
                SystemMessages(prompt=EXAM_AI_SUMMARY_PROMPT),
                UserMessages(prompt=user_prompt)
            ]
            response = llm.chat(messages)

            # 解析 JSON 响应
            try:
                result = json.loads(response)
                return {
                    'summary': result.get('summary', ''),
                    'knowledge_points': result.get('knowledge_points', ''),
                    'suggestions': result.get('suggestions', [])
                }
            except json.JSONDecodeError:
                logger.warning(f"AI 总结 JSON 解析失败，使用默认响应：{response}")
                return {
                    'summary': response[:500],
                    'knowledge_points': '',
                    'suggestions': []
                }

        except Exception as e:
            logger.error(f"生成 AI 总结失败：{str(e)}")
            return {
                'summary': f'考试得分：{total_score:.2f}/{max_score:.2f}',
                'knowledge_points': '',
                'suggestions': []
            }

    @staticmethod
    def get_exam_result(exam_id: int) -> dict:
        """
        获取考试结果

        Args:
            exam_id: 考试记录 ID

        Returns:
            考试结果信息
        """
        exam = ExamPo.get_by_id(exam_id)
        if not exam:
            raise ValueError(f"考试记录不存在：{exam_id}")

        paper = PaperPo.get_by_id(exam.paper_id)

        return {
            'exam_uuid': exam.exam_uuid,
            'paper_name': paper.paper_name if paper else '未知试卷',
            'subject': paper.subject if paper else '未知',
            'user_id': exam.user_id,
            'start_time': exam.start_time.isoformat() if exam.start_time else None,
            'end_time': exam.end_time.isoformat() if exam.end_time else None,
            'total_score': exam.total_score,
            'max_score': paper.total_score if paper else 0,
            'score_rate': (exam.total_score / paper.total_score) if paper and paper.total_score > 0 else 0,
            'ai_summary': json.loads(exam.ai_summary) if exam.ai_summary else None,
            'score_details': exam.get_score_details_dict,
            'status': exam.status
        }

    @staticmethod
    def get_exam_result_detail(exam_id: int) -> dict:
        """
        获取考试结果详情（包含每题的详细内容）

        Args:
            exam_id: 考试记录 ID

        Returns:
            考试结果详情信息
        """
        exam = ExamPo.get_by_id(exam_id)
        if not exam:
            raise ValueError(f"考试记录不存在：{exam_id}")

        paper = PaperPo.get_by_id(exam.paper_id)
        if not paper:
            raise ValueError(f"试卷不存在：{exam.paper_id}")

        # 获取答题记录
        answer_records = AnswerPo.get_by_source_and_connection_id('exam', str(exam_id))

        # 获取试卷的题目 ID 列表和分值列表
        question_id_list = paper.get_question_id_list
        score_list = paper.get_score_list

        # 构建每题的详细信息
        question_details = {}
        for record in answer_records:
            question = QuestionPo.get_by_id(record.question_id)
            if not question:
                continue

            # 解析 AI 结果
            ai_result = {}
            if record.ai_result:
                try:
                    ai_result = json.loads(record.ai_result)
                except (json.JSONDecodeError, Exception):
                    ai_result = {'comment': record.ai_result}

            # 获取题目索引和分值
            try:
                q_id = int(record.question_id) if isinstance(record.question_id, str) else record.question_id
                if q_id in question_id_list:
                    question_index = question_id_list.index(q_id)
                    max_score = score_list[question_index] if question_index < len(score_list) else 1.0
                else:
                    max_score = 1.0
            except (ValueError, IndexError):
                max_score = 1.0

            question_details[str(record.question_id)] = {
                'question_id': record.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'user_answer': record.user_answer,
                'score': record.score * max_score,
                'max_score': max_score,
                'ai_model': record.ai_model,
                'ai_comment': ai_result.get('comment', ''),
                'ai_analysis': ai_result.get('analysis', '')
            }

        return {
            'exam_uuid': exam.exam_uuid,
            'paper_name': paper.paper_name if paper else '未知试卷',
            'subject': paper.subject if paper else '未知',
            'user_id': exam.user_id,
            'total_score': exam.total_score,
            'max_score': paper.total_score if paper else 0,
            'score_rate': (exam.total_score / paper.total_score) if paper and paper.total_score > 0 else 0,
            'question_details': question_details,
            'status': exam.status
        }

    @staticmethod
    def get_user_history(user_id: str, limit: int = 10) -> list:
        """
        获取用户考试历史

        Args:
            user_id: 用户 ID
            limit: 返回数量限制

        Returns:
            考试历史列表
        """
        exams = ExamPo.get_by_user_id(user_id, limit)
        result = []

        for exam in exams:
            paper = PaperPo.get_by_id(exam.paper_id)
            result.append({
                'exam_uuid': exam.exam_uuid,
                'paper_name': paper.paper_name if paper else '未知试卷',
                'subject': paper.subject if paper else '未知',
                'total_score': exam.total_score,
                'max_score': paper.total_score if paper else 0,
                'status': exam.status,
                'created_at': exam.created_at.isoformat() if exam.created_at else None
            })

        return result


def get_exam_service():
    """获取 ExamService 单例"""
    return ExamService()


if __name__ == '__main__':
    # 测试
    service = ExamService()
    print("ExamService 初始化成功")
