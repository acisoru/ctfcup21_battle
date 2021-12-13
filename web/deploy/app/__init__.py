from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from . import settings, view

app = FastAPI(
    docs_url="/h1dd3n_docs",
    redoc_url="/h1dd3n_redoc",
    openapi_url="/h1dd3n_opeapi.json",
)

app.include_router(view.router)

app.mount("/static", StaticFiles(directory=str(settings._base_path / "static")), name="static")
