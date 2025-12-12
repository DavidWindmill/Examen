from beanie import Document
from pydantic import Field


class Location(Document):
    """Marcador (país/ciudad) asociado a un usuario por email."""

    email: str = Field(..., description="Email del usuario autenticado (Firebase)")
    name: str = Field(..., description="Nombre del país o ciudad")
    lat: float
    lon: float

    class Settings:
        name = "locations"
