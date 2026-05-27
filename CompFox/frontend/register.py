# 挂载静态文件
from pathlib import Path

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from fastapi import Request, APIRouter

from fastapi import FastAPI

# 定位当前目录作为模板根路径（如此 需要 .html 文件和当前文件同目录下）
BASE_DIR = Path(__file__).parent

router = APIRouter(prefix="/compfox")


def frontend_init(app: FastAPI):
    # 模板配置
    templates = Jinja2Templates(directory=BASE_DIR)

    @router.get("/", response_class=HTMLResponse)
    async def interview_upload_page(request: Request):
        """合规练习页面"""
        return templates.TemplateResponse("doQuestion.html", {"request": request})

    @router.get("/game", response_class=HTMLResponse)
    async def game_page(request: Request):
        """合规答题对战页面"""
        return templates.TemplateResponse("questionGame.html", {"request": request})

    # @router.get("/hjkg/game", response_class=HTMLResponse)
    # async def game1_page(request: Request):
    #     """黄金矿工游戏"""
    #     return templates.TemplateResponse("goldMiners.html", {"request": request})

    @router.get("/exam", response_class=HTMLResponse)
    async def exam_page(request: Request):
        """在线合规考核页面"""
        return templates.TemplateResponse("exam.html", {"request": request})

    @router.get("/exam-result", response_class=HTMLResponse)
    async def exam_result_page(request: Request):
        """考核结果页面"""
        return templates.TemplateResponse("exam_result.html", {"request": request})

    @router.get("/history", response_class=HTMLResponse)
    async def history_page(request: Request):
        """考核历史页面"""
        return templates.TemplateResponse("history.html", {"request": request})

    @router.get("/paper-manager", response_class=HTMLResponse)
    async def paper_manager_page(request: Request):
        """合规试卷管理页面"""
        return templates.TemplateResponse("paper_manager.html", {"request": request})

    @router.get("/question-manager", response_class=HTMLResponse)
    async def question_manager_page(request: Request):
        """合规题库管理页面"""
        return templates.TemplateResponse("question_manager.html", {"request": request})

    @router.get("/agent-chat", response_class=HTMLResponse)
    async def agent_chat_page(request: Request):
        """合规助手页面"""
        return templates.TemplateResponse("agentChat.html", {"request": request})

    @router.get("/knowledge-manager", response_class=HTMLResponse)
    async def knowledge_manager_page(request: Request):
        """知识库管理页面"""
        return templates.TemplateResponse("knowledge_manager.html", {"request": request})

    app.include_router(router, tags=["CompFox - 前端"])

    # 挂载静态文件目录
    static_dir = BASE_DIR / "static"
    if static_dir.exists():
        app.mount("/compfox/static", StaticFiles(directory=str(static_dir)), name="compfox_static")

        # # 单独挂载 JavaScript 文件目录，便于访问
        # js_dir = static_dir / "js"
        # if js_dir.exists():
        #     app.mount("/compfox/js", StaticFiles(directory=str(js_dir)), name="compfox_js")
