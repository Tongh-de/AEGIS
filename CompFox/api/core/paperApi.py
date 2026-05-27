import logging
from typing import Optional

from fastapi import APIRouter, Query, Form

from Base.RicUtils.httpUtils import HttpResponse
from CompFox.services.paperService import get_paper_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compfox/paper")


@router.get("/list")
def get_paper_list(
        page: Optional[int] = Query(1, description="页码"),
        page_size: Optional[int] = Query(10, description="每页数量"),
        subject: Optional[str] = Query(None, description="合规领域"),
        status: Optional[str] = Query(None, description="状态")
):
    """
    分页获取试卷列表

    Args:
        page: 页码
        page_size: 每页数量
        subject: 合规领域筛选
        status: 状态筛选

    Returns:
        分页结果
    """
    try:
        result = get_paper_service().get_paper_list(
            page=page or 1,
            page_size=page_size or 10,
            subject=subject,
            status=status
        )
        return HttpResponse.ok(result)
    except Exception as e:
        logger.error(f"获取试卷列表失败：{str(e)}")
        return HttpResponse.error(f"获取试卷列表失败：{str(e)}")


@router.get("/{paper_id}")
def get_paper_detail(paper_id: int):
    """
    获取试卷详情（员工考核用）

    Args:
        paper_id: 试卷 ID

    Returns:
        试卷详情，包含题目列表
    """
    try:
        detail = get_paper_service().get_paper_detail(paper_id)
        return HttpResponse.ok(detail)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取试卷详情失败：{str(e)}")
        return HttpResponse.error(f"获取试卷详情失败：{str(e)}")


@router.post("")
def create_paper(
        paper_name: str = Form(..., description="试卷名称"),
        question_ids: str = Form(..., description="题目 ID 列表（逗号分隔）"),
        scores: Optional[str] = Form(None, description="每题分值（逗号分隔）"),
        description: Optional[str] = Form(None, description="试卷描述"),
        subject: Optional[str] = Form(None, description="合规领域"),
        duration_minutes: Optional[int] = Form(30, description="考核时长（分钟）"),
        created_by: Optional[int] = Form(505, description="创建者 ID")
):
    """
    创建合规试卷

    Args:
        paper_name: 试卷名称
        question_ids: 题目 ID 列表（逗号分隔）
        scores: 每题分值（逗号分隔，可选）
        description: 试卷描述
        subject: 合规领域
        duration_minutes: 考试时长
        created_by: 创建者 ID

    Returns:
        创建的试卷信息
    """
    try:
        # 解析逗号分隔的 ID 列表
        q_ids = [int(x.strip()) for x in question_ids.split(',') if x.strip()]
        score_list = None
        if scores:
            score_list = [float(x.strip()) for x in scores.split(',') if x.strip()]

        service = get_paper_service()
        paper = service.create_paper(
            paper_name=paper_name,
            question_ids=q_ids,
            scores=score_list,
            description=description,
            subject=subject,
            duration_minutes=duration_minutes,
            created_by=created_by
        )

        return HttpResponse.ok({
            'paper_id': paper.id,
            'paper_uuid': paper.paper_uuid,
            'paper_name': paper.paper_name,
            'total_score': paper.total_score
        })
    except Exception as e:
        logger.error(f"创建试卷失败：{str(e)}")
        return HttpResponse.error(f"创建试卷失败：{str(e)}")


@router.get("/{paper_id}/versions")
def get_paper_versions(paper_id: int):
    """
    获取试卷版本历史

    Args:
        paper_id: 试卷 ID

    Returns:
        版本历史列表
    """
    try:
        versions = get_paper_service().get_paper_versions(paper_id)
        return HttpResponse.ok(versions)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取版本历史失败：{str(e)}")
        return HttpResponse.error(f"获取版本历史失败：{str(e)}")


@router.put("/{paper_id}/publish")
def publish_paper(paper_id: int):
    """
    发布试卷

    Args:
        paper_id: 试卷 ID

    Returns:
        操作结果
    """
    try:
        success = get_paper_service().publish_paper(paper_id)
        if success:
            return HttpResponse.ok({'message': '试卷发布成功'})
        else:
            return HttpResponse.error('试卷发布失败')
    except Exception as e:
        logger.error(f"发布试卷失败：{str(e)}")
        return HttpResponse.error(f"发布试卷失败：{str(e)}")


@router.put("/{paper_id}")
def update_paper(
        paper_id: int,
        paper_name: str = Form(..., description="试卷名称"),
        question_ids: str = Form(..., description="题目 ID 列表（逗号分隔）"),
        scores: Optional[str] = Form(None, description="每题分值（逗号分隔）"),
        description: Optional[str] = Form(None, description="试卷描述"),
        subject: Optional[str] = Form(None, description="合规领域"),
        duration_minutes: Optional[int] = Form(30, description="考试时长（分钟）"),
        updated_by: Optional[int] = Form(505, description="更新者 ID")
):
    """
    更新合规试卷（创建新版本）

    Args:
        paper_id: 试卷 ID
        paper_name: 试卷名称
        question_ids: 题目 ID 列表（逗号分隔）
        scores: 每题分值（逗号分隔，可选）
        description: 试卷描述
        subject: 合规领域
        duration_minutes: 考试时长
        updated_by: 更新者 ID

    Returns:
        更新后的试卷信息
    """
    try:
        # 解析逗号分隔的 ID 列表
        q_ids = [int(x.strip()) for x in question_ids.split(',') if x.strip()]
        score_list = None
        if scores:
            score_list = [float(x.strip()) for x in scores.split(',') if x.strip()]

        service = get_paper_service()
        paper = service.update_paper(
            paper_id=paper_id,
            paper_name=paper_name,
            question_ids=q_ids,
            scores=score_list,
            description=description,
            subject=subject,
            duration_minutes=duration_minutes,
            updated_by=updated_by
        )

        return HttpResponse.ok({
            'paper_id': paper.id,
            'paper_uuid': paper.paper_uuid,
            'paper_name': paper.paper_name,
            'total_score': paper.total_score
        })
    except Exception as e:
        logger.error(f"更新试卷失败：{str(e)}")
        return HttpResponse.error(f"更新试卷失败：{str(e)}")


@router.delete("/{paper_id}")
def delete_paper(paper_id: int):
    """
    删除试卷（软删除）

    Args:
        paper_id: 试卷 ID

    Returns:
        操作结果
    """
    try:
        success = get_paper_service().delete_paper(paper_id)
        if success:
            return HttpResponse.ok({'message': '试卷删除成功'})
        else:
            return HttpResponse.error('试卷删除失败')
    except Exception as e:
        logger.error(f"删除试卷失败：{str(e)}")
        return HttpResponse.error(f"删除试卷失败：{str(e)}")


@router.post("/{paper_id}/restore")
def restore_paper_version(
        paper_id: int,
        updated_by: Optional[int] = Form(505, description="更新者 ID")
):
    """
    恢复试卷历史版本

    Args:
        paper_id: 要恢复的版本 ID
        updated_by: 更新者 ID

    Returns:
        恢复后的试卷信息
    """
    try:
        service = get_paper_service()
        paper = service.restore_version(paper_id=paper_id, updated_by=updated_by)

        return HttpResponse.ok({
            'paper_id': paper.id,
            'paper_uuid': paper.paper_uuid,
            'paper_name': paper.paper_name,
            'total_score': paper.total_score,
            'message': '版本恢复成功'
        })
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"恢复试卷版本失败：{str(e)}")
        return HttpResponse.error(f"恢复试卷版本失败：{str(e)}")
