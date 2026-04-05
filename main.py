from fastapi import FastAPI
from source.config import Config
from routers import frontend
import os
import uvicorn

server_path = os.path.abspath(os.path.dirname(__file__))
server_config = Config(server_path, "server.json")
app = FastAPI()

# Incluir routers
app.include_router(frontend.router)

# Inicializador --------------------------------------------------
if __name__  == "__main__":
    uvicorn.run("main:app",
        host=server_config.get_key("host", "0.0.0.0"),
        port=server_config.get_key("port", 80),
        reload=server_config.get_key("reload", True)
    )