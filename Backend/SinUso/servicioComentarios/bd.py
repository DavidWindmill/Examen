from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import models

async def init_db():
    client = AsyncIOMotorClient(
        "mongodb+srv://admin:admin@superbd.bc1ak.mongodb.net/?retryWrites=true&w=majority&appName=SuperBD"
    )
    db = client.Kalendas
    await init_beanie(database=db, document_models=[models.Comentario])
