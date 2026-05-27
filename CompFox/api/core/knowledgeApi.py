import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Query, Form

from Base.RicUtils.httpUtils import HttpResponse
from CompFox.models.pojo.knowledgeBo import KnowledgeImportTextBo, KnowledgeImportUrlBo, KnowledgeSearchBo
from CompFox.models.pojo.knowledgeDocPo import KnowledgeDocPo
from CompFox.services.knowledgeService import get_knowledge_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compfox/knowledge")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/import/text")
def import_text(
    doc_name: str = Form(..., description="文档名称"),
    content: str = Form(..., description="文本内容"),
    source_type: str = Form("raw_text", description="来源类型"),
    tags: Optional[str] = Form(None, description="标签（逗号分隔）"),
    effective_date: Optional[str] = Form(None, description="生效日期"),
    version: Optional[str] = Form(None, description="版本号"),
):
    """导入纯文本到知识库"""
    try:
        bo = KnowledgeImportTextBo(
            doc_name=doc_name,
            content=content,
            source_type=source_type,
            tags=tags,
            effective_date=effective_date,
            version=version,
        )
        ks = get_knowledge_service()
        result = ks.import_text(bo)
        return HttpResponse.ok(result)
    except Exception as e:
        logger.error(f"文本导入知识库失败：{e}")
        return HttpResponse.error(f"文本导入失败：{e}")


@router.post("/import/file")
def import_file(
    file: UploadFile = File(..., description="上传文件（PDF/DOCX/TXT/Excel）"),
    tags: Optional[str] = Form(None, description="标签（逗号分隔）"),
    effective_date: Optional[str] = Form(None, description="生效日期"),
    version: Optional[str] = Form(None, description="版本号"),
):
    """上传文件导入知识库"""
    import os
    import tempfile

    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        return HttpResponse.error(f"文件大小超过限制（最大 50MB）：{file.size} 字节")

    ext = os.path.splitext(file.filename or '')[1].lower()
    if ext not in ('.pdf', '.docx', '.txt', '.xlsx', '.xls'):
        return HttpResponse.error(f"不支持的文件类型：{ext}，支持 PDF/DOCX/TXT/Excel")

    tmp_path = None
    try:
        # 保存到临时文件
        suffix = ext if ext else '.tmp'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        ks = get_knowledge_service()
        result = ks.import_file(
            file_path=tmp_path,
            file_name=file.filename,
            tags=tags,
            effective_date=effective_date,
            version=version,
        )
        return HttpResponse.ok(result)
    except Exception as e:
        logger.error(f"文件导入知识库失败：{e}")
        return HttpResponse.error(f"文件导入失败：{e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/import/url")
def import_url(
    url: str = Form(..., description="文档 URL"),
    doc_name: Optional[str] = Form(None, description="文档名称"),
    source_type: Optional[str] = Form(None, description="来源类型"),
    tags: Optional[str] = Form(None, description="标签"),
    effective_date: Optional[str] = Form(None, description="生效日期"),
    version: Optional[str] = Form(None, description="版本号"),
):
    """从 URL 抓取并导入知识库"""
    try:
        bo = KnowledgeImportUrlBo(
            url=url,
            doc_name=doc_name,
            source_type=source_type,
            tags=tags,
            effective_date=effective_date,
            version=version,
        )
        ks = get_knowledge_service()
        result = ks.import_url(bo)
        return HttpResponse.ok(result)
    except Exception as e:
        logger.error(f"URL 导入知识库失败：{e}")
        return HttpResponse.error(f"URL 导入失败：{e}")


@router.get("/search")
def search_knowledge(
    query: str = Query(..., description="检索查询文本"),
    limit: int = Query(5, description="返回结果数量上限"),
    source_type: Optional[str] = Query(None, description="按来源类型过滤"),
    tags: Optional[str] = Query(None, description="按标签过滤"),
):
    """检索知识库"""
    try:
        bo = KnowledgeSearchBo(
            query=query,
            limit=limit,
            source_type=source_type,
            tags=tags,
        )
        ks = get_knowledge_service()
        results = ks.search(bo)
        return HttpResponse.ok(results)
    except Exception as e:
        logger.error(f"知识库检索失败：{e}")
        return HttpResponse.error(f"检索失败：{e}")


@router.get("/documents")
def list_documents():
    """列出知识库文档清单"""
    try:
        ks = get_knowledge_service()
        docs = ks.list_documents()
        return HttpResponse.ok(docs)
    except Exception as e:
        logger.error(f"列出知识库文档失败：{e}")
        return HttpResponse.error(f"列出文档失败：{e}")


@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    """删除知识库文档"""
    try:
        ks = get_knowledge_service()
        ok = ks.delete_document(doc_id)
        if ok:
            return HttpResponse.ok({"doc_id": doc_id, "deleted": True})
        return HttpResponse.error(f"删除文档失败：{doc_id}")
    except Exception as e:
        logger.error(f"删除知识库文档失败：{e}")
        return HttpResponse.error(f"删除失败：{e}")
