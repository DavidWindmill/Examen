from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import current_user
from app.models_locations import Location
from app.services.geocoding import geocode

from app.services.dropbox_service import delete_dropbox_path

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
async def create_location(
    request: Request,
    place: str = Form(...),
    image: UploadFile | None = File(None),
):
    # aquí asumo que tú ya sacas el email del token en tu dependencia/middleware
    # Ejemplo: email = request.state.user_email
    email = request.state.email  # ajusta esto a tu implementación real

    # 1) geocodificar "place" como ya haces ahora
    # debe devolverte name/lat/lon (lon)
    name, lat, lon = await geocode_place(place)  # <- usa tu función actual

    loc = Location(email=email, name=name, lat=lat, lon=lon)

    # 2) imagen opcional
    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(400, "El archivo debe ser una imagen")

        content = await image.read()
        ext = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
        dropbox_path = f"{DROPBOX_BASE_FOLDER}/locations/{email}/{uuid4().hex}{ext}"

        public_url, saved_path = await upload_image_bytes(content, dropbox_path)
        loc.image_url = public_url
        loc.image_path = saved_path

    await loc.insert()
    return loc


@router.delete("/locations/{location_id}")
async def delete_location(location_id: str, request: Request):
    email = request.state.email  # ajusta
    loc = await Location.get(location_id)
    if not loc or loc.email != email:
        raise HTTPException(404, "No encontrado")

    if loc.image_path:
        await delete_dropbox_path(loc.image_path)

    await loc.delete()
    return {"ok": True}
