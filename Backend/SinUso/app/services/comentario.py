import httpx
import os
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText

import services.evento as EventoService

COMENTARIO_SERVICE_URL = os.getenv("COMENTARIOS_SERVICE_URL", "http://localhost:8003")

# Config SMTP (rellena estas variables en el entorno / .env del gateway)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")  # tu correo de envío
SMTP_PASS = os.getenv("SMTP_PASS")  # contraseña de app / token

def enviar_correo_comentario(destinatario: str, comentario: dict, nombreEvento: str):
    """Envía un correo simple avisando de un nuevo comentario."""
    if not destinatario:
        print("No hay destinatario, no se envía correo")
        return

    if not (SMTP_USER and SMTP_PASS):
        print("SMTP no configurado (faltan SMTP_USER/SMTP_PASS), no se envía correo")
        return

    cuerpo = f"""
Han escrito un nuevo comentario en Kalendas.

Evento: {nombreEvento}
Usuario: {comentario.get("usuario")}
Comentario: {comentario.get("texto")}
Calificación: {comentario.get("calificacion", "-")}
"""

    msg = MIMEText(cuerpo)
    msg["Subject"] = "Nuevo comentario en Kalendas"
    msg["From"] = SMTP_USER
    msg["To"] = destinatario

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


async def get_comentarios_evento(evento_id: str):
    """Obtiene los comentarios de un evento en concreto"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COMENTARIO_SERVICE_URL}/api_comentarios/v1/comentarios/evento/{evento_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de calendario no disponible: {str(e)}")


async def actualizar_comentario(comentario_id: str, data: dict):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.put(
                f"{COMENTARIO_SERVICE_URL}/api_comentarios/v1/comentarios/{comentario_id}",
                json=data
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de comentarios no disponible: {str(e)}")



async def crear_comentario(data: dict):
    # 1) Leemos si hay que enviar correo y a qué correo
    notificacion = bool(data.get("notificacion"))  # checkbox activado
    correo = data.get("correo")
    nombreEvento = data.get("nombreEvento")

    # 2) Preparamos el payload para el microservicio de comentarios (sin el correo)
    payload = data.copy()
    payload.pop("correo", None)  # NO se guarda en BD
    payload.pop("nombreEvento", None)  # NO se guarda en BD

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{COMENTARIO_SERVICE_URL}/api_comentarios/v1/comentarios",
                json=payload
            )
            r.raise_for_status()
            comentario_creado = r.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de comentarios no disponible: {str(e)}")

    # 3) Si el checkbox estaba activado y hay correo, enviamos email
    if (not notificacion) and correo:
        try:
            enviar_correo_comentario(correo, comentario_creado, nombreEvento)
        except Exception as e:
            # No tiramos la app si falla el correo, solo lo logueamos
            print(f"Error enviando correo de comentario: {e}")

    return comentario_creado

async def obtener_notificaciones_organizador(organizador: str):
    """
    Obtiene las notificaciones de un organizador en concreto desde el microservicio
    de comentarios y enriquece cada una con el nombre del evento.
    """
    # 1) Pedimos primero las notificaciones al microservicio de comentarios
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{COMENTARIO_SERVICE_URL}/api_comentarios/v1/comentarios/organizador/{organizador}"
            )
            response.raise_for_status()
            notificaciones = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Servicio de comentarios no disponible: {str(e)}"
            )

    # 2) Para cada notificación, intentamos obtener el evento y añadir su nombre
    if not isinstance(notificaciones, list):
        # Por seguridad, si el microservicio devolviera otra cosa rara
        return notificaciones

    for notif in notificaciones:
        evento_id = notif.get("evento")
        if not evento_id:
            continue

        try:
            # Llamamos al servicio de eventos (otro microservicio)
            evento = await EventoService.get_evento_id(str(evento_id))
        except Exception:
            # Si falla, no rompemos toda la respuesta; simplemente seguimos
            evento = None

        # get_evento_id devuelve [] si no encuentra nada
        if isinstance(evento, dict):
            nombre_evento = (
                evento.get("nombre")
                or evento.get("titulo")
                or evento.get("nombreEvento")
            )
            if nombre_evento:
                notif["nombreEvento"] = nombre_evento

    return notificaciones

async def eliminar_comentario(comentario_id: str):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.delete(
                f"{COMENTARIO_SERVICE_URL}/api_comentarios/v1/comentarios/{comentario_id}"
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Servicio de comentarios no disponible: {str(e)}")

