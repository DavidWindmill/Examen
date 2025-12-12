from fastapi import FastAPI
from beanie import PydanticObjectId
from bd import init_db
import services.mapa as servicioMapa
from models import Comentario, ComentarioUpdate, ComentarioCreate # clases del modelo Comentario
# from typing import List no necesario por ahora

app = FastAPI()

#Prefijo de la aplicación
path = "/api_comentarios/v1"

# Necesraio para usar BEANIE
@app.on_event("startup")
async def start_db():
    await init_db()


# Endpoints de CRUD

@app.get(path + "/comentarios")
async def obtener_comentarios():
    return await servicioMapa.get_all_comentarios()

@app.get(path + "/comentarios/{comentarioID}")
async def obtener_comentario(comentarioID: PydanticObjectId):
    return await servicioMapa.getComentario(comentarioID)

@app.post(path + "/comentarios")
async def crear_comentario(comentario: ComentarioCreate):
    return await servicioMapa.crear_comentario(comentario)


@app.put(path + "/comentarios/{comentarioID}")
async def actualizar_comentario(comentarioID: PydanticObjectId, data: ComentarioUpdate):
    return await servicioMapa.actualizar_comentario(comentarioID, data)


@app.delete(path + "/comentarios/{comentarioID}")
async def eliminar_comentario(comentarioID: PydanticObjectId):
    return await servicioMapa.eliminar_comentario(comentarioID)



######################################################################
######################################################################

# endpoints de operaciones de consulta (2 simples y 2 complejos minimo)

#1
@app.get(path + "/comentarios/calificacion/{min_nota}")
async def obtener_comentarios_por_nota_minima(min_nota: float):
    return await servicioMapa.get_comentarios_por_nota_minima(min_nota)
    
#2
@app.get(path + "/comentarios/usuario/{usuario_id}")
async def obtener_comentarios_por_usuario(usuario_id: str):
    return await servicioMapa.get_comentarios_por_usuario(usuario_id)

#3
@app.get(path + "/comentarios/organizador/{organizador}")
async def obtener_notificaciones_de_un_organizador(organizador: str):
    return await servicioMapa.get_notificaciones_de_un_organizador(organizador)

########################################################################


#1
@app.get(path + "/comentarios/evento/{evento_id}")
async def obtener_comentarios_por_evento(evento_id: str):
    return await servicioMapa.get_comentarios_por_evento(evento_id)

#2 
@app.get(path + "/comentarios/calendario/{calendario_id}")
async def obtener_comentarios_por_calendario(calendario_id: str):
    return await servicioMapa.get_comentarios_por_calendario(calendario_id)

#3
#@app.get(path + "/comentarios/organizador/{nombre_parcial}")
#async def obtener_usuarios_que_comentaron_eventos_de_organizador(nombre_parcial: str):
#    return await servicioComentario.get_usuarios_que_comentaron_eventos_de_organizador(nombre_parcial)
