from flask import Flask, request, render_template_string, redirect
import os
from pathlib import Path
import subprocess

app = Flask(__name__)

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
</body></html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    token_path = Path(__file__).parent / '.smartsheet_token'
    if request.method == 'POST':
        token = request.form['token']
        with open(token_path, 'w') as f:
            f.write(token)
        os.environ['SMARTSHEET_API_TOKEN'] = token
        # Lanzar el script de descarga en segundo plano si no está corriendo
        subprocess.Popen(['python3', 'api/descarga_periodica.py'])
        return render_template_string(TEMPLATE_OK)
    if token_path.exists():
        return render_template_string(TEMPLATE_OK)
    return render_template_string(TEMPLATE_FORM)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
