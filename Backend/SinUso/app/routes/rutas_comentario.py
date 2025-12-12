from fastapi import APIRouter

import services.comentario as ComentarioService

router = APIRouter(prefix="/comentario", tags=["Comentarios"])

# esto se llama desde el frontend evento.html cuantos se va a crear un comentario
@router.post("/", summary="Crear comentario")
async def crear_comentario(data: dict):
    return await ComentarioService.crear_comentario(data)

# esto se llama desde el frontend evento.html cuantos se va a actualizar un comentario
@router.put("/{comentario_id}", summary="Actualizar comentario")
async def actualizar_comentario(comentario_id: str, data: dict):
    return await ComentarioService.actualizar_comentario(comentario_id, data)

# esto se llama desde el frontend evento.html cuantos se va a eliminar un comentario
@router.delete("/{comentario_id}", summary="Eliminar comentario")
async def eliminar_comentario(comentario_id: str):
    return await ComentarioService.eliminar_comentario(comentario_id)

# esto se llama desde el frontend base.html cuantos se va a visualizar las notificaciones
@router.get(
    "/organizador/{organizador}",
    summary="Obtener notificaciones de un organizador",
)

async def obtener_notificaciones_organizador(organizador: str):
    return await ComentarioService.obtener_notificaciones_organizador(organizador)
