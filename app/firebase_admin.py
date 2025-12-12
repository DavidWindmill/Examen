import base64
import json
import os

import firebase_admin
from firebase_admin import auth, credentials

def init_firebase_admin():
    if firebase_admin._apps:
        return

    # En Vercel es común guardar el JSON como string o como base64.
    raw = (
        os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        or os.getenv("FIREBASE_ADMIN_JSON")
        or os.getenv("FIREBASE_SERVICE_ACCOUNT")
    )
    if not raw:
        raise RuntimeError(
            "Falta la credencial de Firebase Admin. Configura FIREBASE_SERVICE_ACCOUNT_JSON (JSON completo) "
            "o FIREBASE_SERVICE_ACCOUNT (base64 del JSON) en Vercel."
        )

    raw = raw.strip()
    try:
        # Si parece JSON, úsalo tal cual; si no, intenta base64.
        if raw.startswith("{"):
            cred_dict = json.loads(raw)
        else:
            decoded = base64.b64decode(raw).decode("utf-8")
            cred_dict = json.loads(decoded)
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el JSON de Firebase Admin desde env: {e}")

    # Muchas veces la private_key viene con \n escapados en variables de entorno.
    if isinstance(cred_dict, dict) and "private_key" in cred_dict and isinstance(cred_dict["private_key"], str):
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

def verify_id_token(id_token: str):
    init_firebase_admin()
    return auth.verify_id_token(id_token)
