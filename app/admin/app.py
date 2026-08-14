from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.service import UserService
from .auth import require_admin
from .dependencies import get_user_service
from app.schemas import UserRead


BASE_DIR = Path(__file__).parent

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates",
)

@app.get('/admin')
async def admin(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    _: str = Depends(require_admin)
):
    raw_users = await user_service.get_users()
    users = [UserRead.model_validate(user, from_attributes=True) for user in raw_users]
    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context={
            "users": users,
        },
    )


