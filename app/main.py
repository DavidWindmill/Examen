from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from app.database import init_db

from app.firebase_admin import verify_id_token
from app.routes.rutas_frontend import router as rutas_frontend
from app.routes.rutas_locations import router as rutas_locations

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent      # .../app
STATIC_DIR = BASE_DIR / "static"               # .../app/static

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
async def startup():
    await init_db()

# Static (para /static/...)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Frontend (ruta /)
app.include_router(rutas_frontend)
app.include_router(rutas_locations)

bearer = HTTPBearer()

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return verify_id_token(creds.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"uid": user["uid"], "email": user.get("email"), "name": user.get("name")}

