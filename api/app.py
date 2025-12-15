
from flask import Flask, request, render_template_string, send_file, jsonify
import os
from pathlib import Path
import subprocess
import datetime

app = Flask(__name__)

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
    if request.method == 'POST' and 'token' in request.form:
        token = request.form['token']
        with open(token_path, 'w') as f:
            f.write(token)
        os.environ['SMARTSHEET_API_TOKEN'] = token
        subprocess.Popen(['python3', str(Path(__file__).parent / 'descarga_periodica.py')])
        return render_template_string(TEMPLATE_OK.format(last_run=get_last_run(), archivos=render_archivos()))
    if token_path.exists():
        return render_template_string(TEMPLATE_OK.format(last_run=get_last_run(), archivos=render_archivos()))
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
    app.run(host='0.0.0.0', port=8080)
