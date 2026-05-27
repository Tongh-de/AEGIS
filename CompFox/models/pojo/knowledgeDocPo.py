from datetime import datetime
from typing import Optional, ClassVar, List
from pydantic import Field
from Base.Repository.models.defaultDbModel import DefaultDbModel


class KnowledgeDocPo(DefaultDbModel):
    """合规知识文档元数据表（MySQL）"""
    table_alias: ClassVar[str] = 'compfox_knowledge_document'
    create_table_sql = f"""
        -- 知识库文档元数据表
        CREATE TABLE IF NOT EXISTS `{table_alias}` (
            `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            `doc_id`          VARCHAR(64) NOT NULL COMMENT '文档UUID',
            `doc_name`        VARCHAR(256) NOT NULL COMMENT '文档名称',
            `source_type`     VARCHAR(32) NOT NULL COMMENT '来源类型：pdf|docx|txt|excel|url|raw_text',
            `source_url`      VARCHAR(1024) COMMENT '原始来源URL',
            `total_chunks`    INT UNSIGNED DEFAULT 0 COMMENT '分块总数',
            `total_chars`     INT UNSIGNED DEFAULT 0 COMMENT '总字符数',
            `tags`            VARCHAR(1024) COMMENT '标签（逗号分隔）',
            `effective_date`  VARCHAR(32) COMMENT '生效日期',
            `version`         VARCHAR(32) COMMENT '版本号',
            `status`          TINYINT UNSIGNED DEFAULT 1 COMMENT '状态：0-禁用 1-正常',

            `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_doc_id` (`doc_id`),
            KEY `idx_source_type` (`source_type`),
            KEY `idx_status` (`status`),
            KEY `idx_created_at` (`created_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='合规知识文档元数据表';
    """

    id: Optional[int] = Field(None, description="主键ID")
    doc_id: str = Field(..., description="文档UUID")
    doc_name: str = Field(..., description="文档名称")
    source_type: str = Field(..., description="来源类型")
    source_url: Optional[str] = Field(None, description="原始来源URL")
    total_chunks: Optional[int] = Field(0, description="分块总数")
    total_chars: Optional[int] = Field(0, description="总字符数")
    tags: Optional[str] = Field(None, description="标签")
    effective_date: Optional[str] = Field(None, description="生效日期")
    version: Optional[str] = Field(None, description="版本号")
    status: Optional[int] = Field(1, description="状态")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @classmethod
    def get_by_doc_id(cls, doc_id: str) -> Optional['KnowledgeDocPo']:
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return None
            table = cls.get_table_name()
            result = db.execute(f"SELECT * FROM `{table}` WHERE `doc_id` = %s AND `status` = 1 LIMIT 1", (doc_id,))
            return cls(**result[0]) if result else None
        except Exception:
            return None

    @classmethod
    def list_active(cls) -> List['KnowledgeDocPo']:
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return []
            table = cls.get_table_name()
            result = db.execute(f"SELECT * FROM `{table}` WHERE `status` = 1 ORDER BY `created_at` DESC")
            return [cls(**row) for row in result] if result else []
        except Exception:
            return []

    @classmethod
    def soft_delete(cls, doc_id: str) -> bool:
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return False
            table = cls.get_table_name()
            db.execute(f"UPDATE `{table}` SET `status` = 0 WHERE `doc_id` = %s", (doc_id,))
            return True
        except Exception:
            return False
