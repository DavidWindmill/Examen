Comandos para ejecutar en local: 
- cd Backend
- cd ServicioEventos
- py -m venv .env (Solo si aún no se ha creado el entorno)
- .\.env\Scripts\Activate.ps1
- py -m pip install -r requirements.txt (Para descargar las dependencias)
- python -m uvicorn main:api --reload --port 8001