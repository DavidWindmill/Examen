from beanie import Document
from pydantic import Field
from typing import Optional


class Location(Document):
    """Marcador (país/ciudad) asociado a un usuario por email."""

    email: str = Field(..., description="Email del usuario autenticado (Firebase)")
    name: str = Field(..., description="Nombre del país o ciudad")
    lat: float
    lon: float

        # NUEVO
    image_url: Optional[str] = None      # enlace público (para mostrar en web)
    image_path: Optional[str] = None     # ruta en dropbox (para borrar/actualizar)

    class Settings:
        name = "locations"
