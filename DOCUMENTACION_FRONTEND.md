# Documentación del Frontend - Kalendas

## Tabla de Contenidos
1. [Página Principal (Homepage)](#página-principal-homepage)
2. [Página de Detalles del Calendario](#página-de-detalles-del-calendario)
3. [Funcionalidad de Búsqueda](#funcionalidad-de-búsqueda)

---

## Página Principal (Homepage)

### Ruta
- **URL**: `/`
- **Método**: GET
- **Parámetros de Query**: 
  - `q` (opcional): Query de búsqueda para filtrar calendarios

### Descripción
La página principal muestra todos los calendarios disponibles en formato de tarjetas con mini-calendarios del mes actual. Para usuarios propietarios (owners), incluye funcionalidades adicionales de gestión.

### Funcionalidades

#### Para Todos los Usuarios
- **Visualización de Calendarios**: Muestra todos los calendarios en una cuadrícula responsive
- **Mini-Calendario**: Cada tarjeta muestra un calendario en miniatura del mes actual con:
  - Nombre del mes y año
  - Días de la semana
  - Días del mes
  - Indicador visual del día actual (resaltado en verde)
- **Navegación**: Click en cualquier tarjeta para ir a los detalles del calendario
- **Búsqueda**: Barra de búsqueda en la parte superior derecha para filtrar calendarios

#### Para Usuarios Propietarios (is_owner = True)
- **Crear Calendario**: Primera tarjeta con icono "+" para crear nuevos calendarios
- **Eliminar Calendario**: Botón "×" en la esquina superior derecha de cada tarjeta
- **Confirmación de Eliminación**: Diálogo de confirmación antes de eliminar

### Componentes de la Interfaz

#### Header Section
```
┌─────────────────────────────────────────────┐
│ Kalendas                    [🔍 Buscar]     │
│ Sistema de gestión...                       │
└─────────────────────────────────────────────┘
```

#### Cuadrícula de Calendarios
```
┌──────────┐ ┌──────────┐ ┌──────────┐
│    +     │ │ Título 1 │ │ Título 2 │
│          │ │ Nov 2025 │ │ Nov 2025 │
│  Crear   │ │ L M X... │ │ L M X... │
└──────────┘ └──────────┘ └──────────┘
```

### Modal de Creación de Calendario

#### Campos
- **Título del Calendario** (requerido): Texto
- **Organizador** (requerido): Texto

#### Acciones
- **Crear**: Envía formulario y recarga la página
- **Cancelar**: Cierra el modal sin cambios

### Implementación Backend

```python
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str = Query(None)):
    """Página principal con búsqueda opcional"""
```

**Parámetros Pasados al Template**:
- `calendarios`: Lista de calendarios (filtrados si hay búsqueda)
- `calendar_days`: Array de días del mes para mini-calendarios
- `current_month`: Nombre del mes en español
- `current_year`: Año actual
- `is_owner`: Boolean (siempre True actualmente)
- `search_query`: Query de búsqueda (si existe)
- `is_searching`: Boolean indicando si se está mostrando resultados de búsqueda

---

## Página de Detalles del Calendario

### Ruta
- **URL**: `/calendario/{calendario_id}`
- **Método**: GET
- **Parámetros de Path**: 
  - `calendario_id`: ID del calendario a visualizar
- **Parámetros de Query**: 
  - `q` (opcional): Query de búsqueda (para preservar contexto de navegación)

### Descripción
Muestra información detallada de un calendario específico con un calendario completo del mes actual mostrando todos los eventos asociados.

### Funcionalidades

#### Para Todos los Usuarios
- **Botón Volver**: Retorna a la página principal (o a resultados de búsqueda si se vino desde ahí)
- **Visualización de Información**:
  - Título del calendario
  - Organizador
  - Etiquetas/Tags
- **Calendario Completo**: Vista mensual con:
  - Días organizados por semana (Lunes a Domingo)
  - Eventos mostrados dentro de cada día
  - Día actual resaltado
  - Múltiples eventos por día si existen

#### Para Usuarios Propietarios (is_owner = True)
- **Editar Título**: Botón "Editar" junto al título para modificarlo
- **Añadir Etiquetas**: Formulario para agregar nuevas etiquetas
- **Eliminar Etiquetas**: Botón "×" en cada etiqueta para removerla

### Layout de la Página

```
┌─────────────────────────────────────────────────────┐
│ ← Volver a Calendarios                              │
│                                                      │
│ Título del Calendario                               │
│                                                      │
│ ┌──────────┐  ┌──────────────────────────────────┐ │
│ │ Info     │  │ Calendario Completo              │ │
│ │ Sidebar  │  │                                  │ │
│ │          │  │ Lun Mar Mié Jue Vie Sáb Dom     │ │
│ │ Título   │  │ ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐   │ │
│ │ Org.     │  │ │1 ││2 ││3 ││4 ││5 ││6 ││7 │   │ │
│ │ Tags     │  │ └──┘└──┘└──┘└──┘└──┘└──┘└──┘   │ │
│ └──────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Sidebar de Información

#### Sección Título
- **Modo Vista**: Muestra el título con botón "Editar" (solo owner)
- **Modo Edición**: Input de texto con botones "Guardar" y "Cancelar"

#### Sección Organizador
- **Campo de solo lectura** mostrando el nombre del organizador

#### Sección Etiquetas
- **Lista de tags** existentes (con botón × para eliminar si es owner)
- **Formulario "Añadir"** (solo owner): Input de texto + botón "Añadir"

### Calendario de Eventos

#### Estructura de Cada Día
```
┌─────────────┐
│ 15          │  ← Número del día
│ ┌─────────┐ │
│ │ Evento1 │ │  ← Cajas de eventos
│ └─────────┘ │
│ ┌─────────┐ │
│ │ Evento2 │ │
│ └─────────┘ │
└─────────────┘
```

#### Características
- **Días del mes anterior**: Color gris claro
- **Días del mes actual**: Borde sólido, fondo blanco
- **Día actual**: Fondo verde, texto blanco
- **Eventos**: Cajas azules con título del evento
- **Tooltip**: Hover sobre evento muestra título completo

### Implementación Backend

```python
@app.get("/calendario/{calendario_id}", response_class=HTMLResponse)
async def calendar_detail(request: Request, calendario_id: str, q: str = Query(None)):
    """Página de detalle del calendario"""
```

**Parámetros Pasados al Template**:
- `calendario`: Objeto con toda la información del calendario
- `calendar_days`: Array de días con eventos asociados
- `current_month`: Nombre del mes en español
- `current_year`: Año actual
- `is_owner`: Boolean (siempre True actualmente)
- `back_url`: URL para el botón volver (preserva búsqueda)

### Endpoints de Gestión

#### Actualizar Título
- **Ruta**: POST `/calendario/{calendario_id}/update-title`
- **Form Data**: `titulo`
- **Acción**: Actualiza el título y redirige a la página de detalles

#### Añadir Etiqueta
- **Ruta**: POST `/calendario/{calendario_id}/add-tag`
- **Form Data**: `tag`
- **Acción**: Añade una etiqueta y redirige a la página de detalles

#### Eliminar Etiqueta
- **Ruta**: POST `/calendario/{calendario_id}/remove-tag`
- **Form Data**: `tag`
- **Acción**: Remueve la etiqueta de la lista y redirige a la página de detalles

---

## Funcionalidad de Búsqueda

### Descripción
Sistema de búsqueda integrado que permite filtrar calendarios por título, organizador o etiquetas.

### Ubicación
Esquina superior derecha de la página principal, dentro de un formulario de búsqueda.

### Características

#### Campo de Búsqueda
- **Placeholder**: "Buscar calendarios..."
- **Tipo**: Input de texto
- **Icono**: 🔍 (emoji de lupa)
- **Método**: GET (query parameter)

#### Criterios de Búsqueda
La búsqueda es **case-insensitive** y busca en:
1. **Título del calendario**: Coincidencia parcial en el nombre
2. **Organizador**: Coincidencia parcial en el nombre del organizador
3. **Etiquetas**: Coincidencia parcial en cualquier tag del calendario

#### Lógica de Filtrado
- Un calendario aparece en los resultados si la query coincide con **cualquiera** de los tres criterios
- La búsqueda es inclusiva (OR entre criterios)
- Búsqueda por substring (no requiere coincidencia exacta)

### Implementación Backend

```python
async def buscar_calendarios(query: str):
    """Busca calendarios por título, organizador o tags"""
    calendarios = await get_calendarios()
    query_lower = query.lower()
    
    resultados = []
    for calendario in calendarios:
        # Buscar en título
        if query_lower in calendario.get('titulo', '').lower():
            resultados.append(calendario)
            continue
        
        # Buscar en organizador
        if query_lower in calendario.get('organizador', '').lower():
            resultados.append(calendario)
            continue
        
        # Buscar en tags
        if calendario.get('palabras_claves'):
            for tag in calendario['palabras_claves']:
                if query_lower in tag.lower():
                    resultados.append(calendario)
                    break
    
    return resultados
```

### Interfaz de Resultados

#### Banner de Información
Cuando hay una búsqueda activa, se muestra:
```
┌────────────────────────────────────────────┐
│ Resultados de búsqueda para: "query"      │
│ (X encontrados)                            │
│ [← Volver a todos los calendarios]         │
└────────────────────────────────────────────┘
```

#### Botón de Retorno
- **Texto**: "← Volver a todos los calendarios"
- **Acción**: Limpia la búsqueda y muestra todos los calendarios
- **URL**: `/` (sin parámetros)

### Preservación de Contexto

#### Navegación desde Búsqueda
Cuando un usuario:
1. Realiza una búsqueda
2. Click en un calendario de los resultados
3. Ve los detalles del calendario
4. Click en "Volver"

→ **Regresa a los resultados de búsqueda**, no a la página principal sin filtrar

#### Implementación
- Los enlaces a calendarios incluyen el parámetro `q` si hay búsqueda activa
- El botón "Volver" en detalles usa `back_url` dinámico:
  - `/?q={query}` si vino de búsqueda
  - `/` si vino de la página principal

### Ejemplos de Uso

#### Ejemplo 1: Búsqueda por Título
- Query: "trabajo"
- Resultados: Calendarios con "trabajo", "Trabajo equipo", "trabajo final", etc.

#### Ejemplo 2: Búsqueda por Organizador
- Query: "juan"
- Resultados: Calendarios organizados por "Juan Pérez", "Juana García", etc.

#### Ejemplo 3: Búsqueda por Tag
- Query: "deportes"
- Resultados: Calendarios que tengan "deportes" en sus etiquetas

#### Ejemplo 4: Búsqueda Múltiple
- Query: "universidad"
- Resultados: Calendarios que contengan "universidad" en:
  - Título: "Calendario Universidad"
  - Organizador: "Universidad de Chile"
  - Tags: ["universidad", "académico"]

---

## Gestión de Calendarios (Solo Propietarios)

### Crear Calendario

#### Endpoint
- **Ruta**: POST `/calendario/crear`
- **Tipo**: Form submission

#### Datos del Formulario
```
titulo: string (requerido)
organizador: string (requerido)
```

#### Flujo
1. Usuario click en tarjeta "+"
2. Se abre modal con formulario
3. Usuario completa campos
4. Submit → POST al endpoint
5. Redirección a homepage (303)

### Eliminar Calendario

#### Endpoint
- **Ruta**: POST `/calendario/{calendario_id}/delete`
- **Tipo**: Form submission

#### Flujo
1. Usuario click en botón "×" de una tarjeta
2. Confirmación JavaScript: "¿Estás seguro...?"
3. Si acepta → POST al endpoint
4. Redirección a homepage (303)

### Actualizar Título del Calendario

#### Endpoint
- **Ruta**: POST `/calendario/{calendario_id}/update-title`
- **Tipo**: Form submission

#### Datos del Formulario
```
titulo: string (requerido)
```

#### Flujo
1. Click en "Editar" junto al título
2. Se muestra input de texto
3. Usuario modifica título
4. Click "Guardar" → POST al endpoint
5. Redirección a página de detalles (303)

### Gestión de Etiquetas

#### Añadir Etiqueta
- **Endpoint**: POST `/calendario/{calendario_id}/add-tag`
- **Form Data**: `tag`
- **Flujo**: Input → Submit → Redirección a detalles

#### Eliminar Etiqueta
- **Endpoint**: POST `/calendario/{calendario_id}/remove-tag`
- **Form Data**: `tag`
- **Flujo**: Click × → Submit → Actualiza lista → Redirección a detalles

---

## Servicios de Backend

### Servicio de Calendarios (`services/calendario.py`)

#### `get_calendarios()`
- **Descripción**: Obtiene todos los calendarios del microservicio
- **Retorna**: Lista de objetos calendario
- **URL del Servicio**: `{CALENDARIO_SERVICE_URL}/api/v1/calendarios`

#### `crear_calendario(titulo, organizador, palabras_claves)`
- **Descripción**: Crea un nuevo calendario
- **Parámetros**:
  - `titulo`: Nombre del calendario
  - `organizador`: Nombre del organizador
  - `palabras_claves`: Lista opcional de tags
- **Retorna**: Objeto calendario creado

#### `eliminar_calendario(calendario_id)`
- **Descripción**: Elimina un calendario por ID
- **Parámetros**: `calendario_id`
- **Retorna**: Respuesta de confirmación

#### `actualizar_calendario(calendario_id, datos)`
- **Descripción**: Actualiza campos de un calendario
- **Parámetros**:
  - `calendario_id`: ID del calendario
  - `datos`: Diccionario con campos a actualizar
- **Retorna**: Calendario actualizado

#### `añadir_palabra_clave(calendario_id, palabra_clave)`
- **Descripción**: Añade una etiqueta a un calendario
- **Parámetros**:
  - `calendario_id`: ID del calendario
  - `palabra_clave`: Tag a añadir
- **Retorna**: Calendario actualizado

#### `buscar_calendarios(query)`
- **Descripción**: Filtra calendarios por búsqueda
- **Parámetros**: `query` - Término de búsqueda
- **Retorna**: Lista de calendarios que coinciden
- **Lógica**: Búsqueda case-insensitive en título, organizador y tags

### Servicio de Eventos (`services/evento.py`)

#### `get_eventos_por_calendario(calendario_id)`
- **Descripción**: Obtiene todos los eventos de un calendario
- **Parámetros**: `calendario_id`
- **Retorna**: Lista de eventos
- **URL del Servicio**: `{EVENTOS_SERVICE_URL}/api_eventos/v1/evento/calendario/{id}`
- **Manejo de Errores**: Retorna lista vacía si no hay eventos (404)

---

## Generación de Calendario

### Función `generate_calendar_days(year, month, eventos)`

#### Descripción
Genera un array de 42 días (6 semanas × 7 días) para mostrar un calendario completo del mes.

#### Parámetros
- `year`: Año del calendario
- `month`: Mes del calendario (1-12)
- `eventos`: Lista opcional de eventos a mostrar en el calendario

#### Retorno
Array de objetos día con estructura:
```python
{
    'day': int,              # Número del día
    'is_today': bool,        # Si es el día actual
    'is_other_month': bool,  # Si pertenece a otro mes
    'events': []             # Lista de eventos del día
}
```

#### Lógica

1. **Días del Mes Anterior**
   - Calcula cuántos días del mes anterior mostrar
   - Marca como `is_other_month = True`

2. **Días del Mes Actual**
   - Genera todos los días del mes
   - Identifica el día actual
   - Asocia eventos a cada día según fechas

3. **Días del Mes Siguiente**
   - Completa hasta 42 días totales
   - Marca como `is_other_month = True`

4. **Asociación de Eventos**
   - Por cada evento, extrae fecha de inicio y fin
   - Si el día está dentro del rango, añade el evento
   - Maneja formatos de fecha ISO y objetos datetime

#### Uso en Templates

**Mini-Calendario (Homepage)**:
```html
{% for day in calendar_days %}
<div class="day {% if day.is_today %}today{% endif %}">
    {{ day.day }}
</div>
{% endfor %}
```

**Calendario Completo (Detalles)**:
```html
{% for day in calendar_days %}
<div class="day">
    <div class="day-number">{{ day.day }}</div>
    {% for event in day.events %}
    <div class="event-box">{{ event.titulo }}</div>
    {% endfor %}
</div>
{% endfor %}
```

---

## Estilos CSS Principales

### Componentes de Búsqueda
- `.header-section`: Contenedor flex para título y búsqueda
- `.search-container`: Contenedor de la barra de búsqueda
- `.search-form`: Formulario con display flex
- `.search-input`: Input de texto con bordes redondeados
- `.search-btn`: Botón verde con icono de búsqueda
- `.search-info`: Banner verde con información de resultados
- `.return-btn`: Botón para volver a todos los calendarios

### Componentes de Calendario
- `.calendar-grid`: Grid responsive para tarjetas
- `.calendar-card`: Tarjeta individual de calendario
- `.create-calendar-card`: Tarjeta especial para crear calendario
- `.mini-calendar`: Contenedor del mini-calendario
- `.calendar-days`: Grid de 7 columnas para días
- `.day`: Caja individual de día
- `.day.today`: Estilo especial para día actual (verde)

### Componentes de Detalles
- `.detail-container`: Grid de 2 columnas (info + calendario)
- `.calendar-info`: Sidebar con información
- `.full-calendar`: Calendario completo con eventos
- `.event-box`: Caja azul para eventos
- `.tag`: Etiqueta con estilo pill
- `.editable-title`: Contenedor para título editable

### Componentes de Propietario
- `.delete-btn`: Botón circular rojo para eliminar
- `.modal`: Overlay para modales
- `.modal-content`: Contenedor de contenido del modal
- `.edit-btn`: Botón azul para editar
- `.add-tag-form`: Formulario inline para añadir tags

### Responsive Design
```css
@media (max-width: 768px) {
    .header-section { flex-direction: column; }
    .search-input { width: 100%; }
    .detail-container { grid-template-columns: 1fr; }
    .calendar-grid { grid-template-columns: 1fr; }
}
```

---

## Notas de Implementación

### Sistema de Propietarios
- Actualmente `is_owner` siempre es `True`
- Preparado para futura implementación de sistema de usuarios
- Las funcionalidades de edición están condicionadas a este flag

### Manejo de Fechas
- Formato de fechas: ISO 8601 con timezone
- Meses en español: Array hardcodeado en backend
- Semana comienza en Lunes (estándar europeo)

### Redirecciones
- Todas las operaciones POST redirigen con código 303
- Preservación del contexto de búsqueda en navegación
- URLs relativas para mejor portabilidad

### Comunicación con Microservicios
- Uso de `httpx.AsyncClient` para llamadas asíncronas
- Manejo de errores con try/except
- Retorno de listas vacías en lugar de errores para mejor UX
- Variables de entorno para URLs de servicios

### Variables de Entorno
```
CALENDARIO_SERVICE_URL=http://servicio-calendario:8002
EVENTOS_SERVICE_URL=http://servicio-eventos:8001
```
