import os, datetime, requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from firebase_admin import auth

app = FastAPI()
bearer = HTTPBearer()

mongo = MongoClient(os.environ["MONGO_URI"])
db = mongo["travel_map"]
markers_col = db["markers"]

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        decoded = auth.verify_id_token(creds.credentials)
        email = decoded.get("email")
        if not email:
            raise HTTPException(401, "Token sin email")
        return {"email": email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

@app.get("/api/markers")
def get_markers(user=Depends(current_user)):
    email = user["email"]
    docs = list(markers_col.find({"email": email}, {"email": 0}))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

@app.post("/api/markers")
def add_marker(payload: dict, user=Depends(current_user)):
    place = (payload.get("place") or "").strip()
    if not place:
        raise HTTPException(400, "Falta 'place'")

    # Nominatim geocoding
    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": place, "format": "json", "limit": 1},
        headers={"User-Agent": "travel-map-david/1.0 (contact: you@example.com)"},
        timeout=10,
    )
    data = r.json()
    if not data:
        raise HTTPException(404, "No se encontró el lugar")

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    label = data[0].get("display_name", place)

    doc = {
        "email": user["email"],
        "label": label,
        "query": place,
        "lat": lat,
        "lon": lon,
        "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
    }
    res = markers_col.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    doc.pop("email", None)
    return doc


