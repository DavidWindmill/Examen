from __future__ import annotations

from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class ReviewImage(BaseModel):
    """Imagen asociada a una reseña."""

    url: str
    path: str


class Review(Document):
    """Reseña de un establecimiento (similar a TripAdvisor)."""

    # Establecimiento
    place_name: str = Field(..., description="Nombre del establecimiento")
    address: str = Field(..., description="Dirección postal")
    lat: float
    lon: float
    rating: int = Field(..., ge=0, le=5, description="Valoración 0..5")

    # Autor (desde el token OAuth/Firebase)
    author_email: str = Field(..., description="Email del autor")
    author_name: Optional[str] = Field(None, description="Nombre del autor")

    # Info del token (timestamps y el token en sí)
    token_iat: Optional[int] = Field(None, description="Issued-at (UNIX seconds)")
    token_exp: Optional[int] = Field(None, description="Expiration (UNIX seconds)")
    oauth_token: str = Field(..., description="Token OAuth/Firebase usado al crear")

    # Imágenes (URLs públicas)
    images: List[ReviewImage] = Field(default_factory=list)

    class Settings:
        name = "reviews"
