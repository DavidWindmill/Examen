import json
import os
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase_admin():
    if firebase_admin._apps:
        return

    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON no está configurada en Vercel.")

    cred_dict = json.loads(raw)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

def verify_id_token(id_token: str):
    init_firebase_admin()
    return auth.verify_id_token(id_token)
