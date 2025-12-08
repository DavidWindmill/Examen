from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.firebase_admin import verify_id_token

bearer = HTTPBearer()


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    """Valida el ID Token de Firebase y devuelve el payload decodificado."""
    try:
        payload = verify_id_token(creds.credentials)
        # Guardamos también el token crudo (para persistirlo con la reseña)
        if isinstance(payload, dict):
            payload["__raw_token"] = creds.credentials
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")
