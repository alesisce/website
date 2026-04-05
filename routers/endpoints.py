from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from source.dependencies import get_db, Database

router = APIRouter(prefix="/api", tags=["endpoint"])

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
        "track": tracker
    })