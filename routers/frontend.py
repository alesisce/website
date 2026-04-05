from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from source.dependencies import get_db

router = APIRouter(tags=["website"]) # sin prefix porque no es necesario si es /
templates = Jinja2Templates(directory="templates") # Para renderizar templates.

@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
        status_code=200
    )

@router.get("/track")
async def track(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context={},
        status_code=200
    )