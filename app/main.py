from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from app.routes.rutas_frontend import router as rutas_frontend
from app.routes.rutas_locations import router as rutas_locations
from app.database import init_db
from app.auth import current_user

app = FastAPI(title="Mapa de viajes", version="1.0.0")

# Static (para /static/...)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Frontend (ruta /)
app.include_router(rutas_frontend)
app.include_router(rutas_locations)

@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"uid": user["uid"], "email": user.get("email"), "name": user.get("name")}


@app.on_event("startup")
async def _startup():
    # Inicializa Beanie + MongoDB usando MONGO_URI (Vercel env)
    await init_db()

