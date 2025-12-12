
# ⚠️ ¿Cómo ejecutar el programa FastAPI? ⚠️ 

## 1) (Si no está creado) — Crear un entorno virtual
Ejecuta:
```bash
python -m venv .venv
```
## 2) Iniciar el entorno virtual (en la misma carpeta donde está .venv)
Ejecuta:
```bash
./.venv/Scripts/activate.ps1
```
## 3) Iniciar la aplicación FastAPI (desde la carpeta donde está main.py)
app es el nombre que se le da cuando en el main.py se crea FastAPI()

Ejecuta:
```bash
uvicorn main:app --port 8002
```

## Si no tienes las librerias instaladas
Después de iniciar el entorno .venv

Ejecuta:
```
pip install -r requirements.txt
```
 y comprueba que se está usando abajo a la derecha el entorno virtual como Intérprete 
(Hay que poner .venv->Scripts->python.exe)

## Si se usa más de un microservicio
Hay que hacer el mismo proceso con dos o más terminales según el número de microservicios que queramos utilizar (en diferentes puertos!)

Cuando se modifica la url de un endpoint, lo mejor es reiniciar el microservicio
