from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from source.dependencies import get_db, Database, get_current_user
from source.config import Config
from source.basemodels import APILogin, ModifyProject, CreateProject
from datetime import datetime, timedelta
from jose import jwt
import pathlib, string, random

router = APIRouter(prefix="/api", tags=["endpoint"])
server_config = Config(pathlib.Path(__file__).resolve().parent.parent, "server.json")

def create_access_token(username: str, expires_minutes: int = 60 * 24) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now() + timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, server_config.get_key("secret_key", "secret"), algorithm="HS256")

@router.get("/get_project/{track_id}")
async def get_project_endpoint(track_id: str, db: Database = Depends(get_db)):
    """
    Este endpoint devuelve:
    {
        "id": int,
        "name": str,
        "project_author_id": str,
        "project_track_id": str,
        "project_description": str,
        "project_status": str,
        "project_priority": int,
        "milestones": Dict[str, bool] | None,
        "overall_progress": int,
        "last_update": datetime
    }

    o codigo 404 si no existe.
    """
    tracker = db.get_project_by_track_id(track_id)
    if not tracker:
        return JSONResponse({
            "message": "No project found"
        }, status_code=404)
    return JSONResponse({
        "track": jsonable_encoder(tracker)
    })

@router.post("/login")
async def login(data: APILogin, db: Database = Depends(get_db)):
    user = db.get_user(data.username)

    if not user or not db.verify_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data.username)

    res = JSONResponse({"ok": True})
    res.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return res

@router.post("/logout")
async def logout(response: Response):
    response = JSONResponse({"ok": True})
    response.delete_cookie("access_token")
    return response

@router.get("/get_projects")
async def get_projects(user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    return db.get_projects() # Es devuelve una lista con todos los datos.

@router.post("/modify_project/{id}")
async def modify_project(data: ModifyProject, id: int, user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    db.update_milestones(id, data.milestones)
    db.update_progress(id, data.progress)
    db.update_priority(id, data.priority)
    db.update_status(id, data.status)
    db.update_description(id, data.description)

@router.delete("/delete_project/{id}")
async def delete_project(id: int, user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    return db.delete_project(id)

@router.put("/create_project")
async def create_project(data: CreateProject, user: dict = Depends(get_current_user), db: Database = Depends(get_db)):
    projid = db.create_project(
        name=data.name,
        author_id=data.author,
        track_id=f"ALX-{"".join(random.choices(string.ascii_lowercase, k=4)).upper()}-{"".join(random.choices(string.ascii_lowercase, k=4)).upper()}",
        description=data.description,
        status=data.status,
        priority=data.priority,
        milestones=data.milestones
    )

    if not projid:
        raise HTTPException(500, "Internal Server Error.")
    return db.get_project_by_id(projid)