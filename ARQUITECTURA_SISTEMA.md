# Arquitectura del Sistema Kalendas

## 📋 Resumen

Kalendas es una aplicación de gestión de calendarios y eventos construida con arquitectura de microservicios.

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Navegador)                      │
│                    Templates Jinja2 + JS                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              API GATEWAY (Puerto 8000)                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │  routes/rutas_calendario.py   (Endpoints HTTP)     │     │
│  │  routes/rutas_frontend.py     (Páginas HTML)       │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     ↓                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │  services/calendario.py   (Cliente HTTP → :8002)   │     │
│  │  services/evento.py       (Cliente HTTP → :8001)   │     │
│  │  services/comentario.py   (Cliente HTTP → :8003)   │     │
│  │  services/imagenes.py     (Cliente Dropbox)        │     │
│  └────────────────────────────────────────────────────┘     │
└────────┬──────────────┬──────────────┬─────────────────────┘
         │              │              │
         ↓              ↓              ↓
┌────────────┐  ┌─────────────┐  ┌────────────────┐
│ Calendario │  │   Eventos   │  │  Comentarios   │
│  :8002     │  │    :8001    │  │     :8003      │
└─────┬──────┘  └──────┬──────┘  └────────┬───────┘
      │                │                   │
      └────────────────┴───────────────────┘
                       ↓
              ┌────────────────┐
              │  MongoDB Atlas │
              └────────────────┘
```

## 🔌 Puertos y URLs

### Desarrollo Local
- **API Gateway**: `http://localhost:8000`
- **Servicio Calendario**: `http://localhost:8002`
- **Servicio Eventos**: `http://localhost:8001`
- **Servicio Comentarios**: `http://localhost:8003`

### Docker (Producción)
- **API Gateway**: `http://kalendas-gateway:8000` (externo: `localhost:8000`)
- **Servicio Calendario**: `http://servicio-calendario:8002`
- **Servicio Eventos**: `http://servicio-eventos:8001`
- **Servicio Comentarios**: `http://servicio-comentarios:8003`

## 📁 Estructura de Archivos

```
Backend/
├── .env                          # Variables de entorno
├── docker-compose.yml            # Orquestación de servicios
│
├── app/                          # API GATEWAY
│   ├── main.py                   # Aplicación principal
│   ├── routes/
│   │   ├── rutas_calendario.py   # Endpoints /calendario/*
│   │   └── rutas_frontend.py     # Endpoints páginas HTML
│   ├── services/
│   │   ├── calendario.py         # Cliente HTTP → Microservicio Calendario
│   │   ├── evento.py             # Cliente HTTP → Microservicio Eventos
│   │   ├── comentario.py         # Cliente HTTP → Microservicio Comentarios
│   │   └── imagenes.py           # Cliente Dropbox API
│   ├── templates/                # Plantillas HTML
│   └── static/                   # CSS, JS, imágenes
│
├── servicioCalendario/           # MICROSERVICIO CALENDARIO (:8002)
│   ├── main.py                   # FastAPI app
│   ├── models.py                 # Modelos Beanie
│   ├── bd.py                     # Conexión MongoDB
│   └── services/
│       └── calendario.py         # Lógica de negocio + MongoDB
│
├── servicioEventos/              # MICROSERVICIO EVENTOS (:8001)
│   ├── main.py
│   ├── models.py
│   ├── bd.py
│   └── services/
│       └── evento.py
│
└── servicioComentarios/          # MICROSERVICIO COMENTARIOS (:8003)
    ├── main.py
    ├── models.py
    ├── bd.py
    └── services/
        └── comentario.py
```

## 🔄 Flujo de Datos

### Ejemplo: Crear un Calendario

```
1. Usuario completa formulario → Frontend
   └─→ POST /calendario/crear (Form Data)

2. API Gateway (rutas_calendario.py)
   └─→ CalendarioService.crear_calendario()

3. Cliente HTTP (services/calendario.py)
   └─→ POST http://servicio-calendario:8002/api/v1/calendarios (JSON)

4. Microservicio Calendario (servicioCalendario/main.py)
   └─→ services/calendario.py → crearCalendario()

5. MongoDB
   └─→ Guarda nuevo documento

6. Respuesta JSON ← Microservicio
   └─→ ← Cliente HTTP
       └─→ ← API Gateway
           └─→ RedirectResponse("/calendarios") ← Frontend
```

### Ejemplo: Editar un Calendario

