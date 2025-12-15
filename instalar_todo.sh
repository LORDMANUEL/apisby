#!/bin/bash
# Instalador y configurador automático para Smartsheet API clonable
# Requiere: whiptail, python3, pip, cron

set -e


# Verificar e instalar dependencias del sistema (idempotente)
function instalar_dependencia() {
    local pkg="$1"
    until command -v "$pkg" &> /dev/null; do
        echo "[INFO] Instalando $pkg..."
        sudo apt-get update && sudo apt-get install -y "$pkg"
        sleep 1
    done
}

instalar_dependencia whiptail
instalar_dependencia python3
instalar_dependencia pip || instalar_dependencia python3-pip
instalar_dependencia crontab || instalar_dependencia cron

# Crear estructura de carpetas
mkdir -p "$(dirname "$0")/api/data"



# Crear y usar entorno virtual Python (idempotente y robusto)
VENV_DIR="$(dirname "$0")/api/venv"
until [ -d "$VENV_DIR" ]; do
    python3 -m venv "$VENV_DIR" || rm -rf "$VENV_DIR"
    sleep 1
done
source "$VENV_DIR/bin/activate"
until pip install --upgrade pip && pip install -r "$(dirname "$0")/api/requirements.txt"; do
    echo "[INFO] Reintentando instalación de dependencias Python..."
    sleep 2
done
deactivate

# Solicitar token al usuario
TOKEN=$(whiptail --title "Token Smartsheet" --inputbox "Pega tu token de Smartsheet API:" 10 60 3>&1 1>&2 2>&3)

if [ -z "$TOKEN" ]; then
    whiptail --msgbox "No se ingresó token. Abortando." 8 40
    exit 1
fi

# Guardar token en archivo oculto para la app web
TOKEN_FILE="$(dirname "$0")/api/.smartsheet_token"
echo "$TOKEN" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"


# Crear script de descarga para cron (usando venv)
CRON_SCRIPT="$(dirname "$0")/api/descarga_cron.sh"
cat > "$CRON_SCRIPT" << EOF
#!/bin/bash
export SMARTSHEET_API_TOKEN="$TOKEN"
cd "$(dirname "$0")"
source venv/bin/activate
python3 descarga_periodica.py --una-sola-ejecucion
deactivate
EOF
chmod +x "$CRON_SCRIPT"

# Agregar tarea al cron cada 3 minutos
(crontab -l 2>/dev/null | grep -v "$CRON_SCRIPT"; echo "*/3 * * * * $CRON_SCRIPT") | crontab -


whiptail --msgbox "Instalación y configuración completadas.\n\n- La descarga se ejecutará cada 3 minutos vía cron.\n- Puedes iniciar la web con: source api/venv/bin/activate && python3 api/app.py" 12 60
