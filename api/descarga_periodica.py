def cargar_todos_los_json():
    """
    Lee todos los archivos JSON en el directorio DATA_DIR y retorna una lista de diccionarios.
    Útil para procesamiento IA, embeddings, búsqueda semántica, etc.
    """
    import glob
    json_files = glob.glob(str(DATA_DIR / 'sheet_*.json'))
    hojas = []
    for file in json_files:
        try:
            with open(file, 'r') as f:
                hojas.append(json.load(f))
        except Exception as e:
            log(f'ERROR al leer {file}: {e}')
    return hojas


import smartsheet
import schedule
import time
import json
import os
import sys
from pathlib import Path
import datetime

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
LOG_FILE = Path(__file__).parent / 'descarga.log'

smartsheet_client = smartsheet.Smartsheet(API_TOKEN)

def log(msg):
    ts = datetime.datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{ts}] {msg}\n')

def descargar_y_guardar_todo():
    try:
        response = smartsheet_client.Sheets.list_sheets()
        sheets = response.data
        for sheet in sheets:
            sheet_id = sheet.id
            # Descargar como JSON
            sheet_data = smartsheet_client.Sheets.get_sheet(sheet_id).to_dict()
            path_json = DATA_DIR / f'sheet_{sheet_id}.json'
            if path_json.exists():
                with open(path_json, 'r') as f:
                    viejo_data = json.load(f)
                if viejo_data != sheet_data:
                    log(f'Cambios detectados en la hoja {sheet.name} (ID: {sheet_id})')
            else:
                log(f'Guardando nueva hoja {sheet.name} (ID: {sheet_id})')
            with open(path_json, 'w') as f:
                json.dump(sheet_data, f)
            # Descargar como Excel (XLSX)
            try:
                file_xlsx = f'sheet_{sheet_id}.xlsx'
                response = smartsheet_client.Sheets.get_sheet_as_excel(sheet_id, str(DATA_DIR), alternate_file_name=file_xlsx)
                path_xlsx = DATA_DIR / file_xlsx
                if not path_xlsx.exists():
                    log(f'ERROR: No se generó el archivo XLSX para hoja {sheet.name}')
            except Exception as e:
                log(f'ERROR al descargar XLSX para hoja {sheet.name}: {e}')
            # Descargar como CSV
            try:
                file_csv = f'sheet_{sheet_id}.csv'
                response = smartsheet_client.Sheets.get_sheet_as_csv(sheet_id, str(DATA_DIR), alternate_file_name=file_csv)
                path_csv = DATA_DIR / file_csv
                if not path_csv.exists():
                    log(f'ERROR: No se generó el archivo CSV para hoja {sheet.name}')
            except Exception as e:
                log(f'ERROR al descargar CSV para hoja {sheet.name}: {e}')
            # Descargar como PDF
            try:
                file_pdf = f'sheet_{sheet_id}.pdf'
                response = smartsheet_client.Sheets.get_sheet_as_pdf(sheet_id, str(DATA_DIR), alternate_file_name=file_pdf)
                path_pdf = DATA_DIR / file_pdf
                if not path_pdf.exists():
                    log(f'ERROR: No se generó el archivo PDF para hoja {sheet.name}')
            except Exception as e:
                log(f'ERROR al descargar PDF para hoja {sheet.name}: {e}')
        log('Descarga y comparación completadas.')
    except Exception as e:
        log(f'ERROR: {e}')

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
