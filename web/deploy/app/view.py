import os
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.routing import Router
from loguru import logger
from werkzeug.utils import secure_filename
from jinja2 import Environment, BaseLoader


from . import settings, db, auth
from .db import DB

router = APIRouter(
    prefix="",
    tags=["view"],
)
t = Jinja2Templates(directory=str(settings._base_path / "templates"))


def route_generator(req: Request, base_path="/api") -> Dict[str, str]:
    router: Router = req.scope["router"]
    ret = {}
    for r in router.routes:
        if r.path.startswith(base_path):
            dummy_params = {i: f"NONE_{i}" for i in set(r.param_convertors.keys())}
            ret[r.name] = req.url_for(name=r.name, **dummy_params)
    return ret


def response_generator(
    req: Request,
    filename: str,
    context: dict = {},
    status_code: int = 200,
    headers: dict = None,
    media_type: str = None,
    background=None,
) -> Response:
    context_base = {
        "request": req,
        "api_list": route_generator(req),
    }
    context_base.update(context)
    return t.TemplateResponse(
        name=filename,
        context=context_base,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
        background=background,
    )


async def get_note(user: db.User, note_name: str):
    note_name = secure_filename(note_name)
    username = secure_filename(user.username)
    _p = settings.settings.NOTES_SAVE_BASE_PATH / username
    _p.mkdir(parents=True, exist_ok=True)
    if not (_p / note_name).exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    with open(_p / note_name, "r") as f:
        return f.read()


async def get_note_admin(username: str, note_name: str):
    username = secure_filename(username)
    _p = settings.settings.NOTES_SAVE_BASE_PATH / username
    _p.mkdir(parents=True, exist_ok=True)
    if not (_p / note_name).exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    with open(_p / note_name, "r") as f:
        return f.read()


async def write_note(user: db.User, note_name: str, note_text: str):
    note_name = secure_filename(note_name)
    username = secure_filename(user.username)
    _p = settings.settings.NOTES_SAVE_BASE_PATH / username
    _p.mkdir(parents=True, exist_ok=True)
    with open(_p / note_name, "w") as f:
        f.write(note_text)


@router.get("/")
async def index(
    req: Request,
    resp: Response,
    user: db.User = Depends(auth.get_current_user_safe),
) -> Response:
    logger.info(user)
    return response_generator(
        req,
        "index.jhtml",
        context={
            "user": user,
        },
    )


@router.get("/login")
async def login(req: Request, resp: Response) -> Response:
    return response_generator(req, "login.jhtml")


@router.get("/old_login")
async def old_login(req: Request, resp: Response) -> Response:
    return response_generator(req, "old_login.jhtml")


@router.post("/login")
async def login_post(
    req: Request,
    resp: Response,
    login: str = Form(...),
    password: str = Form(...),
) -> Response:
    if user := await DB().find(login):
        if user.password == password:
            resp = RedirectResponse(req.url_for("index"), status_code=302)
            resp.set_cookie(key="access_token", value=f"Bearer {auth.create_user_token(user)}")
            return resp
        return response_generator(
            req,
            "login.jhtml",
            context={
                "message": "Invalid password",
                "login": login,
                "password": password,
            },
        )
    return response_generator(
        req,
        "login.jhtml",
        context={
            "message": "Invalid login",
            "login": login,
            "password": password,
        },
    )


@router.get("/register")
async def register(req: Request, resp: Response) -> Response:
    return response_generator(req, "register.jhtml")


@router.post("/register")
async def register_post(
    req: Request,
    resp: Response,
    login: str = Form(...),
    password: str = Form(...),
) -> Response:
    if await DB().find(login):
        return response_generator(
            req,
            "register.jhtml",
            context={
                "message": "Invalid login",
                "login": login,
                "password": password,
            },
        )
    user = await DB().register(login, password)
    resp = RedirectResponse(req.url_for("index"), status_code=302)
    resp.set_cookie(key="access_token", value=f"Bearer {auth.create_user_token(user)}")
    return resp


@router.get("/logout")
async def logout(
    req: Request,
    resp: Response,
) -> Response:
    resp = RedirectResponse(req.url_for("index"), status_code=302)
    resp.delete_cookie("access_token")
    return resp


@router.get("/profile")
async def profile(
    req: Request,
    resp: Response,
    user: db.User = Depends(auth.get_current_user),
) -> Response:
    notes = []
    for note_name in user.notes:
        notes.append(await get_note(user, note_name))
    return response_generator(
        req,
        "profile.jhtml",
        context={
            "user": user,
            "notes": notes
        },
    )


@router.post("/profile")
async def profile_post(
    req: Request,
    resp: Response,
    user: db.User = Depends(auth.get_current_user),
    name: str = Form(...),
    text: str = Form(...),
) -> Response:
    if user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    await write_note(user, name, text)
    user.notes.append(name)
    user.notes = list(set(user.notes))
    return response_generator(
        req,
        "profile.jhtml",
        context={
            "user": user,
            "note_name": name,
            "note_text": text,
        },
    )


@router.post("/rprofile")
async def profile_render(
    req: Request,
    resp: Response,
    user: db.User = Depends(auth.get_current_user),
    name: str = Form(...),
    username: str = Form(...),
) -> Response:
    if not user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    note_text = await get_note_admin(username, name)
    rtemplate = Environment(loader=BaseLoader()).from_string(note_text)
    data = rtemplate.render(
        **{
            "user": user,
        }
    )
    return response_generator(
        req,
        "profile.jhtml",
        context={
            "user": user,
            "user_name": username,
            "note_name": name,
            "note_text": data,
        },
    )


# @router.get("/admin")
# async def admin(
#     req: Request,
#     resp: Response,
#     user: db.User = Depends(auth.get_current_user_safe),
# ) -> Response:
#     if user is None or not user.admin:
#         raise HTTPException(403, detail="No")
#     return response_generator(
#         req,
#         "admin.jhtml",
#         context={
#             "user": user,
#         },
#     )


@router.get("/sup3r_s3cur3_s3cr3t_k3y")
async def get_secret_key(req: Request, resp: Response):
    return settings.settings.JWT_SECRET_KEY
