from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.rutas_evento import router as rutas_evento
from routes.rutas_calendario import router as rutas_calendario
from routes.rutas_frontend import router as rutas_frontend
from routes.rutas_comentario import router as rutas_comentario

app = FastAPI(title="Kalendas API Gateway", version="1.0.0")

# Configuración de Jinja2 y archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Importante: incluir primero las rutas de API de eventos para que
# las rutas estáticas /evento/global_v2 no choquen con /evento/{evento_id} del frontend.
app.include_router(rutas_evento)
app.include_router(rutas_calendario)
app.include_router(rutas_frontend)
app.include_router(rutas_comentario)




