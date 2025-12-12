import httpx
import os
from fastapi import HTTPException

CALENDARIO_SERVICE_URL = os.getenv("CALENDARIO_SERVICE_URL", "http://localhost:8002")

async def get_calendarios():
    """Obtiene todos los calendarios"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def crear_calendario(titulo: str, organizador: str, palabras_claves: list = None): # type: ignore
    """Crea un nuevo calendario"""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "titulo": titulo,
                "organizador": organizador,
                "palabras_claves": palabras_claves or []
            }
            response = await client.post(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def eliminar_calendario(calendario_id: str):
    """Elimina un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def actualizar_calendario(calendario_id: str, datos: dict):
    """Actualiza un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}", json=datos)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def añadir_palabra_clave(calendario_id: str, palabra_clave: str):
    """Añade una palabra clave a un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            payload = {"palabra_clave": palabra_clave}
            response = await client.post(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}/palabras-claves", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def buscar_calendarios(query: str):
    """Busca calendarios por título, organizador o tags usando el microservicio"""
    async with httpx.AsyncClient() as client:
        resultados_dict = {}
        
        try:
            # Buscar por texto (título o palabras_claves) - endpoint: /api/v1/calendarios/buscar/{texto}
            try:
                response = await client.get(
                    f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/buscar/{query}"
                )
                response.raise_for_status()
                resultados_texto = response.json()
                
                # Agregar resultados al diccionario
                if resultados_texto and isinstance(resultados_texto, list):
                    for cal in resultados_texto:
                        cal_id = cal.get('_id')
                        if cal_id:
                            resultados_dict[cal_id] = cal
            except httpx.HTTPStatusError as e:
                # Si es 404, no hay resultados de esta búsqueda, continuar
                if e.response.status_code != 404:
                    raise
            
            # Buscar por organizador - endpoint: /api/v1/calendarios/organizador/{organizador}
            try:
                response_org = await client.get(
                    f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/organizador/{query}"
                )
                response_org.raise_for_status()
                resultados_org = response_org.json()
                
                # Agregar resultados al diccionario
                if resultados_org and isinstance(resultados_org, list):
                    for cal in resultados_org:
                        cal_id = cal.get('_id')
                        if cal_id:
                            resultados_dict[cal_id] = cal
            except httpx.HTTPStatusError as e:
                # Si es 404, no hay resultados de esta búsqueda, continuar
                if e.response.status_code != 404:
                    raise
            
            return list(resultados_dict.values())
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def get_cantidad_eventos_calendario(calendario_id: str):
    """Obtiene la cantidad de eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}/cantidad-eventos")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")

async def get_proximos_eventos_calendario(calendario_id: str, limite: int = 5):
    """Obtiene los próximos eventos de un calendario"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CALENDARIO_SERVICE_URL}/api/v1/calendarios/{calendario_id}/proximos-eventos",
                params={"limite": limite}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")
