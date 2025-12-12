import os
import dropbox
import certifi
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_BASE_FOLDER = os.getenv("DROPBOX_BASE_FOLDER", "/kalendas")

def get_dbx() -> dropbox.Dropbox:
    if not (DROPBOX_APP_KEY and DROPBOX_APP_SECRET and DROPBOX_REFRESH_TOKEN):
        raise RuntimeError("Faltan variables de entorno de Dropbox")
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET,
        ca_certs=certifi.where(),
    )

def _public_raw(url: str) -> str:
    return url.replace("?dl=0", "?raw=1")

async def upload_image_bytes(content: bytes, dropbox_path: str) -> tuple[str, str]:
    dbx = get_dbx()
    dbx.files_upload(content, dropbox_path, mode=WriteMode("overwrite"))

    try:
        url = dbx.sharing_create_shared_link_with_settings(dropbox_path).url
    except ApiError as e:
        # si ya existe, lo reutilizamos
        if "shared_link_already_exists" in str(e).lower():
            links = dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True).links
            url = links[0].url if links else dbx.sharing_create_shared_link_with_settings(dropbox_path).url
        else:
            raise

    return _public_raw(url), dropbox_path

async def delete_dropbox_path(dropbox_path: str) -> None:
    dbx = get_dbx()
    try:
        dbx.files_delete_v2(dropbox_path)
    except ApiError:
        pass
