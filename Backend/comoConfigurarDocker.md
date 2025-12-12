# Docker

Se crea un fichero Docker por cada microservicio. En el proyecto raíz, se cre un fichero docker-compose.yml y un fichero .env (con las variables que usaremos para Docker)
En las implementaciones de los microservicios, hay que usar: SERVICE_URL = os.getenv("SERVICE_URL", "http://localhost:puerto") para que Docker pueda coger correctamente la url del microservicio
La variable SERVICE_URL será el nombre con el que se haya llamado al servicio en docker-compose.yml


# Comandos Docker

## En la carpeta Backend
Poner el siguiente comando:
```bash
docker-compose up --build
```
Levantar en segundo plano:
```bash
docker-compose up -d --build
```

## Para aplicar cambios en el código
Eliminar las imágenes y contenedores de Docker:
```bash
docker compose down --rmi all --volumes --remove-orphans
```
Luego, volver a generar el contenedor:
```bash
docker-compose up --build
```