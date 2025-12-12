from __future__ import annotations

import os
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.auth import current_user
from app.models_locations import Location
from app.services.geocoding import geocode
from app.services.dropbox_service import (
    upload_image_bytes,
    delete_dropbox_path,
    DROPBOX_BASE_FOLDER,
)

router = APIRouter(prefix="/api", tags=["locations"])


@router.get("/locations")
async def list_locations(user: dict = Depends(current_user)):
    """Devuelve los marcadores del usuario autenticado."""
    email = (user or {}).get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autorizado (token sin email)")

    # Solo los marcadores de ese usuario
    return await Location.find(Location.email == email).to_list()


@router.post("/locations")
async def create_location(
    place: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(current_user),
):
    # 1) Email del usuario autenticado (no request.state.email)
    email = (user or {}).get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autorizado (token sin email)")

    place_clean = place.strip()
    if not place_clean:
        raise HTTPException(status_code=400, detail="El campo 'place' está vacío")

    # 2) Geocoding: tu servicio se llama geocode(place) y devuelve (lat, lon) o None
    coords = await geocode(place_clean)
    if not coords:
        raise HTTPException(status_code=400, detail="No se pudo geocodificar el lugar")

    lat, lon = coords

    loc = Location(
        email=email,
        name=place_clean,
        lat=lat,
        lon=lon,
    )

    # 3) Imagen opcional a Dropbox
    if image is not None:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        content = await image.read()
        if not content:
            raise HTTPException(status_code=400, detail="La imagen está vacía")

        ext = os.path.splitext(image.filename or "")[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            # si no trae extensión buena, usa jpg por defecto
            ext = ".jpg"

        dropbox_path = f"{DROPBOX_BASE_FOLDER}/locations/{email}/{uuid4().hex}{ext}"

        public_url, saved_path = await upload_image_bytes(content, dropbox_path)
        loc.image_url = public_url
        loc.image_path = saved_path

    await loc.insert()
    return loc


@router.delete("/locations/{location_id}")
async def delete_location(
    location_id: str,
    user: dict = Depends(current_user),
):
    email = (user or {}).get("email")
    if not email:
        raise HTTPException(status_code=401, detail="No autorizado")

    loc = await Location.get(location_id)
    if not loc or loc.email != email:
        raise HTTPException(status_code=404, detail="Location no encontrada")

    if getattr(loc, "image_path", None):
        # si existe en dropbox, intenta borrar
        await delete_dropbox_path(loc.image_path)

    await loc.delete()
    return {"ok": True}
