from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeImportTextBo(BaseModel):
    """文本导入知识库的入参 BO"""
    doc_name: str = Field(..., description="文档名称")
    content: str = Field(..., description="文本内容")
    source_type: str = Field("raw_text", description="来源类型：raw_text")
    tags: Optional[str] = Field(None, description="标签（逗号分隔）")
    effective_date: Optional[str] = Field(None, description="生效日期")
    version: Optional[str] = Field(None, description="版本号")


class KnowledgeImportUrlBo(BaseModel):
    """URL 导入知识库的入参 BO"""
    url: str = Field(..., description="文档 URL")
    doc_name: Optional[str] = Field(None, description="文档名称（可选，默认从 URL 提取）")
    source_type: Optional[str] = Field(None, description="来源类型（可选，默认从 URL 后缀推断）")
    tags: Optional[str] = Field(None, description="标签（逗号分隔）")
    effective_date: Optional[str] = Field(None, description="生效日期")
    version: Optional[str] = Field(None, description="版本号")


class KnowledgeSearchBo(BaseModel):
    """知识库检索的入参 BO"""
    query: str = Field(..., description="检索查询文本")
    limit: int = Field(5, description="返回结果数量上限")
    source_type: Optional[str] = Field(None, description="按来源类型过滤")
    tags: Optional[str] = Field(None, description="按标签过滤")
