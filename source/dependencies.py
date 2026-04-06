from source.database import Database
from source.config import Config
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException, Request


BASE_DIR = Path(__file__).resolve().parent.parent

config = Config(BASE_DIR, "database.json")
server_config = Config(BASE_DIR, "server.json")

SECRET_KEY = server_config.get_key("secret_key", "12345")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
db = Database(
    host=config.get_key("host", "127.0.0.1"),
    user=config.get_key("user", "root"),
    password=config.get_key("password", "password"),
    database=config.get_key("database", "database")
)
db.setup()
#db.create_user("root", "root")

def get_db() -> Database:
    return db

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=403, detail="Permiso denegado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=403, detail="Permiso denegado")
        user = db.get_user(username)
        if not user:
            raise HTTPException(status_code=403, detail="Permiso denegado")
        return user
    except JWTError:
        raise HTTPException(status_code=403, detail="Permiso denegado")