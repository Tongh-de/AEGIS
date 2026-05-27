from datetime import datetime
from typing import Optional, List, Any, Literal
from pydantic import BaseModel, Field


class AgentChatParams(BaseModel):
    """
    Agent 聊天接口请求参数
    """
    question: str = Field(..., description="用户问题")
    user_id: Optional[str] = Field(None, description="用户标识")
    session_id: Optional[str] = Field(None, description="会话标识")
    is_stream: bool = Field(False, description="是否流式输出")
    is_thinking: bool = Field(False, description="是否思考模式")
    current_question_id: Optional[str] = Field(None, description="当前题目 ID（用于判题、解析等意图）")
    current_question_text: Optional[str] = Field(None, description="当前题目文本（用于解析意图）")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "帮我出一道初二数学的函数题",
                "user_id": "user_123",
                "session_id": "session_456",
                "is_stream": True,
                "is_thinking": False
            }
        }


class IntentRecognitionResult(BaseModel):
    """
    意图识别结果
    """
    intent: str = Field(..., description="意图类型")
    confidence: float = Field(..., description="置信度 0-1")
    params: dict = Field(default_factory=dict, description="意图参数")
    reason: str = Field("", description="判断理由")

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "generate_question",
                "confidence": 0.95,
                "params": {
                    "subject": "math",
                    "grade_type": "初中",
                    "difficulty_level": 3
                },
                "reason": "用户明确要求出题，并指定了年级、科目和难度"
            }
        }


class AgentChatResponse(BaseModel):
    """
    Agent 聊天响应
    """
    intent: str = Field(..., description="识别的意图")
    answer: str = Field(..., description="AI 回复内容")
    data: Optional[Any] = Field(None, description="附加数据（如题目信息、判题结果等）")
    thinking: Optional[str] = Field(None, description="思考过程（如果开启思考模式）")
    session_id: Optional[str] = Field(None, description="会话 ID")
    duration_ms: Optional[int] = Field(None, description="耗时（毫秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "generate_question",
                "answer": "好的，我已经为您生成了一道初中数学函数题：...",
                "data": {
                    "question_id": 123,
                    "question_text": "已知函数 f(x) = 2x + 1，求 f(3) 的值"
                },
                "session_id": "session_uuid_xxx",
                "duration_ms": 1500
            }
        }


class GenerateQuestionParams(BaseModel):
    """
    出题意图参数
    """
    subject: Optional[str] = Field(None, description="科目")
    grade_type: Optional[Literal["小学", "初中", "高中"]] = Field(None, description="年级类型")
    question_type: Optional[str] = Field(None, description="题型")
    difficulty_level: Optional[int] = Field(None, description="难度等级 1-5")
    knowledge_points: Optional[str] = Field(None, description="知识点")


class JudgeAnswerParams(BaseModel):
    """
    判题意图参数
    """
    question_id: Optional[str] = Field(None, description="题目 ID 或 UUID")
    answer: str = Field(..., description="用户答案")


class ExplainQuestionParams(BaseModel):
    """
    题目解析意图参数
    """
    question_id: Optional[str] = Field(None, description="题目 ID 或 UUID")
    question_text: Optional[str] = Field(None, description="题目文本")


class ChatParams(BaseModel):
    """
    聊天意图参数
    """
    topic: Optional[str] = Field(None, description="话题主题")


class RecommendQuestionsParams(BaseModel):
    """
    推荐题目意图参数
    """
    subject: Optional[str] = Field(None, description="科目")
    weak_points: Optional[str] = Field(None, description="薄弱知识点")


class LearningProgressParams(BaseModel):
    """
    学习进度查询意图参数
    """
    subject: Optional[str] = Field(None, description="科目")
    time_range: Optional[Literal["今天", "本周", "本月", "全部"]] = Field("全部", description="时间范围")


class ImportQuestionsParams(BaseModel):
    """
    题目导入意图参数
    """
    subject: str = Field(..., description="科目")
    grade_range: str = Field("7-9", description="年级范围")
    text: Optional[str] = Field(None, description="题目文本")
