import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.auth import current_user

from app.database import init_db

from app.routes.rutas_frontend import router as rutas_frontend
from app.routes.rutas_reviews import router as rutas_reviews

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("✅ Mongo/Beanie inicializado")
    except Exception:
        logger.exception("❌ Falló init_db()")
        raise
    yield

app = FastAPI(lifespan=lifespan)

# Static (para /static/...)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Frontend (ruta /)
app.include_router(rutas_frontend)
app.include_router(rutas_reviews)

@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"uid": user["uid"], "email": user.get("email"), "name": user.get("name")}

