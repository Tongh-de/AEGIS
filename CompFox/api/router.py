from CompFox.api.core.questionApi import router as question_router
from CompFox.api.core.paperApi import router as paper_router
from CompFox.api.core.examApi import router as exam_router
from CompFox.api.core.agentChatApi import router as agent_chat_router
from CompFox.api.core.userProfileApi import router as user_profile_router
from CompFox.api.core.knowledgeApi import router as knowledge_router
from CompFox.api.core.evaluationApi import router as evaluation_router


def router_register(app):
    app.include_router(question_router, tags=["CompFox - 合规题库"])
    app.include_router(paper_router, tags=["CompFox - 合规试卷"])
    app.include_router(exam_router, tags=["CompFox - 合规考核"])
    app.include_router(agent_chat_router, tags=["CompFox - 合规助手"])
    app.include_router(user_profile_router, tags=["CompFox - 员工合规画像"])
    app.include_router(knowledge_router, tags=["CompFox - 合规知识库"])
    app.include_router(evaluation_router, tags=["CompFox - RAG 评测"])