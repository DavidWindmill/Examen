import os
import httpx
import services.mapa as MapaService
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from datetime import date, datetime
router = APIRouter(tags=["Frontend"])

templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------- #
#                   Rutas del Frontend                    #
# ------------------------------------------------------- #

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse("mapa.html", {
         "request": request,
    })
