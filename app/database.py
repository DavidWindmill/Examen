# app/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_locations import Location

_client: AsyncIOMotorClient | None = None
_initialized = False

async def init_db() -> None:
    global _client, _initialized
    if _initialized:
        return

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("Falta la variable de entorno MONGO_URI")

    # Fail-fast si hay red/allowlist mal
    _client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)

    db_name = os.getenv("MONGO_DB_NAME", "examen")
    # Esto funciona tanto si el URI trae DB como si no
    try:
        db = _client.get_default_database()
    except Exception:
        db = _client[db_name]

    await init_beanie(database=db, document_models=[Location])
    _initialized = True
