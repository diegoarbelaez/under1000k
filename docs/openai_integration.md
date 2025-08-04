# Integración con OpenAI - Under1000k

## Descripción

Este documento describe la integración con OpenAI GPT-4o API para el reconocimiento automático de alimentos en imágenes.

## Configuración

### 1. Obtener API Key de OpenAI

1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Ve a la sección "API Keys"
4. Crea una nueva API key
5. Copia la API key

### 2. Configurar la API Key

Edita el archivo `.env` y agrega tu API key:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
```

### 3. Verificar la Configuración

Ejecuta el comando de prueba:

```bash
python manage.py test_openai --test-key
```

## Servicios Disponibles

### OpenAIService

Clase principal para interactuar con la API de OpenAI.

#### Métodos Principales:

- `analyze_food_image(image_path)`: Analiza una imagen de comida
- `validate_api_key()`: Valida que la API key sea correcta
- `get_food_suggestions(food_name)`: Obtiene sugerencias de alimentos
- `save_analysis_to_database(food_image, analysis_data)`: Guarda análisis en BD

### FoodAnalysisService

Servicio de alto nivel que combina análisis y procesamiento.

#### Métodos Principales:

- `analyze_and_save(food_image)`: Analiza y guarda resultados
- `_process_analysis_for_ui(analysis_data)`: Procesa datos para la UI

## Flujo de Análisis

1. **Subida de Imagen**: El usuario sube una imagen de comida
2. **Codificación**: La imagen se codifica a base64
3. **Análisis OpenAI**: Se envía a GPT-4o con prompt específico
4. **Procesamiento**: Se parsea la respuesta JSON
5. **Guardado**: Se guarda en la base de datos
6. **UI**: Se procesan los datos para mostrar en la interfaz

## Prompt de Análisis

El prompt enviado a OpenAI incluye:

- Instrucciones para identificar alimentos
- Formato JSON específico para la respuesta
- Estimación de cantidades en gramos
- Cálculo de calorías por 100g
- Niveles de confianza

## Estructura de Respuesta

```json
{
    "foods": [
        {
            "name": "arroz",
            "estimated_grams": 150,
            "calories_per_100g": 130,
            "confidence": 0.9
        }
    ],
    "total_calories": 195,
    "analysis_confidence": 0.85,
    "notes": "Arroz blanco cocido identificado"
}
```

## Manejo de Errores

### Errores Comunes:

1. **API Key Inválida**: Error 401
2. **Límite de Tokens**: Error 429
3. **Imagen Inválida**: Error de codificación
4. **Respuesta Malformada**: Error de parsing JSON

### Logging

Todos los errores se registran en:
- `logs/under1000k.log`
- Consola (modo debug)

## Comandos de Prueba

### Validar API Key
```bash
python manage.py test_openai --test-key
```

### Prueba Completa
```bash
python manage.py test_openai
```

## Costos y Límites

### GPT-4 Vision Pricing:
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens

### Límites Recomendados:
- Máximo 1000 tokens por análisis
- Máximo 10MB por imagen
- Formato: JPEG, PNG, WEBP

## Optimizaciones

1. **Compresión de Imágenes**: Reducir tamaño antes del análisis
2. **Caché de Resultados**: Evitar análisis repetidos
3. **Batch Processing**: Procesar múltiples imágenes
4. **Fallback**: Usar análisis manual si OpenAI falla

## Seguridad

1. **API Key**: Nunca exponer en código
2. **Validación**: Verificar tipos de archivo
3. **Límites**: Implementar rate limiting
4. **Logs**: No registrar datos sensibles

## Próximos Pasos

1. Implementar compresión de imágenes
2. Agregar caché de resultados
3. Crear fallback manual
4. Optimizar prompts
5. Implementar rate limiting 