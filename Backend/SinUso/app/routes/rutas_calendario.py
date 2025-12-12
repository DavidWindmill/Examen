import os
from fastapi import APIRouter, HTTPException, Query
import httpx
import services.calendario as CalendarioService

router = APIRouter(prefix="/calendario", tags=["Calendarios"])


# ------------------------------------------------------- #
#                   Endpoints de Calendario               #
# ------------------------------------------------------- #

from fastapi import Form
from fastapi.responses import RedirectResponse

@router.post("/crear")
async def crear_calendario_endpoint(titulo: str = Form(...), organizador: str = Form(...)):
    """Crea un nuevo calendario"""
    try:
        await CalendarioService.crear_calendario(titulo, organizador)
        return RedirectResponse(url="/calendarios", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{calendario_id}")
async def eliminar_calendario_endpoint(calendario_id: str):
    """Elimina un calendario"""
    try:
        await CalendarioService.eliminar_calendario(calendario_id)
        return {"success": True, "message": "Calendario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{calendario_id}/titulo")
async def actualizar_titulo_endpoint(calendario_id: str, titulo: str = Form(...)):
    """Actualiza el título de un calendario"""
    try:
        await CalendarioService.actualizar_calendario(calendario_id, {"titulo": titulo})
        return RedirectResponse(url=f"/calendario/{calendario_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{calendario_id}")
async def actualizar_calendario_endpoint(
    calendario_id: str, 
    titulo: str = Form(...), 
    organizador: str = Form(...)
):
    """Actualiza título y organizador de un calendario"""
    try:
        await CalendarioService.actualizar_calendario(
            calendario_id, 
            {"titulo": titulo, "organizador": organizador}
        )
        return {"success": True, "message": "Calendario actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{calendario_id}/add-tag")
async def añadir_tag_endpoint(calendario_id: str, tag: str = Form(...)):
    """Añade una palabra clave a un calendario"""
    try:
        await CalendarioService.añadir_palabra_clave(calendario_id, tag)
        return RedirectResponse(url=f"/calendario/{calendario_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{calendario_id}/remove-tag")
async def eliminar_tag_endpoint(calendario_id: str, tag: str = Form(...)):
    """Elimina una palabra clave de un calendario"""
    try:
        # Get current calendar
        async with httpx.AsyncClient() as client:
            CALENDARIO_SERVICE_URL = os.getenv('CALENDARIO_SERVICE_URL', 'http://localhost:8002')
            cal_response = await client.get(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}")
            cal_response.raise_for_status()
            calendario = cal_response.json()
        
        # Remove tag from list
        if calendario.get('palabras_claves') and tag in calendario['palabras_claves']:
            palabras_claves = [t for t in calendario['palabras_claves'] if t != tag]
            await CalendarioService.actualizar_calendario(calendario_id, {"palabras_claves": palabras_claves})
        
        return RedirectResponse(url=f"/calendario/{calendario_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------- #
#          Endpoints de Estadísticas de Calendario       #
# ------------------------------------------------------- #

@router.get("/{calendario_id}/cantidad-eventos")
async def obtener_cantidad_eventos(calendario_id: str):
    """Obtiene la cantidad de eventos de un calendario"""
    try:
        resultado = await CalendarioService.get_cantidad_eventos_calendario(calendario_id)
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cantidad de eventos: {str(e)}")

@router.get("/{calendario_id}/proximos-eventos")
async def obtener_proximos_eventos(calendario_id: str, limite: int = Query(5, ge=1, le=50)):
    """Obtiene los próximos eventos de un calendario"""
    try:
        resultado = await CalendarioService.get_proximos_eventos_calendario(calendario_id, limite)
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener próximos eventos: {str(e)}")

