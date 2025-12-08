from __future__ import annotations

import os
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import current_user
from app.models_reviews import Review, ReviewImage
from app.services.geocoding import geocode
from app.services.dropbox_service import (
    DROPBOX_BASE_FOLDER,
    delete_dropbox_path,
    upload_image_bytes,
)


router = APIRouter(prefix="/api", tags=["reviews"])


@router.get("/reviews")
async def list_reviews(user: dict = Depends(current_user)):
    """Listado para la vista principal.

    Devuelve todas las reseñas (comunicación autenticada). Para la UI solo se
    necesitan: nombre, dirección, lon/lat y valoración.
    """

    # Solo valida que hay token válido
    if not (user or {}).get("uid"):
        raise HTTPException(status_code=401, detail="No autorizado")

    reviews = await Review.find_all().to_list()
    return [
        {
            "_id": str(r.id),
            "place_name": r.place_name,
            "address": r.address,
            "lat": r.lat,
            "lon": r.lon,
            "rating": r.rating,
        }
        for r in reviews
    ]


@router.get("/reviews/{review_id}")
async def get_review(review_id: str, user: dict = Depends(current_user)):
    """Detalle de una reseña (incluye token, timestamps e imágenes)."""
    if not (user or {}).get("uid"):
        raise HTTPException(status_code=401, detail="No autorizado")

    r = await Review.get(review_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return r


@router.post("/reviews")
async def create_review(
    place_name: str = Form(...),
    address: str = Form(...),
    rating: int = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    user: dict = Depends(current_user),
):
    """Crea una reseña.

    - Geocoding a partir de la dirección.
    - Guarda email/nombre del autor y timestamps del token.
    - Guarda el token OAuth/Firebase usado.
    - Sube 0..N imágenes a Dropbox (o equivalente) y guarda las URIs.
    """
    email = (user or {}).get("email")
    name = (user or {}).get("name")
    iat = (user or {}).get("iat")
    exp = (user or {}).get("exp")

    # El token en sí viaja ya validado; lo guardamos para acreditar autoría.
    raw_token = (user or {}).get("__raw_token")

    if not email:
        raise HTTPException(status_code=401, detail="No autorizado (token sin email)")
    if not raw_token:
        raise HTTPException(status_code=401, detail="No autorizado (token ausente)")

    place_name = (place_name or "").strip()
    address = (address or "").strip()
    if not place_name:
        raise HTTPException(status_code=400, detail="Falta el nombre del establecimiento")
    if not address:
        raise HTTPException(status_code=400, detail="Falta la dirección postal")
    if rating is None or int(rating) < 0 or int(rating) > 5:
        raise HTTPException(status_code=400, detail="La valoración debe estar entre 0 y 5")

    coords = await geocode(address)
    if not coords:
        raise HTTPException(status_code=400, detail="No se pudo geocodificar la dirección")
    lat, lon = coords

    review = Review(
        place_name=place_name,
        address=address,
        lat=lat,
        lon=lon,
        rating=int(rating),
        author_email=email,
        author_name=name,
        token_iat=iat,
        token_exp=exp,
        oauth_token=raw_token,
        images=[],
    )

    # Subida de imágenes (0..N)
    uploaded: List[ReviewImage] = []
    for img in images or []:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Todos los archivos deben ser imágenes")
        content = await img.read()
        if not content:
            continue

        ext = os.path.splitext(img.filename or "")[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"

        dropbox_path = f"{DROPBOX_BASE_FOLDER}/reviews/{email}/{uuid4().hex}{ext}"
        public_url, saved_path = await upload_image_bytes(content, dropbox_path)
        uploaded.append(ReviewImage(url=public_url, path=saved_path))

    review.images = uploaded
    await review.insert()
    return review


@router.get("/geocode")
async def geocode_address(q: str, user: dict = Depends(current_user)):
    """Geocoding para el buscador del mapa (centra el mapa en una dirección)."""
    if not (user or {}).get("uid"):
        raise HTTPException(status_code=401, detail="No autorizado")

    coords = await geocode(q)
    if not coords:
        raise HTTPException(status_code=404, detail="No se encontró la dirección")
    lat, lon = coords
    return {"lat": lat, "lon": lon}


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, user: dict = Depends(current_user)):
    """No requerido por el enunciado, pero útil para pruebas.

    Solo el autor (por email) puede borrar su reseña.
    """
    email = (user or {}).get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autorizado")

    r = await Review.get(review_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    if r.author_email != email:
        raise HTTPException(status_code=403, detail="Solo el autor puede borrar la reseña")

    for img in r.images or []:
        try:
            await delete_dropbox_path(img.path)
        except Exception:
            pass

    await r.delete()
    return {"ok": True}
