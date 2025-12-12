import re
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from beanie import PydanticObjectId
from bson.objectid import ObjectId

from models import Evento

################################################################
######################  CRUD BASICO  ###########################

#Método Get que delvuelve un Evento a través de la id.
async def getEvento(eventoID: PydanticObjectId):
    return await Evento.get(eventoID)


#Método Get que devuelve todos los Eventos de un Calendario dado por su id.
async def getEventosCalendario(calendarioID: PydanticObjectId):
    return await Evento.find(Evento.calendario == calendarioID).to_list()

#Método POST que crea un Evento con los parámetros pasados para el calendario del que se pasa la id.
async def crearEvento(titulo: str, hora_comienzo: datetime, hora_fin: datetime, lugar: str, organizador: str, calendario: ObjectId, descripcion: str, lat: float = None, lon: float = None):
        if not titulo or not organizador or not calendario:
            raise HTTPException(status_code=400, detail="Faltan campos obligatorios (titulo, organizador o calendario).")
        if hora_fin < hora_comienzo:
            raise HTTPException(status_code=400, detail="La hora de fin no puede ser anterior a la hora de comienzo.")
        nuevo_evento = Evento(
            titulo=titulo,
            hora_comienzo=hora_comienzo,
            hora_fin=hora_fin,
            lugar=lugar,
            organizador=organizador,
            calendario=calendario,
            descripcion=descripcion,
            lat=lat,
            lon=lon,
        )
        await nuevo_evento.insert()
        return nuevo_evento

# Definición de la lista de los parámetros de Evento que permiten modificación.
Parametros_Actualizables = {"titulo", "hora_comienzo", "hora_fin", "lugar", "descripcion", "lat", "lon"}

#Método PUT que actualiza la información de un evento, solo de los parámetros permitidos.
async def actualizarEvento(evento_id: PydanticObjectId, data: dict):
        evento = await Evento.get(evento_id)
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        if not data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Filtrar solo los modificables
        data_filtrada = {k: v for k, v in data.items() if k in Parametros_Actualizables}

        # Actualizar los valores
        for key, value in data_filtrada.items():
            setattr(evento, key, value)
        await evento.save() 
        return evento

#Método DELETE que elimina el Evento que se pasa por ID 
async def eliminarEvento(eventoID: PydanticObjectId):
    evento = await Evento.get(eventoID)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    await evento.delete()
    return {"detalle": "Evento eliminado correctamente"}
    

################################################################
#################  BUSQUEDAS PARAMETRIZADAS  ###################

#Método Get que devuelve todos los Eventos de un determinado mes para un calendario.
#Se considera dentro del mes todos los eventos cuyo tiempo entre inicio y fin incluya el mes seleccionado. 
async def getEventosCalendarioPorMes(calendarioID: PydanticObjectId, inicio_mes: datetime, fin_mes: datetime): 
    try:
        query = {
            "calendario": calendarioID,
            "hora_fin": {"$gte": inicio_mes},      # termina después del inicio del mes
            "hora_comienzo": {"$lte": fin_mes}     # empieza antes del final del mes
        }

        eventos = await Evento.find_many(query).to_list()

        if not eventos:
            raise HTTPException(status_code=404, detail="No se encontraron eventos para este mes")

        return eventos

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos del mes: {str(e)}")

#Método Get que devuelve todos los Eventos de un determinado dia para un calendario.
#Se considera dentro del dia todos los eventos cuyo tiempo entre inicio y fin incluya el dia seleccionado.    
async def getEventosCalendarioPorDia(calendarioID: PydanticObjectId, fecha: datetime):   
    try:
        # Rango del día (00:00:00 a 23:59:59)
        inicio_dia = datetime(fecha.year, fecha.month, fecha.day, 0, 0, 0)
        fin_dia = inicio_dia + timedelta(days=1) - timedelta(seconds=1)

        query = {
            "calendario": calendarioID,
            "hora_fin": {"$gte": inicio_dia},       # termina después de que empieza el día
            "hora_comienzo": {"$lte": fin_dia}     # empieza antes de que termine el día
        }

        eventos = await Evento.find_many(query).to_list()

        if not eventos:
            raise HTTPException(status_code=404, detail="No se encontraron eventos para ese día.")

        return eventos

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos del día: {str(e)}")

#Método Get que devuelve todos los Eventos cuyo titulo se asemeje al buscado.
async def getEventosPorTitulo(titulo: str):
    eventos = await Evento.find(
            {
                "titulo": {"$regex": titulo, "$options": "i"}
            }
        ).to_list()
    if not eventos:
        raise HTTPException(status_code=404, detail="No se encontraron eventos con ese título")
    return eventos

#Método Get que devuelve todos los Eventos del calendario seleccionado cuyo titulo se asemeje al buscado.
async def getEventosCalendarioPorTitulo(calendarioID: PydanticObjectId, titulo: str):
    try:
        eventos = await Evento.find(
                {
                    "calendario": calendarioID,
                    "titulo": {"$regex": titulo, "$options": "i"}
                }
            ).to_list()
        return eventos
    except HTTPException:
            raise
    except Exception as e:
            raise HTTPException(status_code=500,detail=f"Error al obtener eventos por título: {str(e)}")
  
#Método Get Devuelve todos los Eventos de un Organizador.
async def getEventosPorOrganizador(organizador: str):
    return await Evento.find(Evento.organizador == organizador).to_list()

#Método Get Devuelve todos los Eventos de un Organizador para un mismo calendario.
async def getEventosCalendarioPorOrganizador(calendarioID: PydanticObjectId, organizador):
    try:
        eventos = await Evento.find(
            Evento.calendario == calendarioID,
            Evento.organizador == organizador
        ).to_list()

        if not eventos:
            raise HTTPException(status_code=404, detail="No se encontraron eventos para este organizador en el calendario.")

        return eventos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos por organizador: {str(e)}")

#Método Get Devuelve eventos según los filtros de titulo, organizador, fecha y calendario
async def buscarEventosPorFiltros(
    titulo: Optional[str] = None,
    organizador: Optional[str] = None,
    calendarios: Optional[List] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
):
    try:
        query: dict = {}

        if titulo:
            query["titulo"] = {"$regex": re.escape(titulo), "$options": "i"}

        if organizador:
            query["organizador"] = organizador

        if calendarios:
            ids: List[PydanticObjectId] = []
            for cid in calendarios:
                try:
                    ids.append(PydanticObjectId(cid))
                except Exception:
                    raise HTTPException(status_code=400, detail="ID de calendario invalida en filtros")
            query["calendario"] = ids[0] if len(ids) == 1 else {"$in": ids}

        if desde or hasta:
            def _parse_fecha(val):
                if isinstance(val, datetime):
                    return val
                if val is None:
                    return None
                try:
                    return datetime.fromisoformat(str(val))
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha invalido. Usa YYYY-MM-DD")

            _desde = _parse_fecha(desde) or datetime.min
            _hasta = _parse_fecha(hasta) or datetime.max
            query["$and"] = [
                {"hora_fin": {"$gte": _desde}},
                {"hora_comienzo": {"$lte": _hasta}},
            ]

        return await Evento.find(query).to_list()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la busqueda global: {str(e)}")
