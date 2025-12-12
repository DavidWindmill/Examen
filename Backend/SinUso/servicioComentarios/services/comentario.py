from models import Comentario, ComentarioUpdate, ComentarioCreate
from beanie import PydanticObjectId
from fastapi import HTTPException
import httpx
from bson import ObjectId
import os
# URLs de servicios desde variables de entorno
EVENTOS_SERVICE_URL = os.getenv("EVENTOS_SERVICE_URL", "http://localhost:8001") # Se devuelve localhost si no está definida la variable


################################################################
######################  CRUD BASICO  ###########################

async def get_all_comentarios():
    # devuelve Document pero FastAPI lo serializa automaticamente
    return await Comentario.find_all().to_list()  


async def getComentario(comentarioID: PydanticObjectId):
    comentario = await Comentario.get(comentarioID)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return comentario


async def crear_comentario(comentarioRecibido: ComentarioCreate):
    # IMPORTANTE: comprobar que exista el evento
    # Lo hacemos mediante una peticion http (con la libreria nueva httpx en vez de requests)
    async with httpx.AsyncClient() as client:
        # Conectamos con el microservicio "Evento" y hacemos get con el id del evento
        resp = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/{comentarioRecibido.evento}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="El evento no existe")

    # Una vez aqui hemos comprobado que el evento existe (continuamos con actualizar)
    comentarioNuevo = Comentario(**comentarioRecibido.dict()) # Convierte de ComentarioCreate -> Comentario

    # Comprobar que la calificacion este entre 0 y 10
    if comentarioNuevo.calificacion < 0 or comentarioNuevo.calificacion > 10:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 0 y 10")

    await comentarioNuevo.insert()
    return comentarioNuevo


async def actualizar_comentario(comentarioID: PydanticObjectId, data: ComentarioUpdate):
    comentario = await Comentario.get(comentarioID)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    # Actualizar solamente texto y calificacion (eventoID & usuario no se actualizan)
    if data.texto is not None:
        comentario.texto = data.texto

    # Comprobar que la calificacion sea no nula y comprendido entre 0 y 10
    if data.calificacion is not None:
        if data.calificacion < 0 or data.calificacion > 10:
            raise HTTPException(status_code=400, detail="La calificación debe estar entre 0 y 10")

        comentario.calificacion = data.calificacion
    
    if data.notificacion is not None:
        comentario.notificacion = data.notificacion

    await comentario.save()
    return comentario


async def eliminar_comentario(comentarioID: PydanticObjectId):
    comentario = await Comentario.get(comentarioID)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    await comentario.delete()
    return {"mensaje": "Comentario eliminado correctamente"}

################################################################
###################### CRUD BASICO FIN ########################
   



################################################################
################ OPERACIONES DE CONSULTA #######################

##########################################################################################
######### mas simples (solo con Comentario, no se conecta con otro microservicio) ########

# minimo 2 "simples"

#1
async def get_comentarios_por_nota_minima(min_nota: float):
    if min_nota < 0 or min_nota > 10:
        raise HTTPException(status_code=400, detail="La calificación mínima debe estar entre 0 y 10")

    comentarios = await Comentario.find(Comentario.calificacion >= min_nota).to_list()

    # Si no hay resultados devolvemos una lista vacía (no es error)
    return comentarios

#2
async def get_comentarios_por_usuario(nombre_usuario: str):
    comentarios = await Comentario.find(Comentario.usuario == nombre_usuario).to_list()
    return comentarios



############################################################################
######## mas complejos (conectarse con otros microservicios) ###############


# Minimo 2 "complejos"

