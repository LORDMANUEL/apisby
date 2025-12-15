#!/bin/bash
echo "$TOKEN" > "$TOKEN_FILE"

# Instalador y configurador automático para Smartsheet API clonable
# Compatible con Ubuntu y Debian
# Requiere: whiptail, python3, pip, cron

set -e

echo "\n[INFO] Instalador para Smartsheet API clonable (Ubuntu/Debian)\n"
echo "Asegúrate de ejecutar este script con permisos de usuario normal (no root)."
echo "Si falta alguna dependencia, el script intentará instalarla automáticamente."

# Detectar sistema operativo
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="desconocido"
fi

# Verificar e instalar dependencias
function instalar_dependencia() {
    local pkg="$1"
    if ! command -v "$pkg" &> /dev/null; then
        echo "[INFO] Instalando $pkg..."
        if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
            sudo apt-get update && sudo apt-get install -y "$pkg"
        else
            echo "[ERROR] Sistema operativo no soportado automáticamente. Instala $pkg manualmente."
            exit 1
        fi
    fi
}

instalar_dependencia whiptail
instalar_dependencia python3
instalar_dependencia pip || instalar_dependencia python3-pip
instalar_dependencia crontab || instalar_dependencia cron

# Crear estructura de carpetas (idempotente)
mkdir -p "$(dirname "$0")/api/data"


# Crear y usar entorno virtual Python (idempotente)
VENV_DIR="$(dirname "$0")/api/venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
if ! pip install -r "$(dirname "$0")/api/requirements.txt"; then
    whiptail --msgbox "[ERROR] Falló la instalación de dependencias Python en el entorno virtual. Revisa el archivo requirements.txt o tu entorno." 10 60
    deactivate
    exit 1
fi
deactivate

# Solicitar token al usuario
TOKEN=$(whiptail --title "Token Smartsheet" --inputbox "Pega tu token de Smartsheet API:" 10 60 3>&1 1>&2 2>&3)

if [ -z "$TOKEN" ]; then
    whiptail --msgbox "No se ingresó token. Abortando." 8 40
    exit 1
fi

# Guardar token en archivo oculto para la app web (idempotente)
TOKEN_FILE="$(dirname "$0")/api/.smartsheet_token"
echo "$TOKEN" > "$TOKEN_FILE"


# Crear script de descarga para cron (idempotente)
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

# Agregar tarea al cron cada 3 minutos (idempotente)
if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
    echo "[INFO] Cron ya configurado."
else
    (crontab -l 2>/dev/null | grep -v "$CRON_SCRIPT"; echo "*/3 * * * * $CRON_SCRIPT") | crontab -
    echo "[INFO] Cron configurado para ejecutar cada 3 minutos."
fi



# Verificar e instalar Flask en el entorno virtual si falta
source "$VENV_DIR/bin/activate"
if ! python3 -c "import flask" 2>/dev/null; then
    pip install flask
fi
deactivate

whiptail --msgbox "Instalación y configuración completadas.\n\n- La descarga se ejecutará cada 3 minutos vía cron.\n- Puedes iniciar la web con: source api/venv/bin/activate && python3 api/app.py" 12 60
