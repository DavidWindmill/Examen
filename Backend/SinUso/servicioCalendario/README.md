<a name="inicio"></a>

# 🗓️ API de Calendarios – Endpoints principales

Esta API permite gestionar calendarios almacenados en una base de datos **MongoDB**, utilizando **FastAPI** como framework y **Beanie** como ODM (Object Document Mapper).
<br/>Este microservicio se encarga de todo lo que tiene que ver con la entidad Calendario

---

## Tabla de Contenidos

- [GET `/api/v1/calendarios`](#get-apiv1calendarios)
- [GET `/api/v1/calendarios/{id}`](#get-apiv1calendariosid)
- [GET `/api/v1/calendarios/organizador/{organizador}`](#get-apiv1calendariosorganizadororganizador)
- [GET `/api/v1/calendarios/buscar/{texto}`](#get-apiv1calendariosbuscartexto)
- [GET `/api/v1/calendarios/{id}/cantidad-eventos`](#get-apiv1calendariosidcantidad-eventos)
- [GET `/api/v1/calendarios/{id}/proximos-eventos`](#get-apiv1calendariosidproximos-eventos)
- [POST `/api/v1/calendarios`](#post-apiv1calendarios)
- [POST `/api/v1/calendarios/{id}/palabras-claves`](#post-apiv1calendariosidpalabras-claves)
- [PUT `/api/v1/calendarios/{id}`](#put-apiv1calendariosid)
- [DELETE `/api/v1/calendarios/{id}`](#delete-apiv1calendariosid)
- [DELETE `/api/v1/calendarios/{id}/palabras-claves`](#delete-apiv1calendariosidpalabras-claves)

---

<br><br><br>

## <a name="get-apiv1calendarios"></a> 🟢 GET `/api/v1/calendarios`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener todos los calendarios
Este endpoint devuelve **la lista completa de calendarios** almacenados en la base de datos MongoDB.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios`.
   - No se requiere ningún parámetro ni cuerpo (`body`) en la petición.

2. **Llamada al servicio `getTodosLosCalendarios()`**
   - El controlador ejecuta:
     ```python
     calendarios = await getTodosLosCalendarios()
     ```
   - Esta función utiliza Beanie para consultar todos los documentos del modelo `Calendario`:
     ```python
     calendarios = await Calendario.find_all().to_list()
     ```
   - Si ocurre algún error durante la consulta, se captura la excepción y se devuelve un mensaje descriptivo:
     ```python
     {"error": f"Error al obtener calendarios: {e}"}
     ```

3. **Respuesta al cliente**
   - En caso de éxito, devuelve una lista de calendarios en formato JSON con código **HTTP 200 (OK)**.

---

### 📥 Ejemplo de petición
**URL:**
GET http://localhost:8002/api/v1/calendarios


### 📤 Ejemplo de respuesta
```json
[
  {
    "_id": "67aa18aabb8c1b864e19226d",
    "titulo": "Calendario de pruebas",
    "organizador": "Tester",
    "palabras_claves": ["evento1", "evento2"]
  },
  {
    "_id": "67aa18aabb8c1b864e19227d",
    "titulo": "Calendario académico",
    "organizador": "Universidad",
    "palabras_claves": ["clases", "exámenes"]
  }
]
```
**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
500     Error interno	            Fallo al insertar el documento en la base de datos.
```
---

<br><br><br>

## <a name="get-apiv1calendariosid"></a> 🟢 GET `/api/v1/calendarios/{id}`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener un calendario por su id
Este endpoint permite **consultar un calendario específico** a partir de su identificador único (`_id`) en la base de datos **MongoDB**.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios/{id}`, donde `{id}` es el identificador del calendario (tipo `PydanticObjectId`).

2. **Llamada al servicio `getCalendario(id)`**
   - El controlador ejecuta:
     ```python
     calendario = await getCalendario(id)
     ```
   - Internamente, esta función busca el calendario correspondiente en la base de datos:
     ```python
     calendario = await Calendario.get(calendarioID)
     ```

3. **Comprobación de existencia**
   - Si no se encuentra ningún documento con el ID proporcionado, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Calendario no encontrado")
     ```

4. **Respuesta exitosa**
   - Si el calendario existe, el servidor devuelve el documento completo con código **HTTP 200 (OK)**.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
500	    Error interno	            Fallo al insertar el documento en la base de datos.
```
---

### 📥 Ejemplo de petición

**URL:**
GET http://localhost:8002/api/v1/calendarios/690b7f04222250ec1a661b7d

### 📤 Ejemplo de respuesta
```json
{
  "_id": "690b7f04222250ec1a661b7d",
  "titulo": "prueba1",
  "organizador": "soyYo",
  "palabras_claves": ["patata", "ciruela"]
}
```
---

<br><br><br>

## <a name="get-apiv1calendariosorganizadororganizador"></a> 🟢 GET `/api/v1/calendarios/organizador/{organizador}`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener una lista de calendarios por su organizador

Este endpoint devuelve **la lista de calendarios** dado su organizador.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios/organizador/{organizador}`, donde `{organizador}` es el nombre del organizador.

2. **Llamada al servicio `getCalendariosPorOrganizador(organizador)`**
   - El controlador ejecuta:
     ```python
     calendarios = await getCalendariosPorOrganizador(organizador)
     ```
   - Internamente, esta función busca los calendarios correspondientes en la base de datos:
     ```python
     calendarios = await Calendario.find(Calendario.organizador == organizador).to_list()
     ```

3. **Respuesta al cliente**
   - Si se encuentran calendarios, devuelve una lista de ellos con código **HTTP 200 (OK)**.
   - Si no se encuentran calendarios, devuelve una lista vacía.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
500	    Error interno	            Fallo al consultar la base de datos.
```

---

### 📥 Ejemplo de petición

**URL:**
GET http://localhost:8002/api/v1/calendarios/organizador/Tester

### 📤 Ejemplo de respuesta
```json
{
  "_id": "67aa18aabb8c1b864e19226d",
  "titulo": "Calendario de pruebas",
  "organizador": "Tester",
  "palabras_claves": ["evento1", "evento2"]
}
```

---

<br><br><br>

## <a name="get-apiv1calendariosbuscartexto"></a> 🟢 GET `/api/v1/calendarios/buscar/{texto}`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener una lista de calendarios mediante el título o una palabra clave

Este endpoint devuelve **la lista de calendarios** dado un título o palabra clave.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios/buscar/{texto}`, donde `{texto}` es el término de búsqueda.

2. **Llamada al servicio `buscarCalendarios(texto)`**
   - El controlador ejecuta:
     ```python
     calendarios = await buscarCalendarios(texto)
     ```
   - Internamente, esta función busca los calendarios cuyo título o palabras clave contengan el texto proporcionado:
     ```python
     calendarios = await Calendario.find(
         (Calendario.titulo.matches(texto, case_insensitive=True)) |
         (Calendario.palabras_claves.any(texto))
     ).to_list()
     ```

3. **Respuesta al cliente**
   - Si se encuentran calendarios, devuelve una lista de ellos with código **HTTP 200 (OK)**.
   - Si no se encuentran calendarios, devuelve una lista vacía.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
500	    Error interno	            Fallo al consultar la base de datos.
```

---

### 📥 Ejemplo de petición

**URL:**
GET http://localhost:8002/api/v1/calendarios/buscar/evento1

### 📤 Ejemplo de respuesta
```json
{
  "_id": "67aa18aabb8c1b864e19226d",
  "titulo": "Calendario de pruebas",
  "organizador": "Tester",
  "palabras_claves": ["evento1", "evento2"]
}
```
---
<br><br><br>

## <a name="get-apiv1calendariosidcantidad-eventos"></a> 🟢 GET `/api/v1/calendarios/{id}/cantidad-eventos`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener la cantidad de eventos asociados a un calendario

Este endpoint devuelve **la cantidad de eventos** asociados a un calendario específico.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios/{id}/cantidad-eventos`, donde `{id}` es el identificador del calendario.

2. **Llamada al servicio `getCantidadEventosDeCalendario(id)`**
   - El controlador ejecuta:
     ```python
     resultado = await getCantidadEventosDeCalendario(id)
     ```
   - Internamente, esta función realiza una solicitud HTTP al microservicio de eventos para obtener los eventos asociados al calendario:
     ```python
     url = f"http://localhost:8001/api_eventos/v1/calendario/{calendarioID}"
     response = await client.get(url)
     eventos = response.json()
     cantidad_eventos = len(eventos)
     ```

3. **Comprobación de errores**
   - Si ocurre un error en la solicitud HTTP o en el procesamiento, se captura y se devuelve un mensaje descriptivo:
     ```python
     {"error": f"Error obteniendo cantidad de eventos: {e}"}
     ```

4. **Respuesta exitosa**
   - Si la operación es exitosa, devuelve un objeto JSON con el ID del calendario y la cantidad de eventos asociados:
     ```json
     {
       "calendarioID": "id_del_calendario",
       "cantidad_eventos": 5
     }
     ```

---

### 📥 Ejemplo de petición

**URL:**
GET http://localhost:8002/api/v1/calendarios/690b7f04222250ec1a661b7d/cantidad-eventos

### 📤 Ejemplo de respuesta
```json
{
  "calendarioID": "690b7f04222250ec1a661b7d",
  "cantidad_eventos": 3
}
```

**⚠️ Posibles errores**
```json
Código	Causa	                    Descripción
400	    Error en la solicitud	    Fallo en la comunicación con el microservicio de eventos.
404	    No encontrado	            No existe ningún calendario con el ID indicado.
```

---
<br><br><br>

## <a name="get-apiv1calendariosidproximos-eventos"></a> 🟢 GET `/api/v1/calendarios/{id}/proximos-eventos`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Obtener los próximos eventos de un calendario

Este endpoint devuelve **los próximos eventos** asociados a un calendario específico. Solo devuelve eventos cuya hora de finalización (`hora_fin`) sea mayor que la hora actual, es decir, eventos futuros o en curso.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `GET` a la ruta `/api/v1/calendarios/{id}/proximos-eventos`, donde `{id}` es el identificador del calendario.
   - Opcionalmente, se puede incluir el parámetro de consulta `limite` para especificar el número máximo de eventos a devolver (por defecto es 10).

2. **Llamada al servicio `getProximosEventosDeCalendario(id, limite)`**
   - El controlador ejecuta:
     ```python
     resultado = await getProximosEventosDeCalendario(id, limite)
     ```
   - Internamente, esta función realiza una solicitud HTTP al microservicio de eventos para obtener los eventos asociados al calendario:
     ```python
     url = f"http://localhost:8001/api_eventos/v1/calendario/{calendarioID}"
     response = await client.get(url, params={"limite": limite})
     eventos = response.json()
     ```

3. **Filtrado de eventos futuros**
   - La función filtra los eventos devueltos, manteniendo solo aquellos cuya `hora_fin` es mayor que la hora actual:
     ```python
     hora_actual = datetime.now(timezone.utc)
     # Para cada evento, convertir hora_fin a datetime y comparar
     if hora_fin > hora_actual:
         eventos_futuros.append(evento)
     ```
   - Soporta diferentes formatos de fecha: timestamps en milisegundos, strings ISO, y objetos con formato `{"$date": ...}`.

4. **Comprobación de errores**
   - Si ocurre un error en la solicitud HTTP o en el procesamiento, se captura y se devuelve un mensaje descriptivo:
     ```python
     {"error": f"Error obteniendo próximos eventos: {e}"}
     ```

5. **Respuesta exitosa**
   - Si la operación es exitosa, devuelve un objeto JSON con:
     - `calendarioID`: ID del calendario consultado
     - `cantidad_eventos`: Número de eventos futuros encontrados
     - `limite`: Límite aplicado en la búsqueda
     - `proximos_eventos`: Array con los eventos futuros

---

### 📥 Ejemplo de petición

**URL:**
```
GET http://localhost:8002/api/v1/calendarios/690b7f04222250ec1a661b7d/proximos-eventos
```

### 📤 Ejemplo de respuesta
```json
{
  "calendarioID": "690b7f04222250ec1a661b7d",
  "cantidad_eventos": 2,
  "limite": 10,
  "proximos_eventos": [
    {
      "_id": "690b8a12345678ec1a661c8e",
      "titulo": "Reunión de equipo",
      "descripcion": "Planificación del sprint",
      "hora_comienzo": {"2025-09-18T10:30:00.000+00:00"},
      "hora_fin": {"2025-12-18T10:30:00.000+00:00"},
      "calendarioID": "690b7f04222250ec1a661b7d"
    },
    {
      "_id": "690b8b23456789ec1a661c9f",
      "titulo": "Presentación del proyecto",
      "descripcion": "Demo para el cliente",
      "hora_comienzo": {"2025-09-18T10:30:00.000+00:00"},
      "hora_fin": {"2025-12-18T10:30:00.000+00:00"},
      "calendarioID": "690b7f04222250ec1a661b7d"
    }
  ]
}
```

**⚠️ Posibles errores**
```json
Código	Causa	                        Descripción
400	    Error en la solicitud	        Fallo en la comunicación con el microservicio de eventos o error al filtrar eventos.
404	    No encontrado	                No existe ningún calendario con el ID indicado.
500	    Error interno	                Error inesperado en el servidor.
```

---

### 📝 Notas adicionales

- **Requisito previo**: El microservicio de eventos debe estar ejecutándose en `http://localhost:8001` para que este endpoint funcione correctamente.
- **Filtrado automático**: Solo se devuelven eventos cuya hora de finalización no ha pasado aún.
- **Parámetro `limite`**: Permite controlar la cantidad de eventos devueltos para optimizar el rendimiento en calendarios con muchos eventos.
- **Timezone**: Todas las comparaciones se realizan en UTC para evitar problemas con zonas horarias.

---
<br><br><br>

## <a name="post-apiv1calendarios"></a> 🟢 POST `/api/v1/calendarios`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Crear un nuevo calendario

Este endpoint permite **crear un nuevo calendario** en la base de datos.  
Recibe un objeto JSON con los campos del calendario y devuelve el documento insertado.

---

### ⚙️ Funcionamiento interno

1. **Recepción del cuerpo (payload)**  
   - FastAPI recibe el cuerpo de la petición como una instancia del modelo `Calendario`, definido en models.py (con Beanie).
   - Si los campos enviados no coinciden con el modelo (`titulo`, `organizador`, `palabras_claves`), FastAPI genera un error de validación `422 Unprocessable Entity`.
   (Darse cuenta si las variables se llaman igual!!)

2. **Llamada al servicio `crearCalendario()`**  
   - El controlador extrae los datos del payload y llama a la función del servicio:
     ```python
     calendario = await crearCalendario(
         titulo=payload.titulo,
         organizador=payload.organizador,
         palabras_claves=payload.palabras_claves
     )
     ```

3. **Inserción en la base de datos**  
   - En la función `crearCalendario`, se crea un nuevo objeto `Calendario` y se inserta en MongoDB:
     ```python
     nuevoCalendario = Calendario(
         titulo=titulo,
         organizador=organizador,
         palabras_claves=palabras_claves
     )
     await nuevoCalendario.insert()
     ```
   - Beanie genera automáticamente el campo `_id`.

4. **Respuesta al cliente**  
   - El endpoint devuelve el calendario creado, junto con el código **HTTP 201 (Created)**.

---

### 📥 Ejemplo de petición (Postman)

**URL:**
POST http://localhost:8002/api/v1/calendarios

**Body (raw JSON):**
```json
{
  "titulo": "Calendario de pruebas",
  "organizador": "Tester",
  "palabras_claves": ["evento1", "evento2", "evento3"]
}
```
**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
422	    Error de validación	        Los campos enviados no coinciden con el modelo Calendario.
500	    Error interno	            Fallo al insertar el documento en la base de datos.
```

---
<br><br><br>

## <a name="post-apiv1calendariosidpalabras-claves"></a> 🟢 POST `/api/v1/calendarios/{id}/palabras-claves`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Añadir una palabra clave a un calendario
Este endpoint permite **añadir una nueva palabra clave** a un calendario existente.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `POST` a la ruta `/api/v1/calendarios/{id}/palabras-claves`, donde `{id}` es el identificador del calendario.
   - El cuerpo de la solicitud debe contener la palabra clave a añadir en formato JSON.

2. **Llamada al servicio `añadirPalabraClaveACalendario(id, palabra_clave)`**
   - El controlador ejecuta:
     ```python
     await añadirPalabraClaveACalendario(id, palabra_clave)
     ```

3. **Comprobación de existencia**
   - Si no se encuentra ningún documento con el ID proporcionado, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Calendario no encontrado")
     ```

4. **Respuesta exitosa**
   - Si la palabra clave se añade correctamente, el servidor devuelve el documento actualizado con código **HTTP 200 (OK)**.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
```

---

### 📥 Ejemplo de petición

**URL:**
POST http://localhost:8002/api/v1/calendarios/67aa18aabb8c1b864e19226d/palabras-claves

**Body (raw JSON):**
```json
{
    "palabra_clave": "nuevo_evento"
}
```

### 📤 Ejemplo de respuesta
```json
{
    "_id": "67aa18aabb8c1b864e19226d",
    "titulo": "Calendario de Ejemplo",
    "organizador": "Organizador",
    "palabras_claves": ["evento1", "evento2", "nuevo_evento"]
}
```

---
<br><br><br>

## <a name="put-apiv1calendariosid"></a> 🟢 PUT `/api/v1/calendarios/{id}`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Actualizar un calendario
Este endpoint permite **actualizar un calendario existente** en la base de datos MongoDB.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `PUT` a la ruta `/api/v1/calendarios/{id}`, donde `{id}` es el identificador del calendario.
   - El cuerpo de la solicitud debe contener los campos a actualizar en formato JSON.

2. **Llamada al servicio `actualizarCalendario(id, calendario)`**
   - El controlador ejecuta:
     ```python
     await actualizarCalendario(id, calendario)
     ```

3. **Comprobación de existencia**
   - Si no se encuentra ningún documento con el ID proporcionado, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Calendario no encontrado")
     ```

4. **Comprobación de campos**
   - Si se intenta actualizar un campo que no existe, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=400, detail="No se proporcionaron campos válidos para actualizar")
     ```

5. **Respuesta exitosa**
   - Si el calendario se actualiza correctamente, el servidor devuelve el documento actualizado con código **HTTP 200 (OK)**.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
400     Error de validación         Los datos proporcionados no son válidos.
```

---

### 📥 Ejemplo de petición

**URL:**
PUT http://localhost:8002/api/v1/calendarios/67aa18aabb8c1b864e19226d

**Body (raw JSON):**
```json
{
    "titulo": "Nuevo Título",
    "organizador": "Nuevo Organizador"
}
```

### 📤 Ejemplo de respuesta
```json
{
    "_id": "67aa18aabb8c1b864e19226d",
    "titulo": "Nuevo Título",
    "organizador": "Nuevo Organizador",
    "palabras_claves": ["evento1", "evento2"]
}
```

---
<br><br><br>

## <a name="delete-apiv1calendariosid"></a> 🟢 DELETE `/api/v1/calendarios/{id}`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Eliminar un calendario
Este endpoint permite **eliminar un calendario existente** de la base de datos MongoDB.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `DELETE` a la ruta `/api/v1/calendarios/{id}`, donde `{id}` es el identificador del calendario.

2. **Llamada al servicio `eliminarCalendario(id)`**
   - El controlador ejecuta:
     ```python
     await eliminarCalendario(id)
     ```

3. **Comprobación de existencia**
   - Si no se encuentra ningún documento con el ID proporcionado, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Calendario no encontrado")
     ```

4. **Respuesta exitosa**
   - Si el calendario se elimina correctamente, el servidor devuelve un mensaje de confirmación con código **HTTP 200 (OK)**.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
500     Error interno               Fallo al eliminar el documento de la base de datos.
```

---

### 📥 Ejemplo de petición

**URL:**
DELETE http://localhost:8002/api/v1/calendarios/67aa18aabb8c1b864e19226d

### 📤 Ejemplo de respuesta
```json
{
    "status_code": 200
}
```

---
<br><br><br>

## <a name="delete-apiv1calendariosidpalabras-claves"></a> 🟢 DELETE `/api/v1/calendarios/{id}/palabras-claves`
[🔝 Volver a la Tabla de Contenidos](#inicio)

### ➤ Eliminar una palabra clave de un calendario
Este endpoint permite **eliminar una palabra clave existente** de un calendario.

---

### ⚙️ Funcionamiento interno

1. **Petición HTTP**
   - El cliente realiza una solicitud `DELETE` a la ruta `/api/v1/calendarios/{id}/palabras-claves`, donde `{id}` es el identificador del calendario.
   - El cuerpo de la solicitud debe contener la palabra clave a eliminar en formato JSON.

2. **Llamada al servicio `eliminarPalabraClaveDeCalendario(id, palabra_clave)`**
   - El controlador ejecuta:
     ```python
     await eliminarPalabraClaveDeCalendario(id, palabra_clave)
     ```

3. **Comprobación de existencia**
   - Si no se encuentra ningún documento con el ID proporcionado, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Calendario no encontrado")
     ```
  - Si no se encuentra la palabra clave en el Calendario, se lanza una excepción manejada por FastAPI:
     ```python
     raise HTTPException(status_code=404, detail="Palabra clave no encontrada en el calendario")
     ```

4. **Respuesta exitosa**
   - Si la palabra clave se elimina correctamente, el servidor devuelve el documento actualizado con código **HTTP 200 (OK)**.

**⚠️ Posibles errores**
```json
                                
Código	Causa	                    Descripción
404     No encontrado               No existe ningún calendario con el ID indicado.
404     Error de validación         No existe la palabra clave que se intenta eliminar.
```

---

### 📥 Ejemplo de petición

**URL:**
DELETE http://localhost:8002/api/v1/calendarios/67aa18aabb8c1b864e19226d/palabras-claves

**Body (raw JSON):**
```json
{
    "palabra_clave": "evento1"
}
```

### 📤 Ejemplo de respuesta
```json
{
    "_id": "67aa18aabb8c1b864e19226d",
    "titulo": "Calendario de Ejemplo",
    "organizador": "Organizador",
    "palabras_claves": ["evento2"]
}
```

---