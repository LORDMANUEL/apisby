
# apisby

API clonable para descargar y comparar datos de Smartsheet periódicamente, con interfaz web para configuración y funcionamiento automático en Linux.

## ¿Qué hace este proyecto?

- Descarga automáticamente todas las hojas de tu cuenta Smartsheet cada 3 minutos y las guarda localmente en formato JSON.
- Compara los datos descargados para detectar cambios.
- Incluye una pequeña web para ingresar el token y mostrar el estado del servicio.
- Listo para clonar y usar en cualquier Linux.

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
	python3 api/app.py
	# Luego abre http://localhost:8080
	```

## Estructura

- `api/descarga_periodica.py`: Script principal de descarga y comparación.
- `api/app.py`: Web mínima para configuración y estado.
- `api/data/`: Carpeta donde se guardan los archivos descargados.
- `instalar_todo.sh`: Instalador y configurador automático.

## Requisitos
- Linux
- Python 3
- pip
- whiptail
- cron

Todo se instala automáticamente con el instalador.

---
Contribuciones y sugerencias bienvenidas.
