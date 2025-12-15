
import smartsheet
import schedule
import time
import json
import os
import sys
from pathlib import Path

API_TOKEN = os.getenv('SMARTSHEET_API_TOKEN')
if not API_TOKEN:
    # Intentar leer de archivo oculto
    token_path = Path(__file__).parent / '.smartsheet_token'
    if token_path.exists():
        API_TOKEN = token_path.read_text().strip()
    else:
        API_TOKEN = 'TU_TOKEN_AQUI'

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

smartsheet_client = smartsheet.Smartsheet(API_TOKEN)

def descargar_y_guardar_todo():
    response = smartsheet_client.Sheets.list_sheets()
    sheets = response.data
    for sheet in sheets:
        sheet_id = sheet.id
        sheet_data = smartsheet_client.Sheets.get_sheet(sheet_id).to_dict()
        path = DATA_DIR / f'sheet_{sheet_id}.json'
        if path.exists():
            with open(path, 'r') as f:
                viejo_data = json.load(f)
            if viejo_data != sheet_data:
                print(f'Cambios detectados en la hoja {sheet.name} (ID: {sheet_id})')
        else:
            print(f'Guardando nueva hoja {sheet.name} (ID: {sheet_id})')
        with open(path, 'w') as f:
            json.dump(sheet_data, f)

def main():
    if '--una-sola-ejecucion' in sys.argv:
        descargar_y_guardar_todo()
        return
    print('Iniciando tarea periódica de descarga de Smartsheet...')
    descargar_y_guardar_todo()  # Primera ejecución inmediata
    schedule.every(3).minutes.do(descargar_y_guardar_todo)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
