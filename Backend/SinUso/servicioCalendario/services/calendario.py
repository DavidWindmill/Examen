from beanie import PydanticObjectId
from models import Calendario
from typing import List
import httpx
from datetime import datetime, timezone
import os

# URLs de servicios desde variables de entorno
EVENTOS_SERVICE_URL = os.getenv("EVENTOS_SERVICE_URL", "http://localhost:8001") # Puerto 8001 para eventos

# ------------------------------------------------------- #
#                   Métodos GET                           #
# ------------------------------------------------------- #

async def getTodosLosCalendarios():
    try:
        calendarios = await Calendario.find_all().to_list()
        return calendarios
    except Exception as e:
        return {"error": f"Error al obtener calendarios: {e}"}

async def getCalendario(calendarioID: PydanticObjectId):
    calendario = await Calendario.get(calendarioID)
    return calendario

# -------------------------------------------------------
# Búsquedas parametrizadas y consultas relacionales
# ---------------------------
# 1) Búsqueda parametrizada:
# Devuelve calendarios gestionados por un organizador (match parcial, case-insensitive),
# ordenados por creación descendente (usamos _id descendente para mostrarlo por de fecha de creación (más reciente)).
# ---------------------------
async def getCalendariosPorOrganizador(organizador: str) -> List[Calendario]:
    """
    Dado un organizador (string), devuelve los calendarios que gestiona
    """
    try: # Usamos regex para búsqueda parcial (Es un comando que busca el patron pasado)
        regex = {"$regex": organizador, "$options": "i"} # 'i' para case-insensitive (Que de igual mayúsculas que minúsculas)
        calendarios = await Calendario.find({"organizador": regex}).sort([("_id", -1)]).to_list() # pyright: ignore[reportArgumentType]
        return calendarios
    except Exception as e:
        return {"error": f"Error buscando calendarios por organizador: {e}"} # pyright: ignore[reportReturnType]

# ---------------------------
# 2) Búsqueda parametrizada:
# Buscar calendarios por texto en título o en palabras_claves (partial match, case-insensitive).
# ---------------------------
async def buscarCalendariosPorTexto(texto: str) -> List[Calendario]:
    """
    Busca en "titulo" o en "palabras_claves" de Calendario el texto dado
    """
    try: # Usamos regex para búsqueda parcial (Es un comando que busca el patron pasado)
        regex = {"$regex": texto, "$options": "i"} # 'i' para case-insensitive (Que de igual mayúsculas que minúsculas)
        query = {"$or": [{"titulo": regex}, {"palabras_claves": regex}]}
        calendarios = await Calendario.find(query).to_list()
        return calendarios
    except Exception as e:
        return {"error": f"Error buscando calendarios por texto: {e}"} # pyright: ignore[reportReturnType]


# -------------------------------------------------------
# Consultas que usan relaciones entre entidades (Evento, Comentario)
# Para poder hacer este tipo de búsquedas, usamos httpx haciendo una llamada con la url al microservicio correspondiente
# Para poder ejecutar estas funciones, es necesario que el microservicio correspondiente esté en funcionamiento, por lo que
# hay que abrir dos o tres terminales: uno para el servicio de calendario y otro para el servicio de eventos o comentarios
# --------------------------- 
async def getCantidadEventosDeCalendario(calendarioID: PydanticObjectId) -> dict:
    """
    Dado un calendarioID, devuelve la cantidad de eventos asociados al calendario.
    """
    url = f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendarioID}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            eventos = response.json()
            cantidad_eventos = len(eventos)
            return {"calendarioID": str(calendarioID), "cantidad_eventos": cantidad_eventos}
    except httpx.HTTPStatusError as e:
        return {"error": f"Error en la solicitud HTTP: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Error obteniendo cantidad de eventos: {e}"}
    
