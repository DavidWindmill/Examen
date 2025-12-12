import httpx
import os
from fastapi import HTTPException

from models import FiltrosEvento

EVENTOS_SERVICE_URL = os.getenv("EVENTOS_SERVICE_URL", "http://localhost:8001")

################################################################
######################  CRUD BASICO  ###########################

#GET EVENTO 
async def get_evento_id(evento_id: str,):
    """Obtiene un evento por id"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/{evento_id}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS DE UN CALENDARIO
async def get_eventos_por_calendario(calendario_id: str):
    """Obtiene todos los eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#POST CREAR EVENTOS
async def crearEvento(calendario_id: str, evento_data: dict):
    """Obtiene todos los eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}",
                    json=evento_data)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#POST CREAR EVENTOS
async def actualizarEvento(evento_id: str, evento_data: dict):
    """Obtiene todos los eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/{evento_id}",
                    json=evento_data)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")


#POST CREAR EVENTOS
async def deleteEvento(evento_id: str):
    """Obtiene todos los eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/{evento_id}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

################################################################
#################  BÚSQUEDAS PARAMETRIZADAS  ###################

#GET EVENTOS DE UN CALENDARIO POR MES
async def get_eventos_por_calendario_y_mes(calendario_id: str, fecha: str):
    """Obtiene eventos de un calendario para un mes específico"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}/mes/{fecha}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS DE UN CALENDARIO POR DIA
async def getEventosCalendarioPorDia(calendario_id: str, fecha: str):
    """Obtiene eventos de un calendario para un dia específico"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}/dia/{fecha}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS POR TITULO
async def getEventosPorTitulo(titulo: str):
    """Obtiene eventos en base a su titulo"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/buscar/{titulo}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS DE UN CALENDARIO POR TITULO
async def getEventosCalendarioPorTitulo(calendario_id: str, titulo: str):
    """Obtiene eventos de un calendario en base a su titulo"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}/buscar/{titulo}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS DE UN ORGANIZADOR
async def getEventosPorOrganizador(organizador: str):
    """Obtiene los eventos de un organizador"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/organizador/{organizador}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS DE UN ORGANIZADOR PARA UN CALENDARIO
async def getEventosCalendarioPorOrganizador(calendario_id: str, organizador: str):
    """Obtiene eventos de un calendario en base a su titulo"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}/organizador/{organizador}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de eventos no disponible: {str(e)}")

#GET EVENTOS POR FILTROS
async def buscarEventosPorFiltros2(
    titulo: str | None = None,
    organizador: str | None = None,
    calendarios: list[str] | None = None,
    desde: str | None = None,
    hasta: str | None = None
):
    """
    Llama al microservicio de eventos usando el endpoint /eventos/filtros
    para obtener eventos según parámetros.
    """
    params = {}

    if titulo:
        params["titulo"] = titulo
    if organizador:
        params["organizador"] = organizador
    if calendarios:
        params["calendarios"] = [c for c in calendarios if c]
    if desde:
        params["desde"] = desde
    if hasta:
        params["hasta"] = hasta

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/eventos/filtros",
                params=params
            )

            if response.status_code == 404:
                return []

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Servicio de eventos no disponible: {str(e)}"
            )


#GET EVENTOS POR FILTROS
async def buscarEventosPorFiltros(filtros: FiltrosEvento):
    # Preparamos el JSON para el microservicio
    payload = {
        "titulo": filtros.titulo,
        "organizador": filtros.organizador,
        "calendarios": filtros.calendarios,
        "desde": filtros.desde,
        "hasta": filtros.hasta
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{EVENTOS_SERVICE_URL}/api_eventos/v1/eventos/filtros",
                json=payload
            )
            if response.status_code == 404:
                return []  # sin resultados no es error
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            )
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Servicio de eventos no disponible: {str(e)}"
            )
