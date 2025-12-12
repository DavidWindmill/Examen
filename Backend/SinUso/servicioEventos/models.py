from datetime import datetime
from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class Evento(Document):
    titulo: str
    hora_comienzo: datetime
    hora_fin: datetime
    lugar: Optional[str] = None
    organizador: Optional[str] = None  # futuro ID de usuario
    calendario: PydanticObjectId
    descripcion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    class Settings:
        name = "Evento"  # Nombre de la clase en MongoDB

class EventoActualizar(BaseModel):
    titulo: Optional[str] = None
    hora_comienzo: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    lugar: Optional[str] = None
    descripcion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class EventoCrear(BaseModel):
    titulo: str
    hora_comienzo: datetime
    hora_fin: datetime
    lugar: Optional[str] = None
    organizador: str
    descripcion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class FiltrosEvento(BaseModel):
    titulo: Optional[str] = None
    organizador: Optional[str] = None
    calendarios: Optional[List[str]] = None
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None

