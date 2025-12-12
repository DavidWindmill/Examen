from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes.rutas_frontend import router as rutas_frontend

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Kalendas API Gateway", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(rutas_frontend)





