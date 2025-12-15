

# apisby

API clonable para descargar y comparar datos de Smartsheet periódicamente, con interfaz web para configuración, endpoints para IA y funcionamiento automático en Linux o Render.

## ¿Qué hace este proyecto?

- Descarga automáticamente todas las hojas de tu cuenta Smartsheet cada 3 minutos y las guarda localmente en formato JSON y Excel (XLSX).
- Compara los datos descargados para detectar cambios.
- Incluye una web para ingresar el token, ver estado, logs y descargar los archivos en ambos formatos.
- Expone endpoints para que una IA o sistema externo pueda consumir los datos descargados.
- Listo para clonar y usar en cualquier Linux o desplegar en Render.com.

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

## Endpoints útiles

- `/` : Página principal, estado y configuración.
- `/logs` : Ver logs de ejecución.
- `/archivos` : Listado de archivos descargados (JSON y XLSX).
- `/archivo/<nombre>` : Descarga o visualiza un archivo específico (útil para IA o integraciones).

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

- `api/descarga_periodica.py`: Script principal de descarga y comparación (genera JSON y XLSX).
- `api/app.py`: Web para configuración, estado, logs y descarga de archivos.
- `api/data/`: Carpeta donde se guardan los archivos descargados.
- `instalar_todo.sh`: Instalador y configurador automático.

## Requisitos
- Linux o Render.com
- Python 3
- pip
- whiptail
- cron

Todo se instala automáticamente con el instalador.

---
Contribuciones y sugerencias bienvenidas.