```
1. Usuario edita y guarda → Frontend (JavaScript fetch)
   └─→ PUT /calendario/{id} (FormData)

2. API Gateway (rutas_calendario.py)
   └─→ CalendarioService.actualizar_calendario()

3. Cliente HTTP (services/calendario.py)
   └─→ PUT http://servicio-calendario:8002/api/v1/calendarios/{id} (JSON)

4. Microservicio Calendario
   └─→ Actualiza en MongoDB

5. Respuesta JSON {"success": true}
   └─→ Frontend recarga la página
```

## 🎯 Métodos HTTP (RESTful)

| Método | Ruta | Descripción |
|--------|------|-------------|
| **GET** | `/calendario/{id}` | Obtener calendario |
| **POST** | `/calendario/crear` | Crear calendario |
| **PUT** | `/calendario/{id}` | Actualizar calendario |
| **DELETE** | `/calendario/{id}` | Eliminar calendario |
| **GET** | `/calendario/{id}/imagenes` | Listar imágenes |
| **POST** | `/calendario/{id}/upload-image` | Subir imagen |
| **DELETE** | `/calendario/imagen?ruta=...` | Eliminar imagen |

## 🔐 Variables de Entorno

```env
# MongoDB
MONGO_USERNAME=admin
MONGO_PASSWORD=admin
MONGO_DB_NAME=Kalendas

# URLs Microservicios (Docker)
EVENTOS_SERVICE_URL=http://servicio-eventos:8001
CALENDARIO_SERVICE_URL=http://servicio-calendario:8002
COMENTARIO_SERVICE_URL=http://servicio-comentarios:8003

# Dropbox
DROPBOX_APP_KEY=tu_app_key
DROPBOX_APP_SECRET=tu_app_secret
DROPBOX_REFRESH_TOKEN=tu_refresh_token
```

## 🚀 Ejecución

### Con Docker (Recomendado)
```bash
cd Backend
docker-compose up --build
```

### Desarrollo Local
```bash
# Terminal 1: Calendario
cd Backend/servicioCalendario
uvicorn main:app --host 0.0.0.0 --port 8002

# Terminal 2: Eventos
cd Backend/servicioEventos
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3: Comentarios
cd Backend/servicioComentarios
uvicorn main:app --host 0.0.0.0 --port 8003

# Terminal 4: Gateway
cd Backend/app
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 Convenciones

### Nombres de Funciones

#### API Gateway (`app/services/*.py`)
- Formato: `verbo_objeto()` (snake_case)
- Ejemplos: `get_calendarios()`, `crear_calendario()`, `eliminar_calendario()`

#### Microservicios (`servicio*/services/*.py`)
- Formato: `verboObjeto()` (camelCase)
- Ejemplos: `getTodosLosCalendarios()`, `crearCalendario()`, `eliminarCalendario()`

### Endpoints

#### API Gateway
- Prefijo: `/calendario/*`
- Ejemplos: `/calendario/crear`, `/calendario/{id}`, `/calendario/{id}/imagenes`

#### Microservicios
- Prefijo: `/api/v1/calendarios/*`
- Ejemplos: `/api/v1/calendarios`, `/api/v1/calendarios/{id}`

## 🎨 Frontend

### Tecnologías
- **Templates**: Jinja2
- **CSS**: Bootstrap 5 + Custom CSS
- **JavaScript**: Vanilla JS (Fetch API)
- **Temas**: Verde Moco y Rosa Pastel

### Páginas
- `/calendarios` - Listado de calendarios
- `/calendario/{id}` - Detalle de calendario
- `/` - Vista de calendario mensual
- `/evento/{id}` - Detalle de evento

## 🔧 Servicios Externos

### Dropbox
- **Uso**: Almacenamiento de imágenes de calendarios
- **Carpeta**: `/kalendas/calendarios/{calendario_id}/`
- **Funciones**: Subir, listar, eliminar imágenes

### MongoDB Atlas
- **Base de datos**: Kalendas
- **Colecciones**: calendarios, eventos, comentarios

## ✅ Coherencia del Sistema

1. **Puertos consistentes**: Gateway (8000), Eventos (8001), Calendario (8002), Comentarios (8003)
2. **Variables de entorno**: Centralizadas en `.env`
3. **Comunicación**: HTTP/JSON entre servicios
4. **Métodos REST**: GET, POST, PUT, DELETE correctamente implementados
5. **Naming**: Coherencia en nombres de servicios y endpoints
6. **Error handling**: HTTPException en todos los servicios
