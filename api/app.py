# Endpoint para descargar un solo JSON con todas las hojas (para IA)
@app.route('/descargar-todo-json', methods=['GET'])
def descargar_todo_json():
    hojas = cargar_todos_los_json()
    return send_file(
        io.BytesIO(json.dumps(hojas, ensure_ascii=False, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='smartsheet_todo.json')
import zipfile
import io
# Endpoint para descargar todos los archivos de Smartsheet en un ZIP
@app.route('/descargar-todo', methods=['GET'])
def descargar_todo():
    data_dir = Path(__file__).parent / 'data'
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for archivo in data_dir.glob('sheet_*.*'):
            # El nombre en el ZIP será igual al nombre del archivo local
            zf.write(archivo, arcname=archivo.name)
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True, download_name='smartsheet_todo.zip')

from flask import Flask, request, render_template_string, send_file, jsonify, Response
import os
from pathlib import Path
import subprocess
import datetime
import threading

app = Flask(__name__)

from descarga_periodica import cargar_todos_los_json

# Endpoint para exponer todos los JSON a la IA
@app.route('/api/hojas_json', methods=['GET'])
def api_hojas_json():
    """Devuelve todos los datos de las hojas en formato JSON para consumo IA."""
    hojas = cargar_todos_los_json()
    return jsonify(hojas)

from flask import Flask, request, render_template_string, send_file, jsonify, Response

import os
from pathlib import Path
import subprocess
import datetime
import threading


app = Flask(__name__)

# Lanzar descarga periódica en background al iniciar la app
def start_descarga_background():
    def run():
        subprocess.Popen(['python3', str(Path(__file__).parent / 'descarga_periodica.py')])
    t = threading.Thread(target=run, daemon=True)
    t.start()

start_descarga_background()

LOG_FILE = Path(__file__).parent / 'descarga.log'
DATA_DIR = Path(__file__).parent / 'data'


TEMPLATE_FORM = '''
<!DOCTYPE html>
<html><head>
<title>Configurar Smartsheet API</title>
<style>
body { font-family: Arial, sans-serif; margin: 2em; }
.container { max-width: 600px; margin: auto; }
input[type=text] { width: 100%; padding: 8px; }
button, input[type=submit] { padding: 8px 16px; margin-top: 8px; }
.panel { background: #f8f8f8; border-radius: 8px; padding: 2em; box-shadow: 0 2px 8px #ddd; }
</style>
</head><body>
<div class="container panel">
<h2>Configurar Token de Smartsheet</h2>
<form method="post">
    <label>Token Smartsheet:</label><br>
    <input type="text" name="token" required><br><br>
    <input type="submit" value="Guardar y Activar">
</form>
</div>
</body></html>
'''


TEMPLATE_OK = '''
<!DOCTYPE html>
<html><head>
<title>Smartsheet API - Estado</title>
<style>
body { font-family: Arial, sans-serif; margin: 2em; }
.container { max-width: 900px; margin: auto; }
table { border-collapse: collapse; width: 100%; margin-top: 1em; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
th { background: #f0f0f0; }
.panel { background: #f8f8f8; border-radius: 8px; padding: 2em; box-shadow: 0 2px 8px #ddd; }
.btn { background: #007bff; color: #fff; border: none; border-radius: 4px; padding: 6px 12px; text-decoration: none; }
.btn:hover { background: #0056b3; }
</style>
</head><body>
<div class="container panel">
<h2>¡Servicio funcionando!</h2>
<p>Token configurado correctamente.</p>
<p>Última ejecución: {last_run}</p>
<p>
    <a class="btn" href="/logs" target="_blank">Ver logs</a>
    <a class="btn" href="/admin">Panel administración</a>
    <a class="btn" href="/openapi" target="_blank">Ver OpenAPI/Swagger</a>
</p>
<h3>Archivos descargados</h3>
<form method="post" action="/descargar_manual">
    <label>ID de hoja Smartsheet para descarga manual:</label>
    <input type="text" name="sheet_id" placeholder="Ej: 123456789" required>
    <button type="submit" class="btn">Descargar ahora</button>
</form>
<table>
    <tr><th>Archivo</th><th>Tipo</th><th>Acción</th></tr>
    {archivos}
</table>
</div>
</body></html>
'''
# Endpoint para servir el archivo OpenAPI/Swagger
@app.route('/openapi')
def openapi():
    openapi_path = Path(__file__).parent / 'openapi.yaml'
    if openapi_path.exists():
        return Response(openapi_path.read_text(), mimetype='text/yaml')
    return 'No se encontró la documentación OpenAPI', 404

def get_last_run():
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.strip():
                    try:
                        ts = line.split(']')[0].strip('[')
                        dt = datetime.datetime.fromisoformat(ts)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
    return 'Sin registros'

@app.route('/', methods=['GET', 'POST'])
def index():
    token_path = Path(__file__).parent / '.smartsheet_token'
    menu_descargas = '''
    <div style="margin:1em 0;">
        <a class="btn" href="/descargar-todo" target="_blank">Descargar TODO (ZIP)</a>
        <a class="btn" href="/descargar-todo-json" target="_blank">Descargar TODO (JSON global)</a>
        <a class="btn" href="/api/hojas_json" target="_blank">Ver JSON para IA</a>
    </div>
    '''
    if request.method == 'POST' and 'token' in request.form:
        token = request.form['token']
        with open(token_path, 'w') as f:
            f.write(token)
        os.environ['SMARTSHEET_API_TOKEN'] = token
        subprocess.Popen(['python3', str(Path(__file__).parent / 'descarga_periodica.py')])
        return render_template_string(menu_descargas + TEMPLATE_OK.replace('{last_run}', get_last_run()).replace('{archivos}', render_archivos()))
    if token_path.exists():
        return render_template_string(menu_descargas + TEMPLATE_OK.replace('{last_run}', get_last_run()).replace('{archivos}', render_archivos()))
    return render_template_string(TEMPLATE_FORM)

# Renderizar tabla de archivos
def render_archivos():
    filas = ""
    for f in sorted(DATA_DIR.glob('sheet_*')):
        tipo = f.suffix.upper().strip('.')
        filas += f'<tr><td>{f.name}</td><td>{tipo}</td><td><a class="btn" href="/archivo/{f.name}">Descargar</a></td></tr>'
    return filas or '<tr><td colspan="3">No hay archivos aún</td></tr>'

# Descarga manual de hoja por ID
@app.route('/descargar_manual', methods=['POST'])
def descargar_manual():
    sheet_id = request.form.get('sheet_id')
    if not sheet_id or not sheet_id.isdigit():
        return 'ID inválido', 400
    # Ejecutar descarga solo de esa hoja
    import smartsheet
    API_TOKEN = os.getenv('SMARTSHEET_API_TOKEN')
    smartsheet_client = smartsheet.Smartsheet(API_TOKEN)
    try:
        # JSON
        sheet_data = smartsheet_client.Sheets.get_sheet(int(sheet_id)).to_dict()
        path_json = DATA_DIR / f'sheet_{sheet_id}.json'
        with open(path_json, 'w') as f:
            json.dump(sheet_data, f)
        # XLSX
        try:
            response_xlsx = smartsheet_client.Sheets.get_sheet_as_excel(int(sheet_id))
            path_xlsx = DATA_DIR / f'sheet_{sheet_id}.xlsx'
            with open(path_xlsx, 'wb') as f:
                for chunk in response_xlsx:
                    f.write(chunk)
        except Exception: pass
        # CSV
        try:
            response_csv = smartsheet_client.Sheets.get_sheet_as_csv(int(sheet_id))
            path_csv = DATA_DIR / f'sheet_{sheet_id}.csv'
            with open(path_csv, 'wb') as f:
                for chunk in response_csv:
                    f.write(chunk)
        except Exception: pass
        # PDF
        try:
            response_pdf = smartsheet_client.Sheets.get_sheet_as_pdf(int(sheet_id))
            path_pdf = DATA_DIR / f'sheet_{sheet_id}.pdf'
            with open(path_pdf, 'wb') as f:
                for chunk in response_pdf:
                    f.write(chunk)
        except Exception: pass
        return '<script>window.location="/"</script>'
    except Exception as e:
        return f'Error al descargar hoja: {e}', 500


@app.route('/logs')
def logs():
    if LOG_FILE.exists():
        return f'<pre>{LOG_FILE.read_text()}</pre>'
    return 'No hay logs aún.'

@app.route('/admin')
def admin():
    # Estadísticas simples
    total_descargas = 0
    cambios = 0
    errores = 0
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                if 'Guardando nueva hoja' in line:
                    total_descargas += 1
                if 'Cambios detectados' in line:
                    cambios += 1
                if 'ERROR' in line:
                    errores += 1
    html = f"""
    <h2>Panel de administración</h2>
    <ul>
        <li>Total descargas/ejecuciones: {total_descargas}</li>
        <li>Cambios detectados: {cambios}</li>
        <li>Errores: {errores}</li>
    </ul>
    <a href='/'>Volver</a>
    """
    return html

@app.route('/archivos')
def archivos():
    archivos = []
    for f in DATA_DIR.glob('sheet_*'):
        archivos.append(f.name)
    html = '<h2>Archivos descargados</h2><ul>'
    for f in sorted(archivos):
        html += f'<li><a href="/archivo/{f}">{f}</a></li>'
    html += '</ul>'
    return html

@app.route('/archivo/<nombre>')
def archivo(nombre):
    file_path = DATA_DIR / nombre
    if file_path.exists():
        if nombre.endswith('.json'):
            with open(file_path) as f:
                return jsonify(json.load(f))
        elif nombre.endswith('.xlsx'):
            return send_file(file_path, as_attachment=True)
        else:
            return send_file(file_path)
    return 'Archivo no encontrado', 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
# Endpoint para Make: descarga archivo, extrae texto y lo devuelve
import requests
import tempfile
import mimetypes
import pandas as pd
import PyPDF2
@app.route('/descargar-y-preparar', methods=['POST'])
def descargar_y_preparar():
    data = request.get_json(force=True)
    url = data.get('archivo_url')
    tipo = data.get('archivo_tipo')
    token_seguridad = data.get('token_seguridad')
    # Validación básica de seguridad
    if token_seguridad != os.getenv('API_SECRET', '12345'):
        return jsonify({'error': 'Token de seguridad inválido'}), 403
    if not url or not tipo:
        return jsonify({'error': 'Faltan parámetros'}), 400
    try:
        # Descargar archivo temporalmente
        r = requests.get(url)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(tipo) or '') as tmp:
            tmp.write(r.content)
            tmp_path = tmp.name
        texto = ''
        if 'excel' in tipo or tmp_path.endswith('.xlsx'):
            df = pd.read_excel(tmp_path)
            texto = df.to_string(index=False)
        elif 'csv' in tipo or tmp_path.endswith('.csv'):
            df = pd.read_csv(tmp_path)
            texto = df.to_string(index=False)
        elif 'pdf' in tipo or tmp_path.endswith('.pdf'):
            with open(tmp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                texto = '\n'.join(page.extract_text() or '' for page in reader.pages)
        else:
            texto = r.text
        os.unlink(tmp_path)
        return jsonify({'texto': texto[:100000]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
