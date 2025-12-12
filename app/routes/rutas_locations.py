from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import current_user
from app.models_locations import Location
from app.services.geocoding import geocode

router = APIRouter(prefix="/api", tags=["locations"])


class AddLocationRequest(BaseModel):
    place: str = Field(..., min_length=1, description="País o ciudad a geocodificar")


@router.get("/locations")
async def get_locations(user=Depends(current_user)):
    """Devuelve los marcadores del usuario autenticado (por email)."""
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="El token no incluye email")

    return await Location.find(Location.email == email).to_list()


@router.post("/locations")
async def add_location(payload: AddLocationRequest, user=Depends(current_user)):
    """Añade un marcador para el usuario usando geocoding (Nominatim)."""
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="El token no incluye email")

    place = payload.place.strip()
    coords = await geocode(place)
    if not coords:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")

    lat, lon = coords
    loc = Location(email=email, name=place, lat=lat, lon=lon)
    await loc.insert()
    return loc


@router.delete("/locations/{location_id}")
async def delete_location(location_id: str, user=Depends(current_user)):
    """Elimina un marcador del usuario. (Opcional, pero útil)"""
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="El token no incluye email")

    try:
        oid = PydanticObjectId(location_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    loc = await Location.get(oid)
    if not loc or loc.email != email:
        raise HTTPException(status_code=404, detail="Marcador no encontrado")

    await loc.delete()
    return {"ok": True}
