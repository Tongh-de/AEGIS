import logging
from typing import Optional

from fastapi import APIRouter, Request, Query, Body

from Base.RicUtils.httpUtils import HttpResponse
from CompFox.services.examService import get_exam_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compfox/exam")


@router.post("/start")
def start_exam(request: Request, paper_id: int, user_id: str):
    """
    开始合规考核

    Args:
        paper_id: 试卷 ID
        user_id: 用户 ID

    Returns:
        考试信息
    """
    try:
        # 获取用户 IP
        user_ip = request.client.host if request.client else None

        result = get_exam_service().start_exam(
            paper_id=paper_id,
            user_id=user_id,
            user_ip=user_ip
        )
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"开始考试失败：{str(e)}")
        return HttpResponse.error(f"开始考试失败：{str(e)}")


@router.post("/{exam_id}/submit")
def submit_exam(exam_id: int, answers: dict = Body(..., description="用户答案字典 {question_id: answer}")):
    """
    提交考核答卷

    Args:
        exam_id: 考试记录 ID
        answers: 用户答案字典 {question_id: answer}

    Returns:
        判卷结果
    """
    try:
        result = get_exam_service().submit_exam(
            exam_id=exam_id,
            user_answers=answers
        )
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"提交考核答卷失败：{str(e)}")
        return HttpResponse.error(f"提交考核答卷失败：{str(e)}")


@router.get("/result")
def get_exam_result(exam_id: Optional[int] = Query(None, description="考试记录 ID（整数）"),
                    exam_uuid: Optional[str] = Query(None, description="考试 UUID（字符串）")):
    """
    获取考试结果

    Args:
        exam_id: 考试记录 ID（整数）
        exam_uuid: 考试 UUID（字符串，与 exam_id 二选一）

    Returns:
        考试结果信息
    """
    try:
        # 优先使用 exam_id，如果没有则尝试 exam_uuid
        if exam_id is not None:
            result = get_exam_service().get_exam_result(exam_id=exam_id)
        elif exam_uuid is not None:
            # 通过 UUID 获取考试记录
            from CompFox.models.pojo.examPo import ExamPo
            exam = ExamPo.get_by_uuid(exam_uuid)
            if not exam:
                return HttpResponse.error("考试记录不存在")
            result = get_exam_service().get_exam_result(exam_id=exam.id)
        else:
            return HttpResponse.error("缺少 exam_id 或 exam_uuid 参数")
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取考试结果失败：{str(e)}")
        return HttpResponse.error(f"获取考试结果失败：{str(e)}")


@router.get("/{exam_id}/result")
def get_exam_result_by_id(exam_id: int):
    """
    获取考试结果（通过 ID）

    Args:
        exam_id: 考试记录 ID

    Returns:
        考试结果信息
    """
    try:
        result = get_exam_service().get_exam_result(exam_id=exam_id)
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取考试结果失败：{str(e)}")
        return HttpResponse.error(f"获取考试结果失败：{str(e)}")


@router.get("/result/detail")
def get_exam_result_detail(exam_id: Optional[int] = Query(None, description="考试记录 ID（整数）"),
                           exam_uuid: Optional[str] = Query(None, description="考试 UUID（字符串）")):
    """
    获取考试结果详情（包含每题详细内容）

    Args:
        exam_id: 考试记录 ID（整数）
        exam_uuid: 考试 UUID（字符串，与 exam_id 二选一）

    Returns:
        考试结果详情信息
    """
    try:
        # 优先使用 exam_id，如果没有则尝试 exam_uuid
        if exam_id is not None:
            result = get_exam_service().get_exam_result_detail(exam_id=exam_id)
        elif exam_uuid is not None:
            # 通过 UUID 获取考试记录
            from CompFox.models.pojo.examPo import ExamPo
            exam = ExamPo.get_by_uuid(exam_uuid)
            if not exam:
                return HttpResponse.error("考试记录不存在")
            result = get_exam_service().get_exam_result_detail(exam_id=exam.id)
        else:
            return HttpResponse.error("缺少 exam_id 或 exam_uuid 参数")
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取考试结果详情失败：{str(e)}")
        return HttpResponse.error(f"获取考试结果详情失败：{str(e)}")


@router.get("/{exam_id}/result/detail")
def get_exam_result_detail_by_id(exam_id: int):
    """
    获取考试结果详情（通过 ID）

    Args:
        exam_id: 考试记录 ID

    Returns:
        考试结果详情信息
    """
    try:
        result = get_exam_service().get_exam_result_detail(exam_id=exam_id)
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"获取考试结果详情失败：{str(e)}")
        return HttpResponse.error(f"获取考试结果详情失败：{str(e)}")


@router.get("/history")
def get_exam_history(user_id: str, limit: Optional[int] = Query(10, description="返回数量限制")):
    """
    查询用户历史答题记录

    Args:
        user_id: 用户 ID
        limit: 返回数量限制

    Returns:
        历史答题记录列表
    """
    try:
        history = get_exam_service().get_user_history(user_id=user_id, limit=limit or 10)
        return HttpResponse.ok(history)
    except Exception as e:
        logger.error(f"查询历史记录失败：{str(e)}")
        return HttpResponse.error(f"查询历史记录失败：{str(e)}")


@router.post("/{exam_id}/grade")
def grade_exam(exam_id: int):
    """
    手动触发判卷（一般不需要，系统会在提交时自动判卷）

    Args:
        exam_id: 考试记录 ID

    Returns:
        判卷结果
    """
    try:
        result = get_exam_service().grade_exam(exam_id=exam_id)
        return HttpResponse.ok(result)
    except ValueError as e:
        return HttpResponse.error(str(e))
    except Exception as e:
        logger.error(f"判卷失败：{str(e)}")
        return HttpResponse.error(f"判卷失败：{str(e)}")
