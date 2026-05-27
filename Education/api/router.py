from Education.api.core.questionApi import router as question_router
from Education.api.core.paperApi import router as paper_router
from Education.api.core.examApi import router as exam_router
from Education.api.core.agentChatApi import router as agent_chat_router
from Education.api.core.userProfileApi import router as user_profile_router


def router_register(app):
    app.include_router(question_router, tags=["教育局项目 - 题目"])
    app.include_router(paper_router, tags=["教育局项目 - 试卷"])
    app.include_router(exam_router, tags=["教育局项目 - 考试"])
    app.include_router(agent_chat_router, tags=["教育局项目 - Agent 聊天"])
    app.include_router(user_profile_router, tags=["教育项目 - 用户画像"])