# Esta clase "models" sirve para representar
# las clases / documentos de la base de datos Mongo
# (necesaria para usar beanie como lo que haciamos en springboot con JPA)

# models.py
from typing import Optional, List
from beanie import Document, PydanticObjectId
from datetime import datetime
from pydantic import BaseModel
# Document de Beanie ya hereda de Pydantic.BaseModel.

# Creado solo para pasar la palabra clave en el cuerpo de la solicitud
class PalabraClave(BaseModel):
    palabra_clave: str

class Calendario(Document):
    titulo: str
    organizador: str
    palabras_claves: Optional[List[str]] = None

    class Settings:
        name = "Calendario"
