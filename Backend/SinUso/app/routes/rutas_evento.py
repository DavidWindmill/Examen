from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body, File, Query, UploadFile
from models import FiltrosEvento
import services.evento as EventoService
import services.imagenes as ImagenesService
import services.calendario as calendarioService
import os
import tempfile

router = APIRouter(prefix="/evento", tags=["Eventos"])

# ------------------------------------------------------- #
#                   Endpoints CRUD Eventos                #
# ------------------------------------------------------- #
@router.get("/calendario/{calendario_id}/")
async def getEventosCalendario(calendario_id: str):
    """Devuelve los eventos de un calendario"""
    resultado = await EventoService.get_eventos_por_calendario(calendario_id)
    return resultado

@router.get("/{evento_id}/")
async def getEvento(evento_id: str):
    """Devuelve un evento"""
    resultado = await EventoService.get_evento_id(evento_id)
    return resultado

@router.put("/evento/{evento_id}/")
async def crearEvento(evento_id: str, evento_data: dict = Body(...)):
    """Crea un nuevo evento"""
    resultado = await EventoService.crearEvento(evento_id, evento_data)
    return resultado

@router.post("/calendario/{calendario_id}/")
async def crearEvento(calendario_id: str, evento_data: dict = Body(...)):
    """Crea un nuevo evento"""
    resultado = await EventoService.crearEvento(calendario_id, evento_data)
    return resultado


# ------------------------------------------------------- #
#                Endpoints Búsquedas Eventos              #
# ------------------------------------------------------- #

# Gateway alternativo para búsqueda combinada de calendarios y eventos
@router.get("/global_v2")
async def busqueda_global_v2(
    query: Optional[str] = Query(None, description="Texto a buscar en titulo"),
    organizador: Optional[str] = Query(None, description="Organizador/Creador"),
    calendarios: Optional[List[str]] = Query(default=None, description="IDs de calendarios (solo eventos)"),
    desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD, eventos)"),
    hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD, eventos)"),
):
    """
    Busca calendarios y eventos usando los servicios del gateway
    sin depender del endpoint /evento/global del microservicio.
    """
    return await _buscar_global_combined(query, organizador, calendarios, desde, hasta)

#GET EVENTOS DE UN CALENDARIO POR MES
@router.get("/calendario/{calendario_id}/mes/{fecha}") 
async def getEventosCalendarioPorMes(calendario_id: str, fecha: str):
    """Devuelve todos los eventos de un calendario de un determinado mes"""
    resultado = await EventoService.get_eventos_por_calendario_y_mes(calendario_id, fecha)
    return resultado

#GET EVENTOS DE UN CALENDARIO POR DIA
@router.get("/calendario/{calendario_id}/dia/{fecha}") 
async def getEventosCalendarioPorDia(calendario_id: str, fecha: str):
    """Devuelve todos los eventos de un calendario de un determinado dia"""
    resultado = await EventoService.getEventosCalendarioPorDia(calendario_id, fecha)
    return resultado

#GET EVENTOS POR TITULO
@router.get("/titulo/{titulo}") 
async def getEventosPorTitulo(titulo: str):
    """Devuelve eventos según un titulo"""
    resultado = await EventoService.getEventosPorTitulo(titulo)
    return resultado

#GET EVENTOS DE UN CALENDARIO POR TITULO
@router.get("calendario/{calendario_id}/titulo/{titulo}") 
async def getEventosPorTitulo(calendario_id: str, titulo: str):
    """Devuelve eventos según un titulo"""
    resultado = await EventoService.getEventosCalendarioPorTitulo(calendario_id, titulo)
    return resultado

#GET EVENTOS DE UN ORGANIZADOR
@router.get("/organizador/{organizador}") 
async def getEventosPorTitulo(organizador: str):
    """Devuelve eventos según un organizador"""
    resultado = await EventoService.getEventosPorOrganizador(organizador)
    return resultado

