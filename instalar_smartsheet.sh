#!/bin/bash
# Instalador interactivo para Smartsheet SDK y configuración de token
# Requiere: whiptail, python3, pip

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

# Crear estructura de carpetas
mkdir -p "$(dirname "$0")/api/data"

# Instalar dependencias Python
pip install --user smartsheet-python-sdk schedule

# Solicitar token al usuario
TOKEN=$(whiptail --title "Token Smartsheet" --inputbox "Pega tu token de Smartsheet API:" 10 60 3>&1 1>&2 2>&3)

if [ -z "$TOKEN" ]; then
    whiptail --msgbox "No se ingresó token. Abortando." 8 40
    exit 1
fi

# Guardar token en variable de entorno local
PROFILE="$HOME/.bashrc"
if ! grep -q 'SMARTSHEET_API_TOKEN' "$PROFILE"; then
    echo "export SMARTSHEET_API_TOKEN=\"$TOKEN\"" >> "$PROFILE"
    whiptail --msgbox "Token guardado en $PROFILE. Reinicia tu terminal o ejecuta: source $PROFILE" 10 60
else
    sed -i '/SMARTSHEET_API_TOKEN/d' "$PROFILE"
    echo "export SMARTSHEET_API_TOKEN=\"$TOKEN\"" >> "$PROFILE"
    whiptail --msgbox "Token actualizado en $PROFILE. Reinicia tu terminal o ejecuta: source $PROFILE" 10 60
fi

whiptail --msgbox "Instalación y configuración completadas. Ejecuta el script:\n\npython3 api/descarga_periodica.py" 12 60
