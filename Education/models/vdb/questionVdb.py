import logging
from typing import Optional, List, ClassVar

from pydantic import Field

from Base.Ai.llms.qwenLlm import get_default_qwen_llm
from Base.Repository.base.baseVDB import BaseVDBModel
from Education.models.pojo.questionPo import QuestionPo

logger = logging.getLogger(__name__)


class QuestionVdb(BaseVDBModel):
    """
    题目向量数据库模型
    只保留主要字段，所有字段类型为 varchar 默认
    """
    collection_alias: ClassVar[str] = "question"
    description: ClassVar[str] = "题目表"

    # 主键 ID（自增）
    id: Optional[int] = Field(
        default=0,
        json_schema_extra={
            'is_primary': True,
            'auto_id': True
        }
    )

    # 核心 ID
    question_uuid: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 36
        }
    )

    # 题目内容
    question_text: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 65535,
            'enable_match': True,
            'enable_analyzer': True
        }
    )

    # 答案与解析
    answer: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 65535
        }
    )

    analysis: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 65535
        }
    )

    knowledge_points: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 500
        }
    )

    # 题目元数据
    grade: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 10
        }
    )

    subject: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 20
        }
    )

    question_type: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 20
        }
    )

    # 难度与评分
    difficulty_level: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 10
        }
    )

    difficulty_label: Optional[str] = Field(
        default='',
        json_schema_extra={
            'max_length': 10
        }
    )

    # 语义向量（用于相似度搜索）
    embedding: Optional[List[float]] = Field(
        default_factory=list,
        json_schema_extra={
            'dim': 1024
        }
    )

    # 稀疏向量（基于 question_text 的 BM25）
    content_sparse: Optional[List[float]] = Field(
        default_factory=list,
        json_schema_extra={
            'is_sparse_vector': True,
            'bm25_source_field': 'question_text'
        }
    )

    @classmethod
    def sync_all_from_db(cls, batch_size: int = 100) -> dict:
        """
        全量同步：从 MySQL 数据库导入所有题目到向量数据库

        Args:
            batch_size: 批量插入大小，默认 100

        Returns:
            dict: 同步结果统计
        """
        logger.info("开始全量同步题目到向量数据库...")

        # 1. 确保 VDB 集合已创建
        cls._check_and_create_collection()

        # 2. 查询 DB 中所有题目
        all_questions = QuestionPo.get_all()
        total_count = len(all_questions)

        if total_count == 0:
            logger.info("MySQL 中没有题目数据")
            return {'inserted': 0, 'total': 0}

        logger.info(f"从 MySQL 中读取到 {total_count} 道题目")

        # 3. 获取 embedding 模型
        llm = get_default_qwen_llm()

        # 4. 批量转换并插入
        inserted_count = 0
        failed_count = 0
        batch_data = []

        for i, question in enumerate(all_questions):
            try:
                # 将所有非 varchar 字段转换为 varchar（字符串）
                vdb_instance = cls(
                    question_uuid=str(question.question_uuid) if question.question_uuid else '',
                    question_text=str(question.question_text) if question.question_text else '',
                    answer=str(question.answer) if question.answer is not None else '',
                    analysis=str(question.analysis) if question.analysis is not None else '',
                    knowledge_points=str(question.knowledge_points) if question.knowledge_points is not None else '',
                    # 数值类型转字符串
                    grade=str(question.grade) if question.grade is not None else '',
                    subject=str(question.subject) if question.subject else '',
                    question_type=str(question.question_type) if question.question_type else '',
                    difficulty_level=str(question.difficulty_level) if question.difficulty_level is not None else '',
                    difficulty_label=str(question.difficulty_label) if question.difficulty_label is not None else '',
                )

                # 生成 embedding 向量
                if question.question_text:
                    embedding = llm.embedding(text=question.question_text, dimensions=1024)
                    vdb_instance.embedding = embedding[0]

                batch_data.append(vdb_instance)

                # 批量插入
                if len(batch_data) >= batch_size:
                    result = cls.batch_insert(batch_data)
                    inserted_count += result.get('insert_count', len(batch_data))
                    logger.info(f"已插入 {inserted_count}/{total_count} 道题目")
                    batch_data = []

            except Exception as e:
                failed_count += 1
                logger.error(f"处理题目 ID={question.id} 失败：{e}")

        # 处理剩余数据
        if batch_data:
            result = cls.batch_insert(batch_data)
            inserted_count += result.get('insert_count', len(batch_data))

        logger.info(f"全量同步完成：成功 {inserted_count} 道，失败 {failed_count} 道")
        return {'inserted': inserted_count, 'failed': failed_count, 'total': total_count}

    @classmethod
    def query_all(cls) -> List['QuestionVdb']:
        """
        查询所有题目

        Returns:
            List[QuestionVdb]: 题目列表
        """
        return cls.find_by(filter="", output_fields=["*"])


if __name__ == '__main__':
    QuestionVdb().sync_all_from_db()