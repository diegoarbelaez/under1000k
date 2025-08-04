# Guía de Despliegue en Render

## Problemas Solucionados

### 1. Error de DisallowedHost
- **Problema**: Django rechazaba el dominio `under1000k.onrender.com`
- **Solución**: Configurado `ALLOWED_HOSTS` en `render.yaml` para incluir el dominio de Render

### 2. Problema de Puertos
- **Problema**: Render no podía detectar un puerto abierto
- **Solución**: Configurado `gunicorn` para vincular al puerto `$PORT` que Render proporciona

## Archivos de Configuración

### render.yaml
```yaml
services:
  - type: web
    name: under1000k
    env: python
    plan: free
    buildCommand: ./build.sh
    startCommand: gunicorn under1000k.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: under1000k.onrender.com,localhost,127.0.0.1
      - key: STATIC_ROOT
        value: staticfiles
      - key: STATIC_URL
        value: /static/
      - key: MEDIA_ROOT
        value: media
      - key: MEDIA_URL
        value: /media/
```

### build.sh
```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

## Variables de Entorno Requeridas

En Render, asegúrate de configurar estas variables de entorno:

- `SECRET_KEY`: Generada automáticamente por Render
- `DEBUG`: false (para producción)
- `ALLOWED_HOSTS`: under1000k.onrender.com,localhost,127.0.0.1
- `OPENAI_API_KEY`: Tu clave de API de OpenAI (si usas funcionalidades de IA)

## Pasos para Desplegar

1. **Conectar el repositorio** a Render
2. **Configurar las variables de entorno** en el dashboard de Render
3. **Desplegar automáticamente** cuando se haga push al repositorio

## Verificación Local

Para probar localmente antes del despliegue:

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Probar gunicorn
gunicorn under1000k.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Si el despliegue falla:
1. Verificar que `gunicorn` esté en `requirements.txt`
2. Asegurar que `build.sh` sea ejecutable
3. Verificar que las variables de entorno estén configuradas
4. Revisar los logs en Render para errores específicos

### Si la aplicación no responde:
1. Verificar que el puerto esté configurado correctamente
2. Asegurar que `ALLOWED_HOSTS` incluya el dominio de Render
3. Verificar que las migraciones se hayan ejecutado correctamente 