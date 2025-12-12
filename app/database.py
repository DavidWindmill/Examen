import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models_locations import Location


async def init_db() -> None:
    """Inicializa la conexión a MongoDB y registra los modelos Beanie.

    Requiere la variable de entorno MONGO_URI (por ejemplo en Vercel).
    """

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("Falta la variable de entorno MONGO_URI")

    client = AsyncIOMotorClient(mongo_uri)

    # Si el URI incluye nombre de base de datos (....mongodb.net/<DB>?...)
    # get_default_database() funciona. Si NO incluye DB (caso típico), usamos
    # MONGO_DB_NAME o un valor por defecto.
    try:
        db = client.get_default_database()
    except Exception:
        db_name = os.getenv("MONGO_DB_NAME", "examen")
        db = client[db_name]

    await init_beanie(database=db, document_models=[Location])
