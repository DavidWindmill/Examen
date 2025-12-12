import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Path, Body
from datetime import datetime, timedelta
from services import evento as eventoAPI
from beanie import PydanticObjectId
from models import EventoActualizar, EventoCrear, FiltrosEvento
from bd import init_db
from bson.errors import InvalidId

api = FastAPI()

# Prefijo de la aplicación
path = "/api_eventos/v1"


# Necesario para usar BEANIE
@api.on_event("startup")
async def start_db():
    await init_db()


# ------------------------------------------------------- #
#        Búsqueda global declarada antes de /evento/{id}  #
# ------------------------------------------------------- #
@api.get(path + "/evento/global",
    summary="Búsqueda global de eventos con filtros opcionales",
    description="Devuelve eventos filtrando por texto, organizador, calendarios y rango de fechas.")
async def buscarEventosGlobal(
    query: Optional[str] = Query(None, description="Texto a buscar en el título"),
    organizador: Optional[str] = Query(None, description="ID/nombre del organizador"),
    calendarios: Optional[List[str]] = Query(default=None, description="IDs de calendarios"),
    desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    try:
        calendario_ids = [PydanticObjectId(cid) for cid in calendarios] if calendarios else None
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de calendario inválida")

    def parse_fecha(valor: Optional[str]) -> Optional[datetime]:
        if not valor:
            return None
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    return await eventoAPI.buscarEventosPorFiltros(
        titulo=query,
        organizador=organizador,
        calendarios=calendario_ids,
        desde=parse_fecha(desde),
        hasta=parse_fecha(hasta)
    )


@api.get(path + "/evento/global_v2",
    summary="Búsqueda global V2 de eventos con filtros opcionales",
    description="Alias de /evento/global para evitar conflictos con /evento/{id}.")
async def buscarEventosGlobalV2(
    query: Optional[str] = Query(None, description="Texto a buscar en el título"),
    organizador: Optional[str] = Query(None, description="ID/nombre del organizador"),
    calendarios: Optional[List[str]] = Query(default=None, description="IDs de calendarios"),
    desde: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    return await buscarEventosGlobal(query, organizador, calendarios, desde, hasta)


################################################################
######################  CRUD BASICO  ###########################

#GET EVENTO 
@api.get(path + "/evento/{id}",
    summary="Obtener un Evento por id",
    description="Delvuelve un Evento a través de la id.")
async def getEvento(id: PydanticObjectId):
        evento = await eventoAPI.getEvento(id)
        if evento is None:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return evento

#GET EVENTOS DE UN CALENDARIO
@api.get(path + "/evento/calendario/{id}",
    summary="Obtener todos los Eventos de un calendario",
    description="Devuelve todos los Eventos de un Calendario dado por su id.")
async def getEventosPorCalendario(id: str):
    eventos = await eventoAPI.getEventosCalendario(PydanticObjectId(id))
    if not eventos:
        raise HTTPException(status_code=404, detail="No se han encontrado eventos para este calendario")
    return eventos

#POST CREAR EVENTOS
@api.post(path + "/evento/calendario/{id}",
    summary="Crear Evento",
    description="Crea un Evento para un determinado calendario.")
async def crearEvento(id: PydanticObjectId, evento: EventoCrear = Body(...)):
    nuevo_evento = await eventoAPI.crearEvento(
        titulo=evento.titulo,
        hora_comienzo=evento.hora_comienzo,
        hora_fin=evento.hora_fin,
        lugar=evento.lugar,
        organizador=evento.organizador,
        calendario=id,
        descripcion=evento.descripcion,
        lat=evento.lat,
        lon=evento.lon
    )
    return nuevo_evento

# PUT ACTUALIZAR EVENTO
@api.put(path + "/evento/{id}",
    summary="Actualizar Evento",
    description="Actualiza la información de un evento, aunque solo de los parámetros permitidos.")
async def actualizarEventoEndpoint(
    id: PydanticObjectId = Path(..., description="ID del evento a actualizar"),
    evento_data: EventoActualizar = Body(..., description="Campos a actualizar")
):
    evento_actualizado = await eventoAPI.actualizarEvento(id, evento_data.dict(exclude_unset=True))
    if not evento_actualizado:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento_actualizado

# DELETE ELIMINAR EVENTO
@api.delete(path + "/evento/{id}",
    summary="Eliminar Evento",
    description="Elimina el Evento que se pasa por ID .")
async def eliminarEventoEndpoint(id: str):
    resultado = await eventoAPI.eliminarEvento(PydanticObjectId(id))
    return resultado

################################################################
#################  BÚSQUEDAS PARAMETRIZADAS  ###################

#GET EVENTOS DE UN CALENDARIO POR MES
@api.get(path + "/evento/calendario/{id}/mes/{fecha}",
    summary="Obtener los Eventos de un calendario por mes",
    description="Devuelve todos los Eventos de un determinado mes para un calendario. " \
                "Se considera dentro del mes todos los eventos cuyo tiempo entre inicio y fin incluya el mes seleccionado. El formato de fecha será DD-MM-AAAA")
async def getEventosPorCalendarioYMes(id: str, fecha: str):
    try:
        calendario_id = PydanticObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de calendario inválida")

    try:
        fecha_dt = datetime.strptime(fecha, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use dd-mm-YYYY.")
    
    inicio_mes = datetime(fecha_dt.year, fecha_dt.month, 1)
    if fecha_dt.month == 12:
        fin_mes = datetime(fecha_dt.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        fin_mes = datetime(fecha_dt.year, fecha_dt.month + 1, 1) - timedelta(seconds=1)

    eventos = await eventoAPI.getEventosCalendarioPorMes(calendario_id, inicio_mes, fin_mes)
    return eventos

#GET EVENTOS DE UN CALENDARIO POR DIA
@api.get(
    path + "/evento/calendario/{id}/dia/{fecha}",
    summary="Obtener eventos de un calendario por día",
    description="Devuelve todos los Eventos de un determinado día para un calendario. " \
                "Se considera dentro del dia todos los eventos cuyo tiempo entre inicio y fin incluya el dia seleccionado.")
async def getEventosPorCalendarioYDia(id: str, fecha: str):
    try:
        calendario_id = PydanticObjectId(id)
        fecha_dt = datetime.strptime(fecha, "%d-%m-%Y")
        eventos = await eventoAPI.getEventosCalendarioPorDia(calendario_id, fecha_dt)
        return eventos

    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa DD-MM-YYYY.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los eventos del día: {str(e)}")

#GET EVENTOS POR TITULO
@api.get(path + "/evento/buscar/{titulo}",
    summary="Obtener Eventos por Titulos",
    description="Devuelve todos los Eventos cuyo titulo se asemeje a la búsqueda.")
async def getEventosPorTitulo(titulo: str):
    return await eventoAPI.getEventosPorTitulo(titulo)

#GET EVENTOS DE UN CALENDARIO POR TITULO
@api.get(path + "/evento/calendario/{id}/buscar/{titulo}",
    summary="Obtener Eventos de un calendario por titulo",
    description="Devuelve todos los Eventos asociados a un calendario cuyo titulo se asemeje al de la búsqueda.")
async def getEventosCalendarioPorTitulo(id: str, titulo: str):
    try:
        calendario_id = PydanticObjectId(id)
        eventos = await eventoAPI.getEventosCalendarioPorTitulo(calendario_id, titulo)
        if not eventos:
            raise HTTPException(status_code=404, detail="No se encontraron eventos con ese título en este calendario")
        return eventos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener eventos del calendario por título: {str(e)}"
        )

#GET EVENTOS DE UN ORGANIZADOR
@api.get(path + "/evento/organizador/{organizador}",
    summary="Obtener todos los Eventos de un organizador",
    description="Devuelve todos los Eventos de un Organizador.")
async def getEventosPorOrganizador(organizador: str):
    eventos = await eventoAPI.getEventosPorOrganizador(organizador)
    if not eventos:
        raise HTTPException(status_code=404, detail="No se han encontrado eventos para este usuario")
    return eventos

#GET EVENTOS DE UN ORGANIZADOR PARA UN CALENDARIO
@api.get(path + "/evento/calendario/{id}/organizador/{organizador}",
    summary="Obtener todos los Eventos de un calendario de un organizador",
    description="Devuelve todos los Eventos de un Organizador para un mismo calendario.")
async def getEventosCalendarioPorOrganizador(organizador: str, id: str):
    try:
        calendario_id = PydanticObjectId(id)
        eventos = await eventoAPI.getEventosCalendarioPorOrganizador(calendario_id, organizador)
        return eventos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos: {str(e)}")

#GET EVENTOS SEGÚN FILTROS 
@api.get(path + "/evento/calendario/{id}/organizador/{organizador}",
    summary="Obtener todos los Eventos de un calendario de un organizador",
    description="Devuelve todos los Eventos de un Organizador para un mismo calendario.")
async def getEventosCalendarioPorOrganizador(organizador: str, id: str):
    try:
        calendario_id = PydanticObjectId(id)
        eventos = await eventoAPI.getEventosCalendarioPorOrganizador(calendario_id, organizador)
        return eventos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos: {str(e)}")

#GET EVENTOS POR FILTROS
@api.post(path + "/eventos/filtros")
async def buscarEventosPorFiltros(filtros: FiltrosEvento):
    eventos = await eventoAPI.buscarEventosPorFiltros(
        titulo=filtros.titulo,
        organizador=filtros.organizador,
        calendarios=filtros.calendarios,
        desde=filtros.desde,
        hasta=filtros.hasta
    )
    return eventos