#1
# Encuentra todos los comentarios de un evento especifico
async def get_comentarios_por_evento(eventoID_str: str):
    try:
        eventoID = PydanticObjectId(eventoID_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de evento inválida")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/{eventoID}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="El evento no existe")

    comentarios = await Comentario.find(Comentario.evento == eventoID).to_list()

    return comentarios


#2
# Encuentra todos los comentarios asociados a un calendario (que tiene uno o varios eventos)
async def get_comentarios_por_calendario(calendario_id_str: str):
    try:
        calendario_id = PydanticObjectId(calendario_id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de calendario inválida")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{calendario_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="No se encontraron eventos para este calendario")

    eventos = resp.json()
    if not eventos:
        return []

    eventos_ids_obj = []
    for evento in eventos:
        if "_id" in evento:
            id_val = evento["_id"]
            if isinstance(id_val, dict) and "$oid" in id_val:
                eventos_ids_obj.append(ObjectId(id_val["$oid"]))
            elif isinstance(id_val, str):
                try:
                    eventos_ids_obj.append(ObjectId(id_val))
                except Exception:
                    continue

    comentarios = await Comentario.find({"evento": {"$in": eventos_ids_obj}}).to_list()
    return comentarios

#3
async def get_notificaciones_de_un_organizador(organizador: str):
    """
    Devuelve los comentarios de todos los eventos organizados por `organizador`
    que cumplan:
      - notificacion == True
      - usuario != organizador
    """

    # 1) Pedir al microservicio de eventos los eventos de este organizador
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/organizador/{organizador}"
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="No se encontraron eventos para este organizador"
            )

    eventos = resp.json()
    if not eventos:
        return []

    # 2) Convertir los _id de esos eventos a ObjectId
    eventos_ids_obj = []
    for evento in eventos:
        if "_id" in evento:
            id_val = evento["_id"]
            if isinstance(id_val, dict) and "$oid" in id_val:
                eventos_ids_obj.append(ObjectId(id_val["$oid"]))
            elif isinstance(id_val, str):
                eventos_ids_obj.append(ObjectId(id_val))

    if not eventos_ids_obj:
        return []

    # 3) Buscar comentarios de esos eventos que:
    #    - tengan notificacion == True
    #    - no sean del propio organizador
    comentarios = await Comentario.find({
        "evento": {"$in": eventos_ids_obj},
        "notificacion": True,
        "usuario": {"$ne": organizador},
    }).to_list()

    return comentarios

# #3 (Falta el metodo en eventos) WORK IN PROGRESS
# async def get_usuarios_que_comentaron_eventos_de_organizador(organizador: str):
#     async with httpx.AsyncClient() as client:
#         resp = await client.get(
#             f"http://127.0.0.1:8001/api_eventos/v1/evento/organizador/{organizador}"
#         )
#         if resp.status_code != 200:
#             raise HTTPException(status_code=502, detail="Error al obtener los eventos del organizador")

#         eventos = resp.json()

#     # Si no hay eventos, devolvemos lista vacía
#     if not eventos:
#         return {"organizador": organizador, "usuarios_comentaron": []}

#     # Extraemos los IDs de esos eventos
#     eventos_ids = []
#     for evento in eventos:
#         if "_id" in evento:
#             # Si el evento viene como {"_id": "68f36377f383d1e8486031a4"} sin $oid
#             if isinstance(evento["_id"], str):
#                 eventos_ids.append(ObjectId(evento["_id"]))
#             # Si el evento viene con {"_id": {"$oid": "..."}}
#             elif isinstance(evento["_id"], dict) and "$oid" in evento["_id"]:
#                 eventos_ids.append(ObjectId(evento["_id"]["$oid"]))

#     if not eventos_ids:
#         return {"organizador": organizador, "usuarios_comentaron": []}

#     # Buscamos los comentarios sobre esos eventos usando Beanie
#     comentarios = await Comentario.find(In(Comentario.evento, eventos_ids)).to_list()

#     # Extraemos los usuarios únicos que comentaron o valoraron
#     usuarios = list({comentario.usuario for comentario in comentarios})

#     # Devolvemos los resultados
#     return {"organizador": organizador, "usuarios_comentaron": usuarios}
