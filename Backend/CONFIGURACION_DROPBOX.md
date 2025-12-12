# Configuración de Dropbox para Kalendas

## Paso 1: Crear una aplicación en Dropbox

1. Ve a https://www.dropbox.com/developers/apps
2. Haz clic en "Create app"
3. Selecciona:
   - **API**: Scoped access
   - **Type of access**: Full Dropbox
   - **Name**: Kalendas (o el nombre que prefieras)
4. Haz clic en "Create app"

## Paso 2: Configurar permisos

En la página de tu aplicación:

1. Ve a la pestaña "Permissions"
2. Asegúrate de tener los siguientes permisos marcados:
   - `files.metadata.write`
   - `files.metadata.read`
   - `files.content.write`
   - `files.content.read`
   - `sharing.write`
   - `sharing.read`
3. Haz clic en "Submit" para guardar los cambios

## Paso 3: Obtener credenciales

### App Key y App Secret

En la pestaña "Settings" de tu aplicación:
- **App key**: Copia este valor
- **App secret**: Haz clic en "Show" y copia el valor

### Refresh Token

Para obtener el refresh token, necesitas autorizar la aplicación:

#### Opción 1: Usando el script de Python (Recomendado)

1. Crea un archivo llamado `get_dropbox_token.py` con el siguiente contenido:

```python
import requests

APP_KEY = "tu_app_key_aqui"  # Reemplaza con tu App Key
APP_SECRET = "tu_app_secret_aqui"  # Reemplaza con tu App Secret

# Paso 1: Imprime la URL de autorización
auth_url = f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&token_access_type=offline&response_type=code"
print("1. Abre esta URL en tu navegador:")
print(auth_url)
print("\n2. Autoriza la aplicación y copia el código de la URL")

# Paso 2: Pega el código aquí
code = input("\n3. Pega el código aquí: ")

# Paso 3: Intercambia el código por el refresh token
response = requests.post(
    "https://api.dropbox.com/oauth2/token",
    data={
        "code": code,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }
)

if response.status_code == 200:
    data = response.json()
    print("\n✅ ¡Éxito! Tu Refresh Token es:")
    print(data["refresh_token"])
    print("\nGuárdalo en tu archivo .env")
else:
    print(f"❌ Error: {response.text}")
```

2. Ejecuta el script:
   ```bash
   python get_dropbox_token.py
   ```

3. Sigue las instrucciones en pantalla:
   - Abre la URL que se muestra
   - Autoriza la aplicación en Dropbox
   - Copia el código de la URL de redirección
   - Pega el código en el script
   - El script te mostrará tu Refresh Token

#### Opción 2: Manualmente

1. En la pestaña "Settings", en la sección "OAuth 2":
   - **Redirect URIs**: Añade `http://localhost` (sin puerto)

2. Construye esta URL (reemplaza `YOUR_APP_KEY` con tu App Key):
   ```
   https://www.dropbox.com/oauth2/authorize?client_id=YOUR_APP_KEY&token_access_type=offline&response_type=code
   ```

3. Abre esa URL en tu navegador y autoriza la aplicación

4. Serás redirigido a una URL como:
   ```
   http://localhost/?code=AUTHORIZATION_CODE
   ```
   Copia el `AUTHORIZATION_CODE` (todo el texto después de `code=`)

5. **En PowerShell**, ejecuta:
   ```powershell
   $body = @{
       code = "EL_CODIGO_QUE_COPIASTE"
       grant_type = "authorization_code"
       client_id = "YOUR_APP_KEY"
       client_secret = "YOUR_APP_SECRET"
   }

   $response = Invoke-RestMethod -Uri "https://api.dropbox.com/oauth2/token" -Method Post -Body $body
   $response | ConvertTo-Json
   ```

   **O en bash/curl**:
   ```bash
   curl https://api.dropbox.com/oauth2/token \
     -d code=AUTHORIZATION_CODE \
     -d grant_type=authorization_code \
     -d client_id=YOUR_APP_KEY \
     -d client_secret=YOUR_APP_SECRET
   ```

6. En la respuesta JSON, busca el campo `refresh_token`. Este es tu token permanente:
   ```json
   {
     "access_token": "...",
     "token_type": "bearer",
     "expires_in": 14400,
     "refresh_token": "ESTE_ES_TU_REFRESH_TOKEN",
     "scope": "...",
     "uid": "...",
     "account_id": "..."
   }
   ```

## Paso 4: Configurar variables de entorno

Crea un archivo `.env` en la carpeta `app/` con el siguiente contenido:

```env
DROPBOX_APP_KEY=tu_app_key_aqui
DROPBOX_APP_SECRET=tu_app_secret_aqui
DROPBOX_REFRESH_TOKEN=tu_refresh_token_aqui
```

## Paso 5: Instalar dependencias

```bash
pip install dropbox requests
```

O si usas el archivo requirements.txt:

```bash
pip install -r requirements.txt
```

## Uso en la aplicación

Una vez configurado, la aplicación podrá:

- ✅ Subir imágenes a Dropbox
- ✅ Obtener enlaces públicos para visualizar imágenes
- ✅ Listar imágenes por calendario
- ✅ Eliminar imágenes

Las imágenes se organizarán en carpetas por calendario:
```
/kalendas/calendarios/{calendario_id}/imagen.jpg
```

## Endpoints disponibles

- `POST /calendario/{calendario_id}/upload-image` - Subir imagen
- `GET /calendario/{calendario_id}/imagenes` - Listar imágenes
- `DELETE /imagen?ruta={ruta}` - Eliminar imagen

## Notas de seguridad

⚠️ **IMPORTANTE**: 
- Nunca subas el archivo `.env` a tu repositorio
- Añade `.env` a tu `.gitignore`
- El refresh token es **permanente** hasta que sea revocado manualmente
- Guarda tus credenciales de forma segura
- No compartas tus tokens en lugares públicos

