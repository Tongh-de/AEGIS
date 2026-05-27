from typing import Optional, Literal

from pydantic import BaseModel, Field


class QuestionRandomBo(BaseModel):
    """
    随机出题函数的入参 BO 类
    """
    subject: Optional[str] = Field(None, description="科目")
    question_type: Optional[str] = Field(None, description="题型")
    difficulty_level: Optional[int | str] = Field(None, description="难度等级（1-5 整数或 easy/medium/hard 字符串）")
    grade_type: Optional[Literal["小学", "初中", "高中"]] = Field(None, description="年级类型")


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
    subject: str = Field(..., description="科目")
    grade_range: str = Field("7-9", description="年级范围（如 1-6 小学，7-9 初中，10-12 高中）")
    difficulty: int = Field(3, description="默认难度（1-5）")
    question_type: Optional[str] = Field(None, description="指定题型（可选）")
    created_by: int = Field(505, description="创建人 ID")
