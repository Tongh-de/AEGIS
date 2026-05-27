from datetime import datetime
from typing import Optional, ClassVar
import json
from pydantic import Field, field_serializer, field_validator
from Base.Repository.models.defaultDbModel import DefaultDbModel


class ExamPo(DefaultDbModel):
    """
    考试记录表实体类
    """
    table_alias: ClassVar[str] = 'exams'
    create_table_sql = f"""
        -- 考试记录表
        CREATE TABLE IF NOT EXISTS `{table_alias}` (
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
        """

    # 字段定义
    id: Optional[int] = Field(None, description="考试记录 ID")
    exam_uuid: Optional[str] = Field(None, description="考试 UUID")

    # 关联信息
    paper_id: int = Field(..., description="试卷 ID")
    user_id: str = Field(..., description="考生姓名/ID")

    # 考试过程
    start_time: Optional[datetime] = Field(None, description="开始答题时间")
    end_time: Optional[datetime] = Field(None, description="交卷时间")
    user_ip: Optional[str] = Field(None, description="用户 IP 地址")

    # 答案信息
    answers: Optional[dict] = Field(None, description="用户答案（JSON 格式）")

    # 成绩信息
    total_score: Optional[float] = Field(None, description="总分")
    score_details: Optional[dict] = Field(None, description="得分详情（JSON 格式）")

    # AI 评判
    ai_summary: Optional[str] = Field(None, description="AI 考试总结")
    ai_scoring_basis: Optional[str] = Field(None, description="AI 打分依据")
    teacher_review: Optional[str] = Field(None, description="教师复核意见")

    # 状态
    status: str = Field('ongoing', description="状态：ongoing|submitted|graded")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    # JSON 字段验证器 - 从数据库读取时解析 JSON 字符串
    @field_validator('answers', 'score_details', mode='before')
    @classmethod
    def parse_json_fields(cls, value):
        """从数据库读取时，如果字段是 JSON 字符串则解析为 dict"""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, Exception):
                return None
        return value

    # JSON 字段序列化器
    @field_serializer('answers', 'score_details')
    def serialize_json_fields(self, value, _info):
        """将 dict 类型的字段序列化为 JSON 字符串"""
        if value is None:
            return None
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return value

    @property
    def get_answers_dict(self) -> dict:
        """获取答案字典"""
        if not self.answers:
            return {}
        if isinstance(self.answers, str):
            try:
                return json.loads(self.answers)
            except (json.JSONDecodeError, Exception):
                return {}
        return self.answers

    @property
    def get_score_details_dict(self) -> dict:
        """获取得分详情字典"""
        if not self.score_details:
            return {}
        if isinstance(self.score_details, str):
            try:
                return json.loads(self.score_details)
            except (json.JSONDecodeError, Exception):
                return {}
        return self.score_details

    @classmethod
    def get_by_uuid(cls, exam_uuid: str) -> Optional['ExamPo']:
        """
        根据 UUID 查询考试记录

        Args:
            exam_uuid: 考试 UUID

        Returns:
            考试记录对象，未找到返回 None
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return None

            table_name = cls.get_table_name()
            sql = f"SELECT * FROM `{table_name}` WHERE `exam_uuid` = %s LIMIT 1"
            result = db.execute(sql, (exam_uuid,))

            if not result:
                return None

            return cls(**result[0])
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_by_uuid({exam_uuid}) 失败：{str(e)}")
            return None

    @classmethod
    def check_user_exam_exists(cls, paper_id: int, user_id: str) -> bool:
        """
        检查用户是否已经参加过某个试卷的考试

        Args:
            paper_id: 试卷 ID
            user_id: 用户 ID

        Returns:
            True 表示已参加过，False 表示未参加过
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return False

            table_name = cls.get_table_name()
            sql = f"SELECT COUNT(*) as cnt FROM `{table_name}` WHERE `paper_id` = %s AND `user_id` = %s"
            result = db.execute(sql, (paper_id, user_id))

            if result and result[0].get('cnt', 0) > 0:
                return True
            return False
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"check_user_exam_exists(paper_id={paper_id}, user_id={user_id}) 失败：{str(e)}")
            return False

    @classmethod
    def get_by_user_id(cls, user_id: str, limit: int = 10) -> list:
        """
        根据用户 ID 查询考试历史

        Args:
            user_id: 用户 ID
            limit: 返回数量限制

        Returns:
            考试记录列表
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return []

            table_name = cls.get_table_name()
            sql = f"""
                SELECT * FROM `{table_name}`
                WHERE `user_id` = %s
                ORDER BY `created_at` DESC
                LIMIT %s
            """
            results = db.execute(sql, (user_id, limit))

            if not results:
                return []

            return [cls(**row) for row in results]
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_by_user_id({user_id}) 失败：{str(e)}")
            return []


if __name__ == '__main__':
    po = ExamPo()
    po.create_table()
    print("考试记录表创建成功")