async def getProximosEventosDeCalendario(calendarioID: PydanticObjectId, limite: int) -> dict:
    """
    Dado un calendarioID, devuelve los próximos eventos (ordenados por fecha de inicio).
    Solo devuelve eventos cuya hora_fin sea mayor que la hora actual.
    """
    url = f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendarioID}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"limite": limite})
            response.raise_for_status()
            eventos = response.json()
            
            # Filtrar eventos: solo aquellos cuya hora_fin es mayor que la hora actual
            hora_actual = datetime.now(timezone.utc)
            eventos_futuros = []
            for evento in eventos:
                hora_fin_raw = evento.get("hora_fin")
                if hora_fin_raw:
                    try:
                        # Si viene como dict (ej: {"$date": timestamp}), extraer el valor
                        if isinstance(hora_fin_raw, dict):
                            if "$date" in hora_fin_raw:
                                # Timestamp en milisegundos
                                timestamp = hora_fin_raw["$date"]
                                if isinstance(timestamp, int):
                                    hora_fin = datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc)
                                else:
                                    hora_fin = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            else:
                                continue
                        # Si viene como string ISO
                        elif isinstance(hora_fin_raw, str):
                            hora_fin = datetime.fromisoformat(hora_fin_raw.replace('Z', '+00:00'))
                        else:
                            continue
                        
                        # Asegurar que hora_fin sea timezone-aware
                        if hora_fin.tzinfo is None:
                            hora_fin = hora_fin.replace(tzinfo=timezone.utc)
                        
                        if hora_fin > hora_actual:
                            eventos_futuros.append(evento)
                    except (ValueError, KeyError):
                        # Si hay error al parsear, ignorar este evento
                        continue
            
            return {
                "calendarioID": str(calendarioID),
                "cantidad_eventos": len(eventos_futuros),
                "limite": limite,
                "proximos_eventos": eventos_futuros
            }
    except httpx.HTTPStatusError as e:
        return {"error": f"Error en la solicitud HTTP: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Error obteniendo próximos eventos: {e}"}


# ------------------------------------------------------- #
#                   Métodos POST                          #
# ------------------------------------------------------- #

async def crearCalendario(titulo: str, organizador: str, palabras_claves: list | None = None):
    nuevoCalendario = Calendario(
        titulo=titulo,
        organizador=organizador,
        palabras_claves=palabras_claves
    )
    await nuevoCalendario.insert()
    return nuevoCalendario

async def añadirPalabraClaveACalendario(id: PydanticObjectId, palabra_clave: str):
    calendario = await Calendario.get(id)
    if not calendario:
        return {"error": "Calendario no encontrado"}
    if calendario.palabras_claves is None:
        calendario.palabras_claves = []
    if palabra_clave not in calendario.palabras_claves:
        calendario.palabras_claves.append(palabra_clave)
        await calendario.save()
    return calendario


# ------------------------------------------------------- #
#                   Métodos PUT                           #
# ------------------------------------------------------- #

async def actualizarCalendario(id: PydanticObjectId, calendario: dict):
    calendario_existente = await Calendario.get(id)
    if not calendario_existente:
        return {"error": "Calendario no encontrado",
                "codigo_respuesta": 404}
    
    campos_validos = ["titulo", "organizador", "palabras_claves"]
    actualizado = False

    for campo in campos_validos:
        if campo in calendario:
            setattr(calendario_existente, campo, calendario[campo])
            actualizado = True

    if not actualizado:
        return {"error": "No se proporcionaron campos válidos para actualizar",
                "codigo_respuesta": 400}

    await calendario_existente.save()
    return calendario_existente
    

# ------------------------------------------------------- #
#                   Métodos DELETE                        #
# ------------------------------------------------------- #

async def eliminarCalendario(id: PydanticObjectId):
    calendario = await Calendario.get(id)
    if calendario:
        await calendario.delete()
        return True
    return False


async def eliminarPalabraClaveDeCalendario(id: PydanticObjectId, palabra_clave: str):
    calendario = await Calendario.get(id)
    if not calendario:
        return {"error": "Calendario no encontrado"}
    if calendario.palabras_claves and palabra_clave in calendario.palabras_claves:
        calendario.palabras_claves.remove(palabra_clave)
        await calendario.save()
        return calendario
    else:
        return {"error": "Palabra clave no encontrada en el calendario"}