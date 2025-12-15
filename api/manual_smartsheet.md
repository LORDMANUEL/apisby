# Manual de uso del SDK de Smartsheet

Este manual describe cómo utilizar el SDK de Smartsheet en Python para descargar todo el contenido de tu cuenta y cómo automatizar este proceso cada 3 minutos, almacenando y comparando los datos localmente.

## 1. Instalación del SDK

Instala el SDK oficial de Smartsheet:

```bash
pip install smartsheet-python-sdk
```

## 2. Autenticación

Obtén tu token de API desde Smartsheet y guárdalo en una variable de entorno o en un archivo seguro.

```python
import smartsheet

API_TOKEN = 'TU_TOKEN_AQUI'
smartsheet_client = smartsheet.Smartsheet(API_TOKEN)
```

## 3. Descarga de datos

Puedes descargar hojas, informes, y otros objetos. Ejemplo para descargar todas las hojas:

```python
# Obtener todas las hojas
response = smartsheet_client.Sheets.list_sheets()
sheets = response.data

for sheet in sheets:
    sheet_id = sheet.id
    sheet_data = smartsheet_client.Sheets.get_sheet(sheet_id)
    # Guardar sheet_data en almacenamiento local
```

## 4. Automatización cada 3 minutos

Puedes usar un scheduler como `schedule` o un cron job. Ejemplo con `schedule`:

```bash
pip install schedule
```

```python
import schedule
import time

def tarea_descarga():
    # Lógica de descarga y comparación aquí
    pass

schedule.every(3).minutes.do(tarea_descarga)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 5. Almacenamiento y comparación local

Guarda los datos descargados en archivos (por ejemplo, JSON) y compara con los datos previos para detectar cambios.

```python
import json
import os

def guardar_datos(sheet_id, data):
    with open(f'data/sheet_{sheet_id}.json', 'w') as f:
        json.dump(data, f)

def comparar_datos(sheet_id, nuevo_data):
    path = f'data/sheet_{sheet_id}.json'
    if os.path.exists(path):
        with open(path, 'r') as f:
            viejo_data = json.load(f)
        return viejo_data != nuevo_data
    return True
```

Crea la carpeta `data` para almacenar los archivos descargados.

---

Adapta los ejemplos según tus necesidades específicas.