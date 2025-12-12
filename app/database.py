import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_locations import Location

async def init_db():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("Falta MONGO_URI")

    client = AsyncIOMotorClient(
        mongo_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
    )

    await client.admin.command("ping")  # fail-fast

    db_name = os.getenv("MONGO_DB_NAME", "examen")
    try:
        db = client.get_default_database()
    except Exception:
        db = client[db_name]

    await init_beanie(database=db, document_models=[Location])
