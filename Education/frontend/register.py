# 挂载静态文件
from pathlib import Path

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from fastapi import Request, APIRouter

from fastapi import FastAPI

# 定位当前目录作为模板根路径（如此 需要 .html 文件和当前文件同目录下）
BASE_DIR = Path(__file__).parent

router = APIRouter(prefix="/edu")


def frontend_init(app: FastAPI):
    # 模板配置
    templates = Jinja2Templates(directory=BASE_DIR)

    @router.get("/", response_class=HTMLResponse)
    async def interview_upload_page(request: Request):
        """做题页面"""
        return templates.TemplateResponse("doQuestion.html", {"request": request})

    @router.get("/game", response_class=HTMLResponse)
    async def game_page(request: Request):
        """答题对战游戏页面"""
        return templates.TemplateResponse("questionGame.html", {"request": request})

    # @router.get("/hjkg/game", response_class=HTMLResponse)
    # async def game1_page(request: Request):
    #     """黄金矿工游戏"""
    #     return templates.TemplateResponse("goldMiners.html", {"request": request})

    @router.get("/exam", response_class=HTMLResponse)
    async def exam_page(request: Request):
        """在线考试页面"""
        return templates.TemplateResponse("exam.html", {"request": request})

    @router.get("/exam-result", response_class=HTMLResponse)
    async def exam_result_page(request: Request):
        """考试结果页面"""
        return templates.TemplateResponse("exam_result.html", {"request": request})

    @router.get("/history", response_class=HTMLResponse)
    async def history_page(request: Request):
        """考试历史页面"""
        return templates.TemplateResponse("history.html", {"request": request})

    @router.get("/paper-manager", response_class=HTMLResponse)
    async def paper_manager_page(request: Request):
        """试卷管理页面"""
        return templates.TemplateResponse("paper_manager.html", {"request": request})

    @router.get("/question-manager", response_class=HTMLResponse)
    async def question_manager_page(request: Request):
        """题目管理页面"""
        return templates.TemplateResponse("question_manager.html", {"request": request})

    @router.get("/agent-chat", response_class=HTMLResponse)
    async def agent_chat_page(request: Request):
        """Agent 聊天页面"""
        return templates.TemplateResponse("agentChat.html", {"request": request})

    app.include_router(router, tags=["教育局项目 - 前端"])

    # 挂载静态文件目录
    static_dir = BASE_DIR / "static"
    if static_dir.exists():
        app.mount("/education/static", StaticFiles(directory=str(static_dir)), name="education_static")

        # # 单独挂载 JavaScript 文件目录，便于访问
        # js_dir = static_dir / "js"
        # if js_dir.exists():
        #     app.mount("/education/js", StaticFiles(directory=str(js_dir)), name="education_js")
