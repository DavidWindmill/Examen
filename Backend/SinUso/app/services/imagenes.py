import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata, WriteMode, ListFolderResult
from dropbox.sharing import ListSharedLinksResult
import requests
import os
from typing import Optional, List, Dict, Any

# Configuración de Dropbox - Obtener desde variables de entorno o configuración
APP_KEY = os.getenv('DROPBOX_APP_KEY', '')
APP_SECRET = os.getenv('DROPBOX_APP_SECRET', '')
REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN', '')

def renovar_access_token():
    """Renueva el access token de Dropbox usando el refresh token."""
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            print(f"✓ Access Token renovado exitosamente")
            return access_token
        else:
            print(f"✗ Error al renovar el token: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Excepción al renovar token: {e}")
        return None

# Inicializar cliente de Dropbox
ACCESS_TOKEN = renovar_access_token()
if ACCESS_TOKEN:
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
else:
    print("⚠ No se pudo obtener un Access Token válido.")
    dbx = None

def generar_nombre_unico(ruta_remota: str) -> str:
    """Genera un nombre único si el archivo ya existe en Dropbox."""
    if not dbx:
        return ruta_remota
    
    try:
        dbx.files_get_metadata(ruta_remota)
        # Si llegamos aquí, el archivo ya existe, generamos un nuevo nombre
        nombre, extension = ruta_remota.rsplit('.', 1) if '.' in ruta_remota else (ruta_remota, '')
        contador = 1
        while True:
            nuevo_nombre = f"{nombre} ({contador})"
            if extension:
                nuevo_nombre += f".{extension}"
            nuevo_ruta_remota = f"/{nuevo_nombre}" if not nuevo_nombre.startswith('/') else nuevo_nombre
            try:
                dbx.files_get_metadata(nuevo_ruta_remota)
            except ApiError:
                # Si no existe, devolvemos el nuevo nombre
                return nuevo_ruta_remota
            contador += 1
    except ApiError:
        # Si no existe, devolvemos el nombre original
        return ruta_remota

def subir_imagen_dropbox(ruta_local: str, ruta_remota: str) -> Optional[str]:
    """
    Sube una imagen a Dropbox.
    
    Args:
        ruta_local: Ruta local del archivo a subir
        ruta_remota: Ruta donde se guardará en Dropbox
        
    Returns:
        URL de la imagen subida o None si falla
    """
    if not dbx:
        print("✗ Cliente de Dropbox no inicializado")
        return None
    
    # Asegurar que la ruta remota comience con /
    if not ruta_remota.startswith('/'):
        ruta_remota = f"/{ruta_remota}"
    
    ruta_remota = generar_nombre_unico(ruta_remota)
    
    try:
        with open(ruta_local, 'rb') as archivo:
            dbx.files_upload(archivo.read(), ruta_remota, mode=WriteMode.overwrite)
            print(f"✓ Imagen subida a {ruta_remota}")
            
            # Obtener enlace de la imagen
            return obtener_enlace_imagen(ruta_remota)
    except FileNotFoundError:
        print(f"✗ Archivo no encontrado: {ruta_local}")
        return None
    except Exception as e:
        print(f"✗ Error al subir el archivo: {e}")
        return None

def obtener_enlace_imagen(ruta_remota: str) -> Optional[str]:
    """
    Obtiene un enlace público para visualizar la imagen.
    
    Args:
        ruta_remota: Ruta del archivo en Dropbox
        
    Returns:
        URL directa de la imagen o None si falla
    """
    if not dbx:
        print("✗ Cliente de Dropbox no inicializado")
        return None
    
    # Asegurar que la ruta remota comience con /
    if not ruta_remota.startswith('/'):
        ruta_remota = f"/{ruta_remota}"
    
    try:
        # Intentar obtener enlace compartido existente
        enlace_compartido = None
        try:
            enlaces: Optional[ListSharedLinksResult] = dbx.sharing_list_shared_links(path=ruta_remota)
            if enlaces and enlaces.links:
                enlace_compartido = enlaces.links[0].url
            else:
                # Crear nuevo enlace compartido
                resultado_enlace = dbx.sharing_create_shared_link_with_settings(ruta_remota)
                if resultado_enlace:
                    enlace_compartido = resultado_enlace.url
        except Exception:
            # Crear nuevo enlace compartido
            resultado_enlace = dbx.sharing_create_shared_link_with_settings(ruta_remota)
            if resultado_enlace:
                enlace_compartido = resultado_enlace.url
        
        if not enlace_compartido:
            print("✗ No se pudo generar un enlace compartido")
            return None
        
        # Modificar el enlace para visualización directa
        # Cambiar dl=0 por dl=1 para descarga directa, o usar raw=1 para visualización
        # www.dropbox.com -> dl.dropboxusercontent.com para enlaces directos
        if 'www.dropbox.com' in enlace_compartido:
            enlace_descarga = enlace_compartido.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '')
        else:
            enlace_descarga = enlace_compartido.replace('?dl=0', '?raw=1')
        
        print(f"✓ Enlace generado: {enlace_descarga}")
        return enlace_descarga
    except ApiError as e:
        print(f"✗ Error al obtener el enlace: {e}")
        return None
    except Exception as e:
        print(f"✗ Excepción al obtener enlace: {e}")
        return None

def eliminar_imagen_dropbox(ruta_remota: str) -> bool:
    """
    Elimina una imagen de Dropbox.
    
    Args:
        ruta_remota: Ruta del archivo en Dropbox
        
    Returns:
        True si se eliminó exitosamente, False en caso contrario
    """
    if not dbx:
        print("✗ Cliente de Dropbox no inicializado")
        return False
    
    # Asegurar que la ruta remota comience con /
    if not ruta_remota.startswith('/'):
        ruta_remota = f"/{ruta_remota}"
    
    try:
        dbx.files_delete_v2(ruta_remota)
        print(f"✓ Imagen eliminada: {ruta_remota}")
        return True
    except ApiError as e:
        print(f"✗ Error al eliminar imagen: {e}")
        return False
    except Exception as e:
        print(f"✗ Excepción al eliminar imagen: {e}")
        return False

def listar_imagenes_dropbox(carpeta: str = "") -> List[Dict[str, Any]]:
    """
    Lista todas las imágenes en una carpeta de Dropbox.
    
    Args:
        carpeta: Carpeta a listar (vacío para raíz)
        
    Returns:
        Lista de archivos con sus metadatos
    """
    if not dbx:
        print("✗ Cliente de Dropbox no inicializado")
        return []
    
    try:
        ruta_carpeta = f"/{carpeta}" if carpeta else ""
        resultado: Optional[ListFolderResult] = dbx.files_list_folder(ruta_carpeta)
        
        if not resultado:
            return []
            
        archivos: List[Dict[str, Any]] = []
        
        for entry in resultado.entries:
            if isinstance(entry, FileMetadata):
                
                # Filtrar solo archivos de imagen
                if entry.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                    archivos.append({
                        'nombre': entry.name,
                        'ruta': entry.path_display,
                        'tamaño': entry.size,
                        'modificado': entry.client_modified
                    })
        
        return archivos
    except ApiError as e:
        print(f"✗ Error de API al listar imágenes: {e}")
        return []
    except Exception as e:
        print(f"✗ Error al listar imágenes: {e}")
        return []
