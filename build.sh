#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Poblar categorías y datos de ejemplo
python manage.py populate_categories
python manage.py populate_sample_data 