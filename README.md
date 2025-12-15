



# apisby

![CI](https://github.com/LORDMANUEL/apisby/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

API clonable para descargar y comparar datos de Smartsheet periódicamente, con interfaz web moderna, endpoints para IA, descarga manual, panel de administración, y funcionamiento automático en Linux, Docker o Render.


## Visión

Ser la solución más sencilla, portable y robusta para la integración, respaldo y análisis de datos de Smartsheet, facilitando la interoperabilidad con IA y sistemas externos.

## Misión

Permitir a cualquier usuario o empresa automatizar la descarga, comparación y exposición de datos de Smartsheet en múltiples formatos, con una interfaz web amigable, moderna y APIs estandarizadas.

## ¿Qué hace este proyecto?

- Descarga automáticamente todas las hojas de tu cuenta Smartsheet cada 3 minutos y las guarda localmente en formato JSON, Excel (XLSX), CSV y PDF.
- Compara los datos descargados para detectar cambios.
- Incluye una web moderna para ingresar el token, ver estado, logs, panel de administración y descargar los archivos en todos los formatos.
- Permite descarga manual de hojas por ID desde la web.
- Expone endpoints para que una IA o sistema externo pueda consumir los datos descargados.
- Inicia la descarga automáticamente al levantar la web.
- Listo para clonar y usar en cualquier Linux, Docker o desplegar en Render.com.


## Sistemas compatibles

- **Linux** (probado en Ubuntu/Debian)
- **Docker** (cualquier sistema compatible)
- **Render.com** (cloud)
- Compatible con cualquier sistema que soporte Python 3 y pip

## Instalación rápida

1. Clona el repositorio:
	```bash
	git clone https://github.com/LORDMANUEL/apisby.git
	cd apisby
	```
2. Ejecuta el instalador interactivo:
	```bash
	bash instalar_todo.sh
	```
	- Instala dependencias, pide el token y configura cron para descargar cada 3 minutos.

3. (Opcional) Levanta la web para ver el estado o ingresar el token:
	```bash
	source api/venv/bin/activate
	python3 api/app.py
	# Luego abre http://localhost:8080
	```

4. (Opcional) Despliega con Docker:
	```bash
	docker build -t apisby .
	docker run -p 8080:8080 apisby
	```

## Endpoints útiles

- `/` : Página principal, estado, configuración, tabla de archivos y descarga manual.
- `/logs` : Ver logs de ejecución.
- `/archivos` : Listado de archivos descargados (JSON, XLSX, CSV, PDF).
- `/archivo/<nombre>` : Descarga o visualiza un archivo específico (útil para IA o integraciones).
- `/admin` : Panel de administración con estadísticas de descargas, cambios y errores.

## Despliegue en Render.com

1. Crea una cuenta en https://render.com y selecciona "New Web Service".
2. Conecta tu repositorio de GitHub.
3. Configura:
	- **Environment**: Python 3
	- **Build Command**: `pip install -r api/requirements.txt`
	- **Start Command**: `python3 api/app.py`
	- **Root Directory**: `.`
	- **Port**: 8080
4. Agrega la variable de entorno `SMARTSHEET_API_TOKEN` en la sección de Environment.
5. Render instalará Flask y todas las dependencias automáticamente.
6. Accede a la URL pública que Render te proporciona.

## Estructura

- `api/descarga_periodica.py`: Script principal de descarga y comparación (genera JSON, XLSX, CSV, PDF).
- `api/app.py`: Web para configuración, estado, logs, descarga manual y panel de administración.
- `api/data/`: Carpeta donde se guardan los archivos descargados.
- `instalar_todo.sh`: Instalador y configurador automático.
- `Dockerfile`: Despliegue fácil con Docker.
- `.github/workflows/ci.yml`: Pruebas automáticas y CI/CD.
- `api/openapi.yaml`: Documentación OpenAPI de los endpoints.

## Requisitos
- Linux, Docker o Render.com
- Python 3
- pip
- whiptail
- cron

Todo se instala automáticamente con el instalador.


## Visión

Ser la solución más sencilla, portable y robusta para la integración, respaldo y análisis de datos de Smartsheet, facilitando la interoperabilidad con IA y sistemas externos.

## Misión

Permitir a cualquier usuario o empresa automatizar la descarga, comparación y exposición de datos de Smartsheet en múltiples formatos, con una interfaz web amigable y APIs estandarizadas.


## Mejoras pensadas / Futuro

- Autenticación avanzada y control de acceso en la web.
- Notificaciones por email/webhook ante cambios o errores.
- Soporte multiusuario y multi-token.
- Integración con otros servicios cloud (Google Drive, Dropbox, etc.).
- Panel de administración avanzado con gráficas y filtros.
- Exportación a otros formatos (XML, ODS, etc.).
- API RESTful documentada con Swagger/OpenAPI.
- Pruebas automáticas más completas y cobertura de endpoints.
- Despliegue one-click en más plataformas cloud.
- Animaciones y mejoras visuales en la web (loader, feedback visual, favicon, etc.).

## Estandarización

- Código Python 3 siguiendo PEP8.
- API documentada en OpenAPI 3.0 (api/openapi.yaml).
- Estructura de carpetas clara y modular.
- Uso de Docker y CI/CD para portabilidad y calidad.

## Sistemas compatibles

- Linux (probado en Ubuntu/Debian)
- Docker (cualquier sistema compatible)
- Render.com (cloud)
- Compatible con cualquier sistema que soporte Python 3 y pip

## Roadmap de funcionamiento

1. Instalación y configuración automática (token, dependencias, cron, venv).
2. Descarga periódica y manual de hojas Smartsheet en JSON, XLSX, CSV, PDF.
3. Exposición de archivos y estado vía web y API.
4. Panel de administración y logs accesibles desde la web.
5. Integración sencilla con IA y sistemas externos vía endpoints REST.
6. Despliegue fácil en local, Docker o cloud.

---
Contribuciones y sugerencias bienvenidas.
