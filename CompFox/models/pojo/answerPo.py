from datetime import datetime
from typing import Optional, ClassVar, Literal
import json
from pydantic import field_serializer
from Base.Repository.models.defaultDbModel import DefaultDbModel


class AnswerPo(DefaultDbModel):
    """
    员工答题记录模型
    """
    table_alias: ClassVar[str] = "compfox_answers"
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_alias}` (
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            `question_id` VARCHAR(50) NOT NULL COMMENT '题目ID',
            `user_id` VARCHAR(50) COMMENT '用户ID',
            `user_answer` TEXT COMMENT '用户答案',
            `score` DECIMAL(3,2) DEFAULT 0 COMMENT '得分率：0-1，1表示做对，0表示做错',
            `ai_model` VARCHAR(50) COMMENT 'AI判题模型，为空表示人工审核或固定逻辑审核',
            `ai_prompt` TEXT COMMENT 'AI判题提示词',
            `ai_result` TEXT COMMENT 'AI判题结果(JSON格式)',
            `source` VARCHAR(50) NOT NULL COMMENT '来源：daily_question|exam|homework|practice',
            `connection_id` VARCHAR(50) COMMENT '关联ID，对应来源的具体ID（如考试ID）',
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

            PRIMARY KEY (`id`),
            KEY `idx_question_id` (`question_id`),
            KEY `idx_user_id` (`user_id`),
            KEY `idx_source` (`source`),
            KEY `idx_connection_id` (`connection_id`),
            KEY `idx_created_at` (`created_at`),
            KEY `idx_user_source` (`user_id`, `source`),
            KEY `idx_source_connection` (`source`, `connection_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='答题记录表';
    """

    # 字段定义
    id: Optional[int] = None
    question_id: Optional[str | int] = None
    user_id: Optional[str | int] = None
    user_answer: Optional[str] = None
    score: Optional[float] = None
    ai_model: Optional[str] = None
    ai_prompt: Optional[str] = None
    ai_result: Optional[str] = None
    source: Optional[str] = None
    connection_id: Optional[str | int] = None
    created_at: datetime = None


    @classmethod
    def get_by_source_and_connection_id(cls, source: str, connection_id: str) -> list:
        """
        根据来源和关联 ID 查询答题记录

        Args:
            source: 来源（exam、practice 等）
            connection_id: 关联 ID（如考试 ID）

        Returns:
            答题记录列表
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return []

            table_name = cls.get_table_name()
            sql = f"SELECT * FROM `{table_name}` WHERE `source` = %s AND `connection_id` = %s"
            results = db.execute(sql, (source, connection_id))

            if not results:
                return []

            return [cls(**row) for row in results]
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_by_source_and_connection_id(source={source}, connection_id={connection_id}) 失败：{str(e)}")
            return []


if __name__ == '__main__':
    po = AnswerPo()
    po.create_table()
