from fastapi import FastAPI, HTTPException, Response
from models import Calendario, PalabraClave
from beanie import PydanticObjectId, init_beanie
from bd import init_db
from services.calendario import *

app = FastAPI()

@app.on_event("startup")
async def start_db():
    await init_db()

# ------------------------------------------------------- #
#                   Métodos GET                           #
# ------------------------------------------------------- #

@app.get("/api/v1/calendarios", status_code=200)
async def get_calendarios():
    return await getTodosLosCalendarios()

@app.get("/api/v1/calendarios/{id}", status_code=200)
async def get_calendario(id: PydanticObjectId):
    calendario = await getCalendario(id)
    if not calendario:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
    return calendario

@app.get("/api/v1/calendarios/organizador/{organizador}", status_code=200)
async def obtener_calendarios_por_organizador(organizador: str):
    calendario = await getCalendariosPorOrganizador(organizador)
    if not calendario:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
    return calendario

@app.get("/api/v1/calendarios/buscar/{texto}", status_code=200)
async def buscar_calendarios_por_texto(texto: str):
    calendario = await buscarCalendariosPorTexto(texto)
    if not calendario:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
    return calendario

@app.get("/api/v1/calendarios/{id}/cantidad-eventos", status_code=200)
async def obtener_cantidad_eventos_de_calendario(id: PydanticObjectId):
    """
    Devuelve la cantidad de eventos asociados a un calendario.
    """
    resultado = await getCantidadEventosDeCalendario(id)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

@app.get("/api/v1/calendarios/{id}/proximos-eventos", status_code=200)
async def obtener_proximos_eventos_de_calendario(id: PydanticObjectId, limite: int = 10):
    """
    Devuelve los próximos eventos de un calendario (con un limite por si acaso xD).
    """
    resultado = await getProximosEventosDeCalendario(id, limite)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

# ------------------------------------------------------- #
#                   Métodos POST                          #
# ------------------------------------------------------- #

@app.post("/api/v1/calendarios", status_code=201)
async def crear_calendario(payload: Calendario):
    calendario = await crearCalendario(
        titulo=payload.titulo,
        organizador=payload.organizador,
        palabras_claves=payload.palabras_claves
    )
    return calendario

@app.post("/api/v1/calendarios/{id}/palabras-claves")
async def añadir_palabra_clave(id: PydanticObjectId, payload: PalabraClave):
    resultado = await añadirPalabraClaveACalendario(id, payload.palabra_clave)
    if isinstance(resultado, dict) and "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado


# ------------------------------------------------------- #
#                   Métodos PUT                           #
# ------------------------------------------------------- #

@app.put("/api/v1/calendarios/{id}")
async def actualizar_calendario(id: PydanticObjectId, calendario: dict):
    resultado = await actualizarCalendario(id, calendario)
    if isinstance(resultado, dict) and "error" in resultado:
        raise HTTPException(status_code=resultado["codigo_respuesta"], detail=resultado["error"])
    return resultado
    

# ------------------------------------------------------- #
#                   Métodos DELETE                        #
# ------------------------------------------------------- #

@app.delete("/api/v1/calendarios/{id}", status_code=200)
async def eliminar_calendario(id: PydanticObjectId):
    calendario_existente = await getCalendario(id)
    if not calendario_existente:
        raise HTTPException(status_code=404, detail="Calendario no encontrado")
    await eliminarCalendario(id)
    return {"status_code": 200}

@app.delete("/api/v1/calendarios/{id}/palabras-claves")
async def eliminar_palabra_clave(id: PydanticObjectId, payload: PalabraClave):
    resultado = await eliminarPalabraClaveDeCalendario(id, payload.palabra_clave)
    if isinstance(resultado, dict) and "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado