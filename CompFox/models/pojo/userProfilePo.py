from datetime import datetime
from typing import Optional, ClassVar, Dict, Any
from pydantic import Field, field_serializer
from Base.Repository.models.defaultDbModel import DefaultDbModel
import json


class UserProfilePo(DefaultDbModel):
    """
    员工合规画像模型
    用于记录员工的合规考核特征、培训画像、合规能力维度等综合信息
    """
    table_alias: ClassVar[str] = "compfox_user_profiles"
    create_table_sql: ClassVar[str] = f"""
        -- 用户画像表
        CREATE TABLE IF NOT EXISTS `compfox_user_profiles` (
            -- 核心 ID
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
            `user_id` VARCHAR(50) NOT NULL COMMENT '用户 ID',
            `profile_uuid` VARCHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '画像 UUID',

            -- 基础信息
            `nickname` VARCHAR(100) COMMENT '用户昵称',
            `avatar_url` VARCHAR(500) COMMENT '头像 URL',
            `grade_type` VARCHAR(20) COMMENT '职级类型：初级 | 中级 | 高级 | 管理层',
            `grade_level` TINYINT UNSIGNED COMMENT '职级：1=初级 2=中级 3=高级 4=管理层',
            `preferred_subject` VARCHAR(200) COMMENT '偏好合规领域（逗号分隔）',

            -- 培训统计
            `total_questions` INT UNSIGNED DEFAULT 0 COMMENT '累计答题数',
            `total_correct` INT UNSIGNED DEFAULT 0 COMMENT '累计正确数',
            `overall_correct_rate` DECIMAL(5,4) DEFAULT 0 COMMENT '总体正确率：0-1',
            `total_practice_time` INT UNSIGNED DEFAULT 0 COMMENT '累计练习时长（分钟）',
            `continuous_days` INT UNSIGNED DEFAULT 0 COMMENT '连续培训天数',
            `last_practice_date` DATE COMMENT '最后考核日期',

            -- 合规特有字段
            `compliance_risk_level` VARCHAR(20) COMMENT '合规风险等级：low|medium|high',
            `retrain_count` INT UNSIGNED DEFAULT 0 COMMENT '复训次数',

            -- 合规领域维度统计（JSON 格式）
            `subject_stats` TEXT COMMENT '各合规领域统计信息（JSON）',

            -- 知识点掌握情况（JSON 格式）
            `knowledge_mastery` TEXT COMMENT '知识点掌握情况（JSON）',

            -- 培训特征
            `learning_style` VARCHAR(50) COMMENT '培训风格：visual|auditory|reading|kinesthetic',
            `practice_frequency` VARCHAR(20) COMMENT '练习频率：daily|weekly|irregular',
            `preferred_difficulty` TINYINT DEFAULT 3 COMMENT '偏好难度：1-5',
            `average_response_time` INT UNSIGNED COMMENT '平均答题时长（秒）',

            -- 聊天画像
            `chat_profile` TEXT COMMENT '聊天画像（JSON）',

            -- 意图偏好统计
            `intent_stats` TEXT COMMENT '意图使用统计（JSON）',

            -- 能力维度评估（JSON 格式）
            `ability_dimensions` TEXT COMMENT '能力维度评估（JSON）',

            -- 薄弱知识点
            `weak_points` TEXT COMMENT '薄弱知识点（JSON 数组）',

            -- 推荐题目池
            `recommend_pool` TEXT COMMENT '推荐题目池（JSON）',

            -- 培训目标
            `learning_goal` VARCHAR(500) COMMENT '培训目标',
            `target_score` DECIMAL(5,4) COMMENT '目标正确率',

            -- AI 画像总结
            `ai_summary` TEXT COMMENT 'AI 生成的画像总结',
            `ai_model` VARCHAR(50) COMMENT 'AI 模型名称',
            `ai_prompt` TEXT COMMENT '生成画像使用的 prompt',

            -- 画像版本
            `profile_version` INT UNSIGNED DEFAULT 1 COMMENT '画像版本号',
            `last_updated_type` VARCHAR(50) COMMENT '最后更新类型：chat|practice|manual',

            -- 时间戳
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

            -- 主键与索引
            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_user_id` (`user_id`),
            KEY `idx_grade_type` (`grade_type`),
            KEY `idx_grade_level` (`grade_level`),
            KEY `idx_created_at` (`created_at`),
            KEY `idx_updated_at` (`updated_at`),
            KEY `idx_last_practice` (`last_practice_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户画像表';
    """

    # 字段定义
    id: Optional[int] = Field(None, description="主键 ID")
    user_id: str = Field(..., description="用户 ID")
    profile_uuid: Optional[str] = Field(None, description="画像 UUID")

    # 基础信息
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar_url: Optional[str] = Field(None, description="头像 URL")
    grade_type: Optional[str] = Field(None, description="职级类型：初级 | 中级 | 高级 | 管理层")
    grade_level: Optional[int] = Field(None, description="职级：1=初级 2=中级 3=高级 4=管理层")
    preferred_subject: Optional[str] = Field(None, description="偏好合规领域")

    # 考核统计
    total_questions: Optional[int] = Field(0, description="累计答题数")
    total_correct: Optional[int] = Field(0, description="累计正确数")
    overall_correct_rate: Optional[float] = Field(0, description="总体合规掌握率")
    total_practice_time: Optional[int] = Field(0, description="累计培训时长（分钟）")
    continuous_days: Optional[int] = Field(0, description="连续培训天数")
    last_practice_date: Optional[datetime] = Field(None, description="最后考核日期")

    # 合规特有字段
    compliance_risk_level: Optional[str] = Field(None, description="合规风险等级：low|medium|high")
    retrain_count: Optional[int] = Field(0, description="复训次数")

    # JSON 字段（存储为字符串）
    subject_stats: Optional[str] = Field(None, description="各合规领域统计信息（JSON）")
    knowledge_mastery: Optional[str] = Field(None, description="知识点掌握情况（JSON）")
    chat_profile: Optional[str] = Field(None, description="聊天画像（JSON）")
    intent_stats: Optional[str] = Field(None, description="意图使用统计（JSON）")
    ability_dimensions: Optional[str] = Field(None, description="能力维度评估（JSON）")
    weak_points: Optional[str] = Field(None, description="薄弱知识点（JSON 数组）")
    recommend_pool: Optional[str] = Field(None, description="推荐题目池（JSON）")

    # 培训特征
    learning_style: Optional[str] = Field(None, description="培训风格")
    practice_frequency: Optional[str] = Field(None, description="考核频率")
    preferred_difficulty: Optional[int] = Field(3, description="偏好难度")
    average_response_time: Optional[int] = Field(None, description="平均答题时长（秒）")

    # 培训目标
    learning_goal: Optional[str] = Field(None, description="培训目标")
    target_score: Optional[float] = Field(None, description="目标正确率")

    # AI 画像总结
    ai_summary: Optional[str] = Field(None, description="AI 生成的画像总结")
    ai_model: Optional[str] = Field(None, description="AI 模型名称")
    ai_prompt: Optional[str] = Field(None, description="生成画像使用的 prompt")

    # 画像版本
    profile_version: Optional[int] = Field(1, description="画像版本号")
    last_updated_type: Optional[str] = Field(None, description="最后更新类型")

    # 时间戳
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_serializer('subject_stats', 'knowledge_mastery', 'chat_profile',
                      'intent_stats', 'ability_dimensions', 'weak_points',
                      'recommend_pool', 'ai_summary', 'ai_prompt')
    def serialize_json_fields(self, value, _info):
        """将 dict/list 类型的字段序列化为 JSON 字符串"""
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    @staticmethod
    def _parse_json_field(value, default_type='dict'):
        if not value:
            return {} if default_type == 'dict' else []
        if isinstance(value, (dict, list)):
            return value
        return json.loads(value)

    @property
    def subject_stats_dict(self) -> Dict:
        """获取合规领域统计字典"""
        return self._parse_json_field(self.subject_stats)

    @property
    def knowledge_mastery_dict(self) -> Dict:
        """获取知识点掌握字典"""
        return self._parse_json_field(self.knowledge_mastery)

    @property
    def chat_profile_dict(self) -> Dict:
        """获取聊天画像字典"""
        return self._parse_json_field(self.chat_profile)

    @property
    def intent_stats_dict(self) -> Dict:
        """获取意图统计字典"""
        return self._parse_json_field(self.intent_stats)

    @property
    def ability_dimensions_dict(self) -> Dict:
        """获取能力维度字典"""
        return self._parse_json_field(self.ability_dimensions)

    @property
    def weak_points_list(self) -> list:
        """获取薄弱知识点列表"""
        return self._parse_json_field(self.weak_points, default_type='list')

    @property
    def mini_dict(self) -> Dict:
        """获取简化版画像信息"""
        return {
            'user_id': self.user_id,
            'nickname': self.nickname,
            'grade_type': self.grade_type,
            'grade_level': self.grade_level,
            'total_questions': self.total_questions,
            'overall_correct_rate': self.overall_correct_rate,
            'continuous_days': self.continuous_days,
            'weak_points': self.weak_points_list,
            'learning_goal': self.learning_goal,
            'ai_summary': self.ai_summary
        }

    @classmethod
    def get_or_create(cls, user_id: str) -> 'UserProfilePo':
        """
        获取或创建用户画像

        Args:
            user_id: 用户 ID

        Returns:
            用户画像对象
        """
        import uuid
        import json
        from datetime import date

        profile = cls.find_by(user_id=user_id, limit=1)
        if profile:
            return profile[0]

        # 创建新画像 - JSON 字段需要传递字符串而不是 dict/list
        new_profile = cls(
            user_id=user_id,
            profile_uuid=str(uuid.uuid4()),
            total_questions=0,
            total_correct=0,
            overall_correct_rate=0,
            subject_stats='{}',
            knowledge_mastery='{}',
            chat_profile=json.dumps({'total_chats': 0, 'common_questions': [], 'interaction_score': 0}),
            intent_stats='{}',
            ability_dimensions='{}',
            weak_points='[]',
            recommend_pool='[]'
        )
        new_profile.save()
        return new_profile

    def update_practice_stats(self, subject: str, is_correct: bool,
                              knowledge_points: list = None, score: float = None):
        """
        更新练习统计

        Args:
            subject: 合规领域
            is_correct: 是否正确
            knowledge_points: 知识点列表
            score: 得分率
        """
        import json

        # 更新总体统计
        self.total_questions = (self.total_questions or 0) + 1
        if is_correct:
            self.total_correct = (self.total_correct or 0) + 1

        # 更新正确率
        if self.total_questions > 0:
            self.overall_correct_rate = self.total_correct / self.total_questions

        # 更新最后练习日期
        self.last_practice_date = datetime.now().date()

        # 更新合规领域统计
        subject_stats = self.subject_stats_dict
        if subject not in subject_stats:
            subject_stats[subject] = {
                'count': 0,
                'correct': 0,
                'correct_rate': 0,
                'weak_points': []
            }

        subject_stats[subject]['count'] += 1
        if is_correct:
            subject_stats[subject]['correct'] += 1
        subject_stats[subject]['correct_rate'] = (
            subject_stats[subject]['correct'] / subject_stats[subject]['count']
        )

        # 更新知识点掌握情况
        if knowledge_points:
            knowledge_mastery = self.knowledge_mastery_dict
            for kp in knowledge_points:
                key = f"{subject}_{kp}"
                if key not in knowledge_mastery:
                    knowledge_mastery[key] = {
                        'mastery': 0.5,
                        'question_count': 0,
                        'last_review': None
                    }
                knowledge_mastery[key]['question_count'] += 1
                knowledge_mastery[key]['last_review'] = datetime.now().isoformat()
                # 根据正确率更新掌握程度
                if is_correct:
                    knowledge_mastery[key]['mastery'] = min(1.0,
                        knowledge_mastery[key]['mastery'] + 0.1)
                else:
                    knowledge_mastery[key]['mastery'] = max(0.0,
                        knowledge_mastery[key]['mastery'] - 0.05)

            self.knowledge_mastery = knowledge_mastery

        # 识别薄弱知识点（掌握度<0.6）
        weak_points = []
        for kp_key, kp_data in self.knowledge_mastery_dict.items():
            if kp_data.get('mastery', 0.5) < 0.6:
                kp_name = kp_key.split('_', 1)[1] if '_' in kp_key else kp_key
                weak_points.append(kp_name)
        self.weak_points = weak_points

        self.subject_stats = subject_stats
        self.last_updated_type = 'practice'
        self.save()

    def update_chat_profile(self, intent: str, question: str = None):
        """
        更新聊天画像

        Args:
            intent: 意图类型
            question: 用户问题
        """
        chat_profile = self.chat_profile_dict
        chat_profile['total_chats'] = chat_profile.get('total_chats', 0) + 1

        # 更新常见意图统计
        intent_stats = self.intent_stats_dict
        intent_stats[intent] = intent_stats.get(intent, 0) + 1

        # 更新常见问题（保留最近 10 个）
        common_questions = chat_profile.get('common_questions', [])
        if question:
            common_questions.append(question)
            if len(common_questions) > 10:
                common_questions = common_questions[-10:]
        chat_profile['common_questions'] = common_questions

        # 计算互动分数（基于聊天次数和意图多样性）
        total_chats = chat_profile['total_chats']
        intent_diversity = len(intent_stats)
        interaction_score = min(1.0, (total_chats / 100) * 0.5 + (intent_diversity / 7) * 0.5)
        chat_profile['interaction_score'] = interaction_score

        self.chat_profile = chat_profile
        self.intent_stats = intent_stats
        self.last_updated_type = 'chat'
        self.save()

    def generate_ai_summary(self) -> str:
        """
        生成 AI 画像总结

        Returns:
            AI 生成的画像总结
        """
        from Base.Ai.base import SystemMessages, UserMessages
        from Base.Ai.llms.qwenLlm import get_default_qwen_llm

        # 构建画像数据摘要
        summary_data = {
            'basic_info': {
                'grade_type': self.grade_type,
                'grade_level': self.grade_level,
            },
            'learning_stats': {
                'total_questions': self.total_questions,
                'correct_rate': round(self.overall_correct_rate, 2) if self.overall_correct_rate else 0,
                'continuous_days': self.continuous_days,
            },
            'subject_stats': self.subject_stats_dict,
            'weak_points': self.weak_points_list,
            'chat_profile': self.chat_profile_dict,
            'ability_dimensions': self.ability_dimensions_dict,
        }

        system_prompt = """你是一个专业的金融合规培训 AI 助手，擅长分析员工的合规考核情况并生成合规能力画像总结。

请根据提供的员工合规培训数据，生成一段专业客观的画像总结，包括：
1. 整体合规考核情况概述
2. 强项合规领域和进步点
3. 需要加强的合规知识薄弱点和风险盲区
4. 个性化的复训建议和合规风险等级评估

请用第二人称"你"来称呼员工，语言专业严谨，注重合规风险意识。"""

        user_prompt = f"""请为以下员工合规培训数据生成画像总结：

{json.dumps(summary_data, ensure_ascii=False, indent=2)}
"""

        messages = [
            SystemMessages(prompt=system_prompt),
            UserMessages(prompt=user_prompt)
        ]

        llm = get_default_qwen_llm()
        response = llm.chat(messages)

        # 保存 AI 总结
        self.ai_summary = response
        self.ai_model = llm.model_name
        self.ai_prompt = str(messages)
        self.save()

        return response


if __name__ == '__main__':
    # 创建表
    po = UserProfilePo()
    po.create_table()

    # 测试示例
    print("\n=== 测试用户画像 ===")

    # 获取或创建用户画像
    profile = UserProfilePo.get_or_create('test_user_001')
    print(f"用户画像：{profile.mini_dict}")

    # 更新练习统计
    profile.update_practice_stats(
        subject='math',
        is_correct=True,
        knowledge_points=['函数', '一次函数'],
        score=0.8
    )
    print(f"更新后答题数：{profile.total_questions}")

    # 更新聊天画像
    profile.update_chat_profile(
        intent='generate_question',
        question='帮我出一道数学题'
    )
    print(f"聊天次数：{profile.chat_profile_dict.get('total_chats')}")

    # 生成 AI 总结
    ai_summary = profile.generate_ai_summary()
    print(f"AI 总结：{ai_summary}")
