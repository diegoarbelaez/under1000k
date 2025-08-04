# Under1000k - Contador de Calorías

Una aplicación web moderna para contar calorías diarias con el objetivo de mantener un consumo menor a 1000kcal por día.

## Características

- 📸 **Reconocimiento de alimentos por foto**: Toma una foto de tu comida y la app identificará los alimentos automáticamente
- 🎯 **Objetivo de 1000kcal**: Mantén un seguimiento claro de tu consumo diario
- 📊 **Dashboard intuitivo**: Visualiza tu progreso y estadísticas
- 📱 **Diseño responsive**: Funciona perfectamente en cualquier dispositivo
- 🗂️ **Historial completo**: Revisa todas tus comidas anteriores

## Tecnologías

- **Backend**: Django 5.x
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **IA**: OpenAI GPT-4 Vision API
- **Hosting**: Render/Vercel

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd under1000k
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

## Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Static Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
```

## Uso

1. **Registrarse/Iniciar sesión**: Crea una cuenta o inicia sesión
2. **Configurar objetivo**: Establece tu objetivo de calorías diarias
3. **Registrar comidas**: Toma una foto de tu comida y súbela
4. **Revisar análisis**: La IA identificará los alimentos y calculará las calorías
5. **Confirmar**: Ajusta las cantidades si es necesario y confirma
6. **Monitorear**: Revisa tu dashboard para ver tu progreso

## Estructura del Proyecto

```
under1000k/
├── core/                 # Aplicación principal
│   ├── models.py        # Modelos de datos
│   ├── views.py         # Vistas
│   ├── forms.py         # Formularios
│   └── services.py      # Servicios (OpenAI)
├── templates/           # Plantillas HTML
├── static/             # Archivos estáticos
├── media/              # Archivos subidos
└── under1000k/         # Configuración del proyecto
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

- Proyecto: [Under1000k](https://github.com/yourusername/under1000k)
- Email: tu-email@ejemplo.com 