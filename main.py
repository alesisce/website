from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from source.config import Config
from source.database import Database

import os
import uvicorn

server_path = os.path.abspath(os.path.dirname(__file__))
db_config = Config(server_path, "database.json") # El archivo se crea. Pero no se crean las claves automaticamente.
server_config = Config(server_path, "server.json")
db = Database(
    host = db_config.get_key("host", "127.0.0.1"),
    user = db_config.get_key("user", "root"), # Necesita los permisos SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, CREATE VIEW, EVENT, TRIGGER, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EXECUTE
    password = db_config.get_key("password", "password"),
    database = db_config.get_key("database", "database")
)

#db.setup() # Solo una vez.

app = FastAPI()


# Inicializador --------------------------------------------------
if __name__  == "__main__":
    uvicorn.run(app,
        host=server_config.get_key("host", "0.0.0.0"),
        port=server_config.get_key("port", 80),
        reload=server_config.get_key("reload", True)
    )