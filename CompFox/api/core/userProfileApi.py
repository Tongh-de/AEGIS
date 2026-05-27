import logging
from typing import Optional
from fastapi import APIRouter, Query

from Base.RicUtils.httpUtils import HttpResponse
from CompFox.services.userProfileService import get_user_profile_service
from CompFox.models.pojo.userProfilePo import UserProfilePo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compfox/user/profile")


@router.get("")
def get_user_profile(
    user_id: str = Query(..., description="用户 ID"),
):
    """
    获取员工合规画像

    Args:
        user_id: 员工 ID

    Returns:
        员工合规画像信息
    """
    try:
        service = get_user_profile_service()
        profile = service.get_profile(user_id)
        return HttpResponse.ok(profile.mini_dict)
    except Exception as e:
        logger.error(f"获取用户画像失败：{str(e)}")
        return HttpResponse.error(f"获取用户画像失败：{str(e)}")


@router.get("/detail")
def get_user_profile_detail(
    user_id: str = Query(..., description="用户 ID"),
):
    """
    获取用户画像详情（包含完整统计信息）

    Args:
        user_id: 用户 ID

    Returns:
        用户画像详情
    """
    try:
        profile = UserProfilePo.get_or_create(user_id)
        return HttpResponse.ok({
            'basic_info': {
                'user_id': profile.user_id,
                'nickname': profile.nickname,
                'avatar_url': profile.avatar_url,
                'grade_type': profile.grade_type,
                'grade_level': profile.grade_level,
                'preferred_subject': profile.preferred_subject,
            },
            'learning_stats': {
                'total_questions': profile.total_questions,
                'total_correct': profile.total_correct,
                'overall_correct_rate': profile.overall_correct_rate,
                'total_practice_time': profile.total_practice_time,
                'continuous_days': profile.continuous_days,
                'last_practice_date': profile.last_practice_date,
            },
            'subject_stats': profile.subject_stats_dict,
            'knowledge_mastery': profile.knowledge_mastery_dict,
            'weak_points': profile.weak_points_list,
            'ability_dimensions': profile.ability_dimensions_dict,
            'chat_profile': profile.chat_profile_dict,
            'intent_stats': profile.intent_stats_dict,
            'learning_goal': profile.learning_goal,
            'target_score': profile.target_score,
            'ai_summary': profile.ai_summary,
        })
    except Exception as e:
        logger.error(f"获取用户画像详情失败：{str(e)}")
        return HttpResponse.error(f"获取用户画像详情失败：{str(e)}")


@router.get("/report")
def get_learning_report(
    user_id: str = Query(..., description="用户 ID"),
    time_range: str = Query("本周", description="时间范围：今天 | 本周 | 本月 | 全部"),
):
    """
    获取合规培训报告

    Args:
        user_id: 员工 ID
        time_range: 时间范围

    Returns:
        合规培训报告
    """
    try:
        service = get_user_profile_service()
        report = service.get_learning_report(user_id, time_range)
        return HttpResponse.ok(report)
    except Exception as e:
        logger.error(f"获取培训报告失败：{str(e)}")
        return HttpResponse.error(f"获取培训报告失败：{str(e)}")


@router.get("/recommendations")
def get_recommendations(
    user_id: str = Query(..., description="用户 ID"),
    limit: int = Query(5, description="推荐数量"),
):
    """
    获取个性化合规考题推荐

    Args:
        user_id: 用户 ID
        limit: 推荐数量

    Returns:
        推荐考题列表
    """
    try:
        service = get_user_profile_service()
        recommendations = service.get_recommendations(user_id, limit)
        return HttpResponse.ok(recommendations)
    except Exception as e:
        logger.error(f"获取推荐题目失败：{str(e)}")
        return HttpResponse.error(f"获取推荐题目失败：{str(e)}")


@router.get("/analysis")
def get_user_analysis(
    user_id: str = Query(..., description="用户 ID"),
):
    """
    获取员工合规行为分析

    Args:
        user_id: 用户 ID

    Returns:
        合规行为分析结果
    """
    try:
        service = get_user_profile_service()
        analysis = service.analyze_user_behavior(user_id)
        return HttpResponse.ok(analysis)
    except Exception as e:
        logger.error(f"获取用户行为分析失败：{str(e)}")
        return HttpResponse.error(f"获取用户行为分析失败：{str(e)}")


@router.post("/refresh-summary")
def refresh_ai_summary(
    user_id: str = Query(..., description="用户 ID"),
):
    """
    刷新 AI 合规画像总结

    Args:
        user_id: 用户 ID

    Returns:
        AI 生成的合规画像总结
    """
    try:
        service = get_user_profile_service()
        summary = service.refresh_ai_summary(user_id)
        return HttpResponse.ok({'ai_summary': summary})
    except Exception as e:
        logger.error(f"刷新 AI 画像总结失败：{str(e)}")
        return HttpResponse.error(f"刷新 AI 画像总结失败：{str(e)}")


@router.post("/update/practice")
def update_profile_from_practice(
    user_id: str = Query(..., description="用户 ID"),
    answer_id: Optional[int] = Query(None, description="答题记录 ID"),
    question_id: Optional[str] = Query(None, description="题目 ID"),
    is_correct: Optional[bool] = Query(None, description="是否正确"),
):
    """
    根据答题记录更新员工合规画像

    Args:
        user_id: 用户 ID
        answer_id: 答题记录 ID
        question_id: 题目 ID
        is_correct: 是否正确

    Returns:
        更新结果
    """
    try:
        service = get_user_profile_service()
        service.update_profile_from_practice(
            user_id=user_id,
            answer_id=answer_id,
            question_id=question_id,
            is_correct=is_correct
        )
        return HttpResponse.ok({'message': '用户画像已更新'})
    except Exception as e:
        logger.error(f"更新用户画像失败：{str(e)}")
        return HttpResponse.error(f"更新用户画像失败：{str(e)}")


@router.post("/update/chat")
def update_profile_from_chat(
    user_id: str = Query(..., description="用户 ID"),
    intent: str = Query(..., description="意图类型"),
    question: Optional[str] = Query(None, description="用户问题"),
):
    """
    根据聊天记录更新员工合规画像

    Args:
        user_id: 用户 ID
        intent: 意图类型
        question: 用户问题

    Returns:
        更新结果
    """
    try:
        service = get_user_profile_service()
        service.update_profile_from_chat(
            user_id=user_id,
            intent=intent,
            question=question
        )
        return HttpResponse.ok({'message': '用户聊天画像已更新'})
    except Exception as e:
        logger.error(f"更新聊天画像失败：{str(e)}")
        return HttpResponse.error(f"更新聊天画像失败：{str(e)}")


def register_user_profile_router(app):
    """注册用户画像路由"""
    app.include_router(router, tags=["CompFox - 员工合规画像"])
