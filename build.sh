#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Configuración completa de la base de datos
python manage.py setup_production

# Diagnóstico de autenticación
python manage.py check_auth 