#GET EVENTOS DE UN ORGANIZADOR
@router.get("/calendario/{calendario_id}/organizador/{organizador}") 
async def getEventosPorTitulo(calendario_id: str, organizador: str):
    """Devuelve eventos según un organizador"""
    resultado = await EventoService.getEventosCalendarioPorOrganizador(calendario_id, organizador)
    return resultado

# ------------------------------------------------------- #
#                   Endpoints de Imagenes                 #
# ------------------------------------------------------- #

@router.post("/{evento_id}/upload-image")
async def subir_imagen_evento(evento_id: str, file: UploadFile = File(...)):
    """Sube una imagen para un evento y devuelve la URL"""
    try:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        if not file.filename:
            raise HTTPException(status_code=400, detail="El archivo debe tener un nombre")

        suffix = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            ruta_dropbox = f"kalendas/eventos/{evento_id}/{file.filename}"
            url_imagen = ImagenesService.subir_imagen_dropbox(temp_path, ruta_dropbox)

            if url_imagen:
                return {"success": True, "url": url_imagen, "ruta": ruta_dropbox}
            raise HTTPException(status_code=500, detail="Error al subir la imagen a Dropbox")
        finally:
            os.unlink(temp_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")


@router.get("/{evento_id}/imagenes")
async def listar_imagenes_evento(evento_id: str):
    """Lista todas las imagenes de un evento"""
    try:
        carpeta = f"kalendas/eventos/{evento_id}"
        imagenes = ImagenesService.listar_imagenes_dropbox(carpeta)
        imagenes_con_url = []
        for img in imagenes:
            url = ImagenesService.obtener_enlace_imagen(img["ruta"])
            if url:
                img["url"] = url
                imagenes_con_url.append(img)
        return {"success": True, "imagenes": imagenes_con_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imagenes: {str(e)}")

@router.delete("/imagen")
async def eliminar_imagen(ruta: str):
    """Elimina una imagen de Dropbox"""
    try:
        resultado = ImagenesService.eliminar_imagen_dropbox(ruta)
        if resultado:
            return {"success": True, "message": "Imagen eliminada correctamente"}
        raise HTTPException(status_code=500, detail="Error al eliminar la imagen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
   
##################################################################
# Lógica compartida para búsquedas combinadas (calendarios + eventos)
##################################################################
async def _buscar_global_combined(
    query: Optional[str],
    organizador: Optional[str],
    calendarios: Optional[List[str]],
    desde: Optional[str],
    hasta: Optional[str],
):
    # Calendarios por texto
    calendarios_result: list = []
    if query:
        try:
            calendarios_result = await calendarioService.buscar_calendarios(query=query)
        except HTTPException:
            calendarios_result = []

    # Calendarios por organizador/creador
    if organizador:
        try:
            encontrados = await calendarioService.buscar_calendarios(query=organizador)
        except HTTPException:
            encontrados = []

        # Unir resultados sin duplicar, normalizando el _id
        def norm_id(val):
            if isinstance(val, dict) and "$oid" in val:
                return val["$oid"]
            return str(val) if val is not None else None

        indexados = {}
        for cal in calendarios_result or []:
            if isinstance(cal, dict):
                cid = norm_id(cal.get("_id"))
                if cid:
                    cal["_id"] = cid
                    indexados[cid] = cal

        for cal in encontrados or []:
            if isinstance(cal, dict):
                cid = norm_id(cal.get("_id"))
                if cid and cid not in indexados:
                    cal["_id"] = cid
                    indexados[cid] = cal

        calendarios_result = list(indexados.values()) if indexados else []

    # IDs de calendario para filtrar eventos: solo los que selecciona el usuario
    calendarios_ids = calendarios if calendarios else None

    filtros = FiltrosEvento(
        titulo=query,
        organizador=organizador,
        calendarios=calendarios_ids,
        desde=desde,
        hasta=hasta,
    )

    try:
        eventos = await EventoService.buscarEventosPorFiltros(filtros)
    except HTTPException:
        eventos = []

    return {"calendarios": calendarios_result, "eventos": eventos}

