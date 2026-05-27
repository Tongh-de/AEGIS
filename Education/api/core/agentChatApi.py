import json
from typing import AsyncGenerator
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from Base.RicUtils.httpUtils import HttpResponse
from Education.models.pojo.agentChatBo import AgentChatParams
from Education.services.agentChatService import get_agent_chat_service

logger = logging.getLogger(__name__)
logger.info("agentChatApi 模块已加载")


router = APIRouter(prefix="/edu/agent")


@router.post("/chat")
async def agent_chat(params: AgentChatParams):
    """
    小 e 做题 Agent 聊天接口

    支持多种意图：
    - generate_question: 出题
    - judge_answer: 判题
    - explain_question: 题目解析
    - chat: 学习聊天
    - recommend_questions: 推荐题目
    - learning_progress: 学习进度查询

    特性：
    - 支持流式输出（is_stream=True）
    - 支持思考模式（is_thinking=True）
    - 自动持久化会话记录（Service 层处理）
    """
    logger.info(f"agent_chat 被调用，params: question={params.question[:20]}..., is_stream={params.is_stream}")
    service = get_agent_chat_service()

    result = await service.handle_request(
        user_input=params.question,
        user_id=params.user_id,
        session_id=params.session_id,
        is_stream=params.is_stream,
        is_thinking=params.is_thinking,
        current_question_id=params.current_question_id,
        current_question_text=params.current_question_text
    )

    logger.info(f"agent_chat 拿到 result，类型：{type(result)}")

    if params.is_stream:
        logger.info("agent_chat: 返回流式响应")
        # 直接返回流式响应
        return StreamingResponse(
            _stream_to_generator(result, params.is_thinking),
            media_type="text/event-stream"
        )
    else:
        logger.info("agent_chat: 返回非流式响应")
        return HttpResponse.ok(result)


async def _stream_to_generator(result, is_thinking: bool = False) -> AsyncGenerator:
    """
    将流式结果转换为 SSE 流生成器

    Args:
        result: 处理结果（AsyncGenerator 或 dict）
        is_thinking: 是否思考模式
    """
    logger.info(f"_stream_to_generator: 开始，result 类型：{type(result)}")
    if isinstance(result, AsyncGenerator):
        logger.info("_stream_to_generator: result 是 AsyncGenerator，开始迭代")
        # 真正的流式输出
        async for chunk in result:
            logger.debug(f"_stream_to_generator: 收到 chunk: {chunk.get('type', 'unknown')}")
            sse_data = f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield sse_data.encode("utf-8")
        logger.info("_stream_to_generator: 迭代完成")
    else:
        logger.info(f"_stream_to_generator: result 不是 AsyncGenerator，类型：{type(result)}")
        # 降级为非流式：直接返回完整结果
        if is_thinking:
            yield {
                'type': 'reasoning',
                'content': '正在分析您的问题...'
            }
        yield {
            'type': 'content',
            'content': result.get('answer', '') if isinstance(result, dict) else str(result)
        }


@router.get("/intents")
def get_intent_types():
    """
    获取支持的意图类型列表
    """
    return HttpResponse.ok({
        'intents': [
            {
                'type': 'generate_question',
                'name': '出题',
                'description': '根据用户需求生成题目',
                'params': ['subject', 'grade_type', 'question_type', 'difficulty_level', 'knowledge_points']
            },
            {
                'type': 'judge_answer',
                'name': '判题',
                'description': 'AI 判题并提供解析',
                'params': ['question_id', 'answer']
            },
            {
                'type': 'explain_question',
                'name': '题目解析',
                'description': '提供题目详细解析',
                'params': ['question_id', 'question_text']
            },
            {
                'type': 'chat',
                'name': '学习聊天',
                'description': '学习相关的普通对话',
                'params': ['topic']
            },
            {
                'type': 'recommend_questions',
                'name': '推荐题目',
                'description': '根据学习情况推荐练习题',
                'params': ['subject', 'weak_points']
            },
            {
                'type': 'learning_progress',
                'name': '学习进度',
                'description': '查询学习进度和统计',
                'params': ['subject', 'time_range']
            }
        ]
    })


def register_agent_chat_router(app):
    """注册 Agent 聊天路由"""
    app.include_router(router, tags=["教育项目 - Agent 聊天"])
