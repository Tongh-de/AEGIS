from pydantic import Field

from Education.models.pojo.questionBo import QuestionRandomBo


class QuestionRandomParamVo(QuestionRandomBo):
    """
    随机出题接口的VO入参类
    """
    num: int = Field(1, description="生成数量")