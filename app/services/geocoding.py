import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "examen-mapa-viajes/1.0 (FastAPI)"


async def geocode(place: str) -> tuple[float, float] | None:
    """Devuelve (lat, lon) usando Nominatim (OpenStreetMap)."""
    place = (place or "").strip()
    if not place:
        return None

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            NOMINATIM_URL,
            params={
                "q": place,
                "format": "json",
                "limit": 1,
            },
            headers={"User-Agent": USER_AGENT},
        )

    data = resp.json()
    if not data:
        return None

    return float(data[0]["lat"]), float(data[0]["lon"])
