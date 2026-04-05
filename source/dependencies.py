from source.database import Database
from source.config import Config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = Config(BASE_DIR, "database.json")
db = Database(
    host=config.get_key("host", "127.0.0.1"),
    user=config.get_key("user", "root"),
    password=config.get_key("password", "password"),
    database=config.get_key("database", "database")
)
db.setup()

def get_db() -> Database:
    return db