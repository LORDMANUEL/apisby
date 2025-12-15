

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
<html><body>
<h2>Configurar Token de Smartsheet</h2>
<form method="post">
  <label>Token Smartsheet:</label><br>
  <input type="text" name="token" style="width:350px" required><br><br>
  <input type="submit" value="Guardar y Activar">
</form>
</body></html>
'''

TEMPLATE_OK = '''
<!DOCTYPE html>
<html><body>
<h2>¡Servicio funcionando!</h2>
<p>Token configurado correctamente.</p>
<p><a href="/logs" target="_blank">Ver logs de ejecución</a></p>
<p>Última ejecución: {last_run}</p>
<p><a href="/archivos">Ver archivos descargados</a></p>
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
    if request.method == 'POST':
        token = request.form['token']
        with open(token_path, 'w') as f:
            f.write(token)
        os.environ['SMARTSHEET_API_TOKEN'] = token
        # Lanzar el script de descarga en segundo plano si no está corriendo
        subprocess.Popen(['python3', 'descarga_periodica.py'])
        return render_template_string(TEMPLATE_OK.format(last_run=get_last_run()))
    if token_path.exists():
        return render_template_string(TEMPLATE_OK.format(last_run=get_last_run()))
    return render_template_string(TEMPLATE_FORM)

@app.route('/logs')
def logs():
    if LOG_FILE.exists():
        return f'<pre>{LOG_FILE.read_text()}</pre>'
    return 'No hay logs aún.'

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
