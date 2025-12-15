#!/bin/bash
# Instalador y configurador automático para Smartsheet API clonable
# Requiere: whiptail, python3, pip, cron

set -e

# Verificar dependencias
if ! command -v whiptail &> /dev/null; then
    echo "Instalando whiptail..."
    sudo apt-get update && sudo apt-get install -y whiptail
fi
if ! command -v python3 &> /dev/null; then
    echo "Python3 es requerido. Instálalo antes de continuar."
    exit 1
fi
if ! command -v pip &> /dev/null; then
    echo "Instalando pip..."
    sudo apt-get install -y python3-pip
fi
if ! command -v crontab &> /dev/null; then
    echo "Instalando cron..."
    sudo apt-get install -y cron
fi

# Crear estructura de carpetas
mkdir -p "$(dirname "$0")/api/data"

# Instalar dependencias Python
pip install --user -r "$(dirname "$0")/api/requirements.txt"

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

# Crear script de descarga para cron
CRON_SCRIPT="$(dirname "$0")/api/descarga_cron.sh"
cat > "$CRON_SCRIPT" << EOF
#!/bin/bash
export SMARTSHEET_API_TOKEN=\"$TOKEN\"
cd "$(dirname "$0")"
python3 descarga_periodica.py --una-sola-ejecucion
EOF
chmod +x "$CRON_SCRIPT"

# Agregar tarea al cron cada 3 minutos
(crontab -l 2>/dev/null | grep -v "$CRON_SCRIPT"; echo "*/3 * * * * $CRON_SCRIPT") | crontab -

whiptail --msgbox "Instalación y configuración completadas.\n\n- La descarga se ejecutará cada 3 minutos vía cron.\n- Puedes iniciar la web con: python3 api/app.py" 12 60
