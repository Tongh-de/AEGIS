from datetime import datetime
from decimal import Decimal
from typing import Optional, ClassVar
import json
from pydantic import field_serializer, Field
from Base.Repository.models.defaultDbModel import DefaultDbModel


class QuestionFeatureEngineeringPo(DefaultDbModel):
    """
    题目全维特征工程宽表模型
    用于存储题目的各类统计、干预、图谱、运维特征
    """
    table_alias: ClassVar[str] = "question_feature_engineering"
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_alias}` (
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
            `question_id` VARCHAR(50) NOT NULL COMMENT '题目唯一标识',
            `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '特征计算/更新时间',

            -- ==================== 1. 基础统计与质量特征 ====================
            `total_attempts` BIGINT DEFAULT 0 COMMENT '【基础统计】求值过程：COUNT(*) GROUP BY question_id，统计历史总作答次数',
            `unique_user_count` INT DEFAULT 0 COMMENT '【基础统计】求值过程：COUNT(DISTINCT user_id)，统计独立作答人数',
            `avg_score_rate` DECIMAL(5,4) DEFAULT 0 COMMENT '【基础统计】求值过程：AVG(score)，全局平均得分率（0-1），反映整体难度',
            `score_std_dev` DECIMAL(5,4) DEFAULT 0 COMMENT '【基础统计】求值过程：STDDEV(score)，得分标准差，反映分数的离散程度',
            `error_rate` DECIMAL(5,4) DEFAULT 0 COMMENT '【基础统计】求值过程：SUM(score=0)/COUNT(*)，完全错误的比例',

            -- ==================== 2. 智能干预与画像特征 ====================
            `distractor_power_json` TEXT COMMENT '【智能干预】求值过程：统计各错误选项的选择频率（JSON 格式存储，如{{"B":0.4, "C":0.01}}），用于识别无效干扰项',
            `speed_kill_ratio` DECIMAL(5,4) DEFAULT 0 COMMENT '【智能干预】求值过程：(作答时长<5 秒且 score=0 的记录数) / 总作答数，用于检测题目表述不清或数据错误',
            `difficulty_drift` DECIMAL(5,4) DEFAULT 0 COMMENT '【智能干预】求值过程：实际平均得分率 - 题目预设难度系数，偏差过大触发难度校准',
            `variant_demand` TINYINT DEFAULT 0 COMMENT '【智能干预】求值过程：若知识点下用户平均练习次数>阈值且正确率提升斜率<0，置 1，表示需要生成变式题',
            `text_perplexity` DECIMAL(10,2) DEFAULT 0 COMMENT '【智能干预】求值过程：使用 NLP 模型计算题干文本的困惑度，值越高代表题目表述越晦涩难懂',
            `circuit_breaker_score` DECIMAL(5,4) DEFAULT 0 COMMENT '【系统熔断】求值过程：加权计算 (秒杀异常指数*0.4 + 难度漂移*0.3 + 投诉率*0.3)，超过阈值触发熔断',

            -- ==================== 3. 知识图谱关联特征 ====================
            `root_cause_depth_avg` DECIMAL(5,4) DEFAULT 0 COMMENT '【图谱归因】求值过程：对错题进行图谱反向遍历，计算追溯到根本薄弱点（掌握度<0.5）的平均路径长度',
            `prereq_missing_count_avg` DECIMAL(5,4) DEFAULT 0 COMMENT '【图谱归因】求值过程：统计错题关联的前置依赖节点中，掌握度低于阈值（如 0.6）的节点平均数量',
            `confusion_conflict_score` DECIMAL(5,4) DEFAULT 0 COMMENT '【图谱归因】求值过程：统计用户在"易混淆"关联节点间反复出错的频率，值越高说明概念辨析越不清',
            `transfer_gain_avg` DECIMAL(5,4) DEFAULT 0 COMMENT '【图谱归因】求值过程：统计掌握前置知识点 A 后，学习平行迁移节点 B 的收敛速度增益',

            -- ==================== 4. 系统运维与健康特征 ====================
            `latency_p99` INT DEFAULT 0 COMMENT '【系统运维】求值过程：统计单位时间窗口内，AI 判题接口返回耗时的 99 分位数值（毫秒）',
            `ai_confidence_avg` DECIMAL(5,4) DEFAULT 0 COMMENT '【系统运维】求值过程：解析 ai_result JSON 字段，提取 confidence 字段并求平均，低分暗示模型识别困难',
            `data_consistency_error_count` BIGINT DEFAULT 0 COMMENT '【系统运维】求值过程：统计 AI 判分逻辑与最终 score 字段冲突的记录数',

            -- ==================== 5. 状态控制 ====================
            `status_level` TINYINT DEFAULT 1 COMMENT '【状态控制】题目当前状态：1-正常，2-L1 观察期，3-L2 干预期，4-L3 熔断期',
            `is_frozen` TINYINT(1) DEFAULT 0 COMMENT '【状态控制】是否被物理熔断：1-是（禁止抽题），0-否',

            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_question_id` (`question_id`),
            KEY `idx_update_time` (`update_time`),
            KEY `idx_circuit_breaker` (`circuit_breaker_score`),
            KEY `idx_status_level` (`status_level`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目全维特征工程宽表';
    """

    # ==================== 核心字段 ====================
    id: Optional[int] = Field(None, description="主键 ID")
    question_id: str = Field(None, description="题目唯一标识")
    update_time: Optional[datetime] = Field(None, description="特征计算/更新时间")

    # ==================== 1. 基础统计与质量特征 ====================
    total_attempts: Optional[int] = Field(None, description="历史总作答次数")
    unique_user_count: Optional[int] = Field(None, description="独立作答人数")
    avg_score_rate: Optional[Decimal] = Field(None, description="全局平均得分率（0-1）")
    score_std_dev: Optional[Decimal] = Field(None, description="得分标准差")
    error_rate: Optional[Decimal] = Field(None, description="完全错误的比例")

    # ==================== 2. 智能干预与画像特征 ====================
    distractor_power_json: Optional[str] = Field(None, description="干扰项强度分析（JSON 格式）")
    speed_kill_ratio: Optional[Decimal] = Field(None, description="秒杀致死率")
    difficulty_drift: Optional[Decimal] = Field(None, description="难度漂移值")
    variant_demand: Optional[int] = Field(None, description="变式题需求标记")
    text_perplexity: Optional[Decimal] = Field(None, description="文本困惑度")
    circuit_breaker_score: Optional[Decimal] = Field(None, description="熔断分数")

    # ==================== 3. 知识图谱关联特征 ====================
    root_cause_depth_avg: Optional[Decimal] = Field(None, description="根本原因深度平均值")
    prereq_missing_count_avg: Optional[Decimal] = Field(None, description="前置缺失节点平均数")
    confusion_conflict_score: Optional[Decimal] = Field(None, description="混淆冲突分数")
    transfer_gain_avg: Optional[Decimal] = Field(None, description="迁移增益平均值")

    # ==================== 4. 系统运维与健康特征 ====================
    latency_p99: Optional[int] = Field(None, description="AI 判题接口 P99 延迟（毫秒）")
    ai_confidence_avg: Optional[Decimal] = Field(None, description="AI 置信度平均值")
    data_consistency_error_count: Optional[int] = Field(None, description="数据一致性错误数")

    # ==================== 5. 状态控制 ====================
    status_level: Optional[int] = Field(None, description="状态等级：1-正常，2-L1 观察期，3-L2 干预期，4-L3 熔断期")
    is_frozen: Optional[int] = Field(None, description="是否熔断：1-是，0-否")

    @staticmethod
    def get_field_mapping() -> dict:
        """
        获取字段名到中文描述的映射

        Returns:
            dict: 字段名到中文描述的映射字典
        """
        field_mapping = {}
        for field_name, field_info in QuestionFeatureEngineeringPo.model_fields.items():
            if hasattr(field_info, 'description') and field_info.description:
                field_mapping[field_name] = field_info.description
        return field_mapping

    # JSON 字段序列化器 - 将 dict/list 转换为 JSON 字符串
    @field_serializer('distractor_power_json')
    def serialize_distractor_power_json(self, value, _info):
        """将 dict 或 list 类型的字段序列化为 JSON 字符串"""
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    @classmethod
    def get_by_question_id(cls, question_id: str) -> Optional['QuestionFeatureEngineeringPo']:
        """
        根据题目 ID 查询特征数据

        Args:
            question_id: 题目 ID

        Returns:
            特征数据对象，未找到返回 None
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return None

            table_name = cls.get_table_name()
            sql = f"SELECT * FROM `{table_name}` WHERE `question_id` = %s LIMIT 1"
            result = db.execute(sql, (question_id,))

            if not result:
                return None

            return cls(**result[0])
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_by_question_id({question_id}) 失败：{str(e)}")
            return None

    @classmethod
    def get_frozen_questions(cls) -> list:
        """
        查询所有被熔断的题目

        Returns:
            被熔断的题目特征列表
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return []

            table_name = cls.get_table_name()
            sql = f"SELECT * FROM `{table_name}` WHERE `is_frozen` = 1"
            results = db.execute(sql)

            if not results:
                return []

            return [cls(**row) for row in results]
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_frozen_questions 失败：{str(e)}")
            return []

    @classmethod
    def get_abnormal_questions(cls, threshold: float = 0.8) -> list:
        """
        查询熔断分数超过阈值的异常题目

        Args:
            threshold: 熔断分数阈值，默认 0.8

        Returns:
            异常题目特征列表
        """
        try:
            cls._ensure_table_exists()
            db = cls.get_db_connection()
            if db is None:
                return []

            table_name = cls.get_table_name()
            sql = f"SELECT * FROM `{table_name}` WHERE `circuit_breaker_score` > %s"
            results = db.execute(sql, (threshold,))

            if not results:
                return []

            return [cls(**row) for row in results]
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"get_abnormal_questions(threshold={threshold}) 失败：{str(e)}")
            return []

    def update_status(self, status_level: int, is_frozen: int = 0) -> bool:
        """
        更新题目状态

        Args:
            status_level: 状态等级（1-4）
            is_frozen: 是否熔断（0 或 1）

        Returns:
            是否更新成功
        """
        try:
            self._ensure_table_exists()
            db = self.get_db_connection()
            if db is None:
                return False

            table_name = self.get_table_name()
            sql = f"UPDATE `{table_name}` SET `status_level` = %s, `is_frozen` = %s WHERE `question_id` = %s"
            affected = db.execute(sql, (status_level, is_frozen, self.question_id))
            return affected > 0
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"update_status 失败：{str(e)}")
            return False

    @property
    def distractor_power(self) -> Optional[dict]:
        """
        解析干扰项强度 JSON

        Returns:
            dict: 干扰项强度数据，如 {"B": 0.4, "C": 0.01}
        """
        if self.distractor_power_json:
            try:
                return json.loads(self.distractor_power_json)
            except json.JSONDecodeError:
                return None
        return None


if __name__ == '__main__':
    from decimal import Decimal
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("=" * 50)
    print("=== 题目特征工程表 - 增删改查测试 ===")
    print("=" * 50)

    # 1. 创建表
    print("\n【1】创建表...")
    po = QuestionFeatureEngineeringPo()
    po.create_table()
    print("✓ 表创建成功")

    # 2. 插入数据（Create）
    print("\n【2】插入测试数据...")
    test_data = QuestionFeatureEngineeringPo(
        question_id="test_uuid_001",
        # 基础统计特征
        total_attempts=1000,
        unique_user_count=850,
        avg_score_rate=Decimal("0.7500"),
        score_std_dev=Decimal("0.2100"),
        error_rate=Decimal("0.1500"),
        # 智能干预特征
        distractor_power_json='{"B": 0.35, "C": 0.08, "D": 0.02}',
        speed_kill_ratio=Decimal("0.0500"),
        difficulty_drift=Decimal("0.1200"),
        variant_demand=0,
        text_perplexity=Decimal("45.60"),
        circuit_breaker_score=Decimal("0.3500"),
        # 知识图谱特征
        root_cause_depth_avg=Decimal("2.3000"),
        prereq_missing_count_avg=Decimal("1.5000"),
        confusion_conflict_score=Decimal("0.4200"),
        transfer_gain_avg=Decimal("0.1800"),
        # 系统运维特征
        latency_p99=1200,
        ai_confidence_avg=Decimal("0.8900"),
        data_consistency_error_count=5,
        # 状态控制
        status_level=1,
        is_frozen=0
    )

    insert_id = test_data.save()
    print(f"✓ 插入成功，ID={insert_id}, question_id={test_data.question_id}")

    # 3. 查询数据（Read）
    print("\n【3】查询测试...")

    # 3.1 根据 ID 查询
    print("  3.1 根据 question_id 查询...")
    result = QuestionFeatureEngineeringPo.get_by_question_id("test_uuid_001")
    if result:
        print(f"  ✓ 查询成功：circuit_breaker_score={result.circuit_breaker_score}, "
              f"status_level={result.status_level}")
        print(f"  ✓ 解析干扰项 JSON: {result.distractor_power}")
    else:
        print("  ✗ 查询失败")

    # 3.2 查询被熔断的题目（应该为空）
    print("  3.2 查询被熔断的题目...")
    frozen_list = QuestionFeatureEngineeringPo.get_frozen_questions()
    print(f"  ✓ 被熔断的题目数量：{len(frozen_list)}")

    # 3.3 查询异常题目（阈值 0.3）
    print("  3.3 查询异常题目（circuit_breaker_score > 0.3）...")
    abnormal_list = QuestionFeatureEngineeringPo.get_abnormal_questions(threshold=0.3)
    print(f"  ✓ 异常题目数量：{len(abnormal_list)}")
    for item in abnormal_list:
        print(f"    - question_id={item.question_id}, circuit_breaker_score={item.circuit_breaker_score}")

    # 4. 更新数据（Update）
    print("\n【4】更新测试...")
    if result:
        # 更新状态为 L2 干预期
        print("  更新状态：status_level=3 (L2 干预期), is_frozen=0")
        success = result.update_status(status_level=3, is_frozen=0)
        if success:
            print("  ✓ 更新成功")

        # 验证更新结果
        updated = QuestionFeatureEngineeringPo.get_by_question_id("test_uuid_001")
        if updated:
            print(f"  ✓ 验证更新：status_level={updated.status_level}, "
                  f"is_frozen={updated.is_frozen}")

    # 5. 插入一条熔断数据用于测试删除
    print("\n【5】插入熔断数据用于测试...")
    frozen_data = QuestionFeatureEngineeringPo(
        question_id="test_uuid_frozen",
        total_attempts=500,
        unique_user_count=400,
        avg_score_rate=Decimal("0.3000"),
        circuit_breaker_score=Decimal("0.9500"),
        status_level=4,
        is_frozen=1
    )
    frozen_id = frozen_data.save()
    print(f"✓ 插入熔断数据成功，ID={frozen_id}")

    # 验证熔断列表
    frozen_list = QuestionFeatureEngineeringPo.get_frozen_questions()
    print(f"✓ 当前被熔断的题目数量：{len(frozen_list)}")

    # 6. 删除数据（Delete）
    print("\n【6】删除测试...")
    if result:
        # 根据 question_id 先获取完整对象
        to_delete = QuestionFeatureEngineeringPo.get_by_question_id("test_uuid_001")
        if to_delete:
            to_delete.id = to_delete.id  # 确保 ID 有值
            success = to_delete.delete()
            if success:
                print(f"  ✓ 删除成功：question_id=test_uuid_001")
            else:
                print("  ✗ 删除失败")

    # 验证删除结果
    deleted_check = QuestionFeatureEngineeringPo.get_by_question_id("test_uuid_001")
    if deleted_check is None:
        print("  ✓ 验证删除：数据已不存在")
    else:
        print("  ✗ 验证失败：数据仍然存在")

    # 7. 清理测试数据
    print("\n【7】清理测试数据...")
    frozen_to_delete = QuestionFeatureEngineeringPo.get_by_question_id("test_uuid_frozen")
    if frozen_to_delete:
        frozen_to_delete.delete()
        print("  ✓ 已清理熔断测试数据")

    print("\n" + "=" * 50)
    print("=== 测试完成 ===")
    print("=" * 50)
