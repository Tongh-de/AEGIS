import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from Education.models.pojo.paperPo import PaperPo
from Education.models.pojo.questionPo import QuestionPo

logger = logging.getLogger(__name__)


class PaperService(BaseModel):
    """
    试卷服务类
    """

    @staticmethod
    def create_paper(
        paper_name: str,
        question_ids: List[int],
        scores: Optional[List[float]] = None,
        description: str = None,
        subject: str = None,
        duration_minutes: int = 30,
        default_score_type: str = 'uniform_1',
        created_by: int = None
    ) -> PaperPo:
        """
        创建试卷

        Args:
            paper_name: 试卷名称
            question_ids: 题目 ID 列表
            scores: 每题分值列表（可选，为空则使用默认分值）
            description: 试卷描述
            subject: 科目
            duration_minutes: 考试时长（分钟）
            default_score_type: 默认分值类型
            created_by: 创建者 ID

        Returns:
            创建的试卷对象
        """
        # 验证题目是否存在
        valid_question_ids = []
        for q_id in question_ids:
            question = QuestionPo.get_by_id(q_id)
            if question:
                valid_question_ids.append(q_id)
            else:
                logger.warning(f"题目不存在：{q_id}")

        if not valid_question_ids:
            raise ValueError("没有有效的题目")

        # 转换 ID 列表为逗号分隔字符串
        question_ids_str = ','.join(map(str, valid_question_ids))
        scores_str = ','.join(map(str, scores)) if scores else None

        # 创建试卷
        paper = PaperPo(
            paper_name=paper_name,
            description=description,
            subject=subject,
            question_ids=question_ids_str,
            scores=scores_str,
            default_score_type=default_score_type,
            duration_minutes=duration_minutes,
            created_by=created_by or 505,  # 默认创建者 ID
            status='draft'
        )
        paper.save()

        logger.info(f"试卷创建成功：id={paper.id}, name={paper.paper_name}")
        return paper

    @staticmethod
    def update_paper(
        paper_id: int,
        paper_name: str = None,
        question_ids: List[int] = None,
        scores: List[float] = None,
        description: str = None,
        subject: str = None,
        duration_minutes: int = None,
        updated_by: int = None
    ) -> PaperPo:
        """
        更新试卷（创建新版本）

        Args:
            paper_id: 试卷 ID
            paper_name: 试卷名称
            question_ids: 题目 ID 列表
            scores: 每题分值列表
            description: 试卷描述
            subject: 科目
            duration_minutes: 考试时长
            updated_by: 更新者 ID

        Returns:
            新版本的试卷对象
        """
        # 获取原始试卷
        original_paper = PaperPo.get_by_id(paper_id)
        if not original_paper:
            raise ValueError(f"试卷不存在：{paper_id}")

        # 确定 parent_id（如果是第一版本，parent_id 为原始试卷 ID）
        parent_id = original_paper.parent_id or original_paper.id

        # 创建新版本
        new_paper = PaperPo(
            parent_id=parent_id,
            paper_name=paper_name or original_paper.paper_name,
            description=description if description is not None else original_paper.description,
            subject=subject or original_paper.subject,
            question_ids=','.join(map(str, question_ids)) if question_ids else original_paper.question_ids,
            scores=','.join(map(str, scores)) if scores else original_paper.scores,
            default_score_type=original_paper.default_score_type,
            duration_minutes=duration_minutes or original_paper.duration_minutes,
            created_by=updated_by or original_paper.created_by,
            status='draft'
        )
        new_paper.save()

        logger.info(f"试卷新版本创建成功：id={new_paper.id}, parent_id={parent_id}")
        return new_paper

    @staticmethod
    def get_paper_detail(paper_id: int) -> dict:
        """
        获取试卷详情（含题目信息）

        Args:
            paper_id: 试卷 ID

        Returns:
            试卷详情字典
        """
        paper = PaperPo.get_by_id(paper_id)
        if not paper:
            raise ValueError(f"试卷不存在：{paper_id}")

        # 获取题目列表
        questions = []
        for idx, q_id in enumerate(paper.get_question_id_list):
            question = QuestionPo.get_by_id(q_id)
            if question:
                questions.append({
                    'question_id': q_id,
                    'index': idx + 1,
                    'score': paper.get_score_for_question(idx),
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'knowledge_points': question.knowledge_points
                })

        return {
            'paper_id': paper.id,
            'paper_uuid': paper.paper_uuid,
            'paper_name': paper.paper_name,
            'description': paper.description,
            'subject': paper.subject,
            'duration_minutes': paper.duration_minutes,
            'total_score': paper.total_score,
            'question_count': len(questions),
            'questions': questions,
            'status': paper.status
        }

    @staticmethod
    def get_paper_versions(paper_id: int) -> list:
        """
        获取试卷版本历史

        Args:
            paper_id: 试卷 ID

        Returns:
            版本历史列表
        """
        paper = PaperPo.get_by_id(paper_id)
        if not paper:
            raise ValueError(f"试卷不存在：{paper_id}")

        # 获取 parent_id
        parent_id = paper.parent_id or paper.id

        # 查询所有版本
        versions = PaperPo.get_versions(parent_id)

        result = []
        for idx, version in enumerate(versions):
            result.append({
                'version': idx + 1,
                'id': version.id,
                'paper_uuid': version.paper_uuid,
                'paper_name': version.paper_name,
                'created_at': version.created_at.isoformat() if version.created_at else None,
                'created_by': version.created_by,
                'question_count': len(version.get_question_id_list),
                'total_score': version.total_score
            })

        return result

    @staticmethod
    def delete_paper(paper_id: int) -> bool:
        """
        删除试卷（软删除，将状态设为 archived）

        Args:
            paper_id: 试卷 ID

        Returns:
            是否成功
        """
        paper = PaperPo.get_by_id(paper_id)
        if not paper:
            return False

        paper.status = 'archived'
        paper.save()
        return True

    @staticmethod
    def publish_paper(paper_id: int) -> bool:
        """
        发布试卷

        Args:
            paper_id: 试卷 ID

        Returns:
            是否成功
        """
        paper = PaperPo.get_by_id(paper_id)
        if not paper:
            return False

        paper.status = 'published'
        paper.save()
        return True

    @staticmethod
    def get_paper_list(page: int = 1, page_size: int = 10, subject: str = None, status: str = None) -> dict:
        """
        分页获取试卷列表

        Args:
            page: 页码
            page_size: 每页数量
            subject: 科目筛选
            status: 状态筛选

        Returns:
            分页结果
        """
        result = PaperPo.get_paginated(page=page, page_size=page_size, subject=subject, status=status)

        # 转换为字典列表
        paper_list = []
        for paper in result['list']:
            paper_list.append({
                'id': paper.id,
                'paper_uuid': paper.paper_uuid,
                'paper_name': paper.paper_name,
                'subject': paper.subject,
                'duration_minutes': paper.duration_minutes,
                'question_count': len(paper.get_question_id_list),
                'total_score': paper.total_score,
                'status': paper.status,
                'created_at': paper.created_at.isoformat() if paper.created_at else None,
                'created_by': paper.created_by
            })

        return {
            'list': paper_list,
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size']
        }

    @staticmethod
    def update_paper_questions(paper_id: int, question_ids: List[int], scores: List[float] = None) -> PaperPo:
        """
        更新试卷题目列表

        Args:
            paper_id: 试卷 ID
            question_ids: 题目 ID 列表
            scores: 每题分值列表

        Returns:
            更新后的试卷对象
        """
        return PaperService.update_paper(
            paper_id=paper_id,
            question_ids=question_ids,
            scores=scores
        )

    @staticmethod
    def restore_version(paper_id: int, updated_by: int = None) -> PaperPo:
        """
        恢复历史版本（创建该版本的新副本作为最新版本）

        Args:
            paper_id: 要恢复的版本 ID
            updated_by: 更新者 ID

        Returns:
            新创建的试卷对象

        Raises:
            ValueError: 当试卷不存在时
        """
        # 获取要恢复的版本
        source_paper = PaperPo.get_by_id(paper_id)
        if not source_paper:
            raise ValueError(f"试卷不存在：{paper_id}")

        # 获取该试卷的 parent_id（版本根 ID）
        parent_id = source_paper.parent_id or source_paper.id

        # 创建新版本（复制源版本的所有配置）
        new_paper = PaperPo(
            parent_id=parent_id,
            paper_name=source_paper.paper_name,
            description=source_paper.description,
            subject=source_paper.subject,
            question_ids=source_paper.question_ids,
            scores=source_paper.scores,
            default_score_type=source_paper.default_score_type,
            duration_minutes=source_paper.duration_minutes,
            created_by=updated_by or source_paper.created_by,
            status='draft'
        )
        new_paper.save()

        logger.info(f"试卷版本恢复成功：新 id={new_paper.id}, 恢复到版本 id={paper_id}")
        return new_paper


def get_paper_service():
    """获取 PaperService 单例"""
    return PaperService()


if __name__ == '__main__':
    service = PaperService()
    print("PaperService 初始化成功")
