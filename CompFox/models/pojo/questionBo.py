from typing import Optional, Literal

from pydantic import BaseModel, Field


class QuestionRandomBo(BaseModel):
    """
    随机出题函数的入参 BO 类
    """
    subject: Optional[str] = Field(None, description="合规领域")
    question_type: Optional[str] = Field(None, description="题型")
    difficulty_level: Optional[int | str] = Field(None, description="难度等级（1-5 整数或 basic/intermediate/advanced 字符串）")
    grade_type: Optional[Literal["初级", "中级", "高级", "管理层"]] = Field(None, description="职级")


class AiJudgeQuestionBo(BaseModel):
    """
    AI 判题函数的入参 BO 类
    """
    user_id: Optional[int | str] = Field(None, description="用户 ID")
    question_id: int | str = Field(..., description="题目 ID 或 UUID")
    answer: str = Field(..., description="用户答案")
    source: Optional[str] = Field(None, description="来源")


class QuestionImportBo(BaseModel):
    """
    题目导入接口的入参 BO 类
    """
    text: str = Field(..., description="包含题目的文本")
    subject: str = Field(..., description="合规领域")
    grade_range: str = Field("1-2", description="职级范围（如 1-2 初级，2-3 中级，3-4 高级/管理层）")
    difficulty: int = Field(3, description="默认难度（1-5）")
    question_type: Optional[str] = Field(None, description="指定题型（可选）")
    created_by: int = Field(505, description="创建人 ID")
