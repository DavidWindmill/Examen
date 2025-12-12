# (necesaria para usar beanie como lo que haciamos en springboot con JPA)

from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel



# Document de Beanie ya hereda de Pydantic.BaseModel.
class Comentario(Document):
    evento: PydanticObjectId #IMPORTANTE SERIALIZAR (para objetos) NO PONER ObjectId solo  
    usuario: str
    texto: str
    calificacion: Optional[float] = None
    notificacion: bool

    class Settings:
        name = "Comentario"  

# Necesario para actualizar en los metodos CRUD (solo actualiza texto y calificacion)
class ComentarioUpdate(BaseModel):
    texto: Optional[str] = None
    calificacion: Optional[float] = None
    notificacion: Optional[bool] = None

# Lo mismo para crear (para que no tengamos que escribir un id a la hora de crear el comentario)
class ComentarioCreate(BaseModel):
    evento: PydanticObjectId
    usuario: str
    texto: str
    calificacion: Optional[float] = None
    notificacion: bool

