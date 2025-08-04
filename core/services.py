import base64
import json
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.files.base import ContentFile
from openai import OpenAI
from .models import FoodImage, OpenAIAnalysis, Food, FoodCategory

logger = logging.getLogger(__name__)


class OpenAIService:
    """Servicio para interactuar con la API de OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Codifica una imagen a base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error codificando imagen: {e}")
            raise
    
    def analyze_food_image(self, image_path: str) -> Dict:
        """
        Analiza una imagen de comida usando GPT-4 Vision
        Retorna un diccionario con los alimentos identificados y sus calorías
        """
        try:
            # Codificar imagen
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prompt para análisis de alimentos
            prompt = """
            Analiza esta imagen de comida y proporciona la siguiente información en formato JSON:
            
            {
                "foods": [
                    {
                        "name": "nombre del alimento",
                        "estimated_grams": cantidad estimada en gramos,
                        "calories_per_100g": calorías por 100g (estimación realista),
                        "confidence": nivel de confianza (0-1)
                    }
                ],
                "total_calories": calorías totales estimadas,
                "analysis_confidence": confianza general del análisis (0-1),
                "notes": "observaciones adicionales"
            }
            
            Reglas importantes:
            - Identifica todos los alimentos visibles en la imagen
            - Estima las cantidades en gramos de manera realista
            - Proporciona calorías por 100g basadas en valores nutricionales estándar:
              * Carne de pollo: ~165 kcal/100g
              * Carne de res: ~250 kcal/100g
              * Salchicha: ~300 kcal/100g
              * Papas fritas/asadas: ~200 kcal/100g
              * Arroz: ~130 kcal/100g
              * Pan: ~250 kcal/100g
              * Queso: ~350 kcal/100g
              * Huevo: ~155 kcal/100g
              * Lechuga: ~15 kcal/100g
              * Tomate: ~20 kcal/100g
              * Bebidas azucaradas: ~40 kcal/100ml
            - Calcula las calorías totales sumando (gramos * calorías/100g) / 100
            - Sé específico con los nombres de alimentos
            - Si no estás seguro de algún alimento, inclúyelo con baja confianza
            - NO devuelvas calorías en 0, siempre proporciona una estimación realista
            """
            
            # Llamada a la API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Procesar respuesta
            response_text = response.choices[0].message.content
            analysis_data = self._parse_openai_response(response_text)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analizando imagen con OpenAI: {e}")
            raise
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parsea la respuesta de OpenAI y la convierte en un diccionario estructurado"""
        try:
            # Buscar JSON en la respuesta
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Validar estructura
            required_keys = ['foods', 'total_calories', 'analysis_confidence']
            for key in required_keys:
                if key not in parsed_data:
                    raise ValueError(f"Falta clave requerida: {key}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de OpenAI: {e}")
            # Retornar estructura por defecto
            return {
                'foods': [],
                'total_calories': 0,
                'analysis_confidence': 0.0,
                'notes': 'Error parseando respuesta de OpenAI'
            }
        except Exception as e:
            logger.error(f"Error procesando respuesta de OpenAI: {e}")
            raise
    
    def save_analysis_to_database(self, food_image: FoodImage, analysis_data: Dict) -> OpenAIAnalysis:
        """Guarda el análisis de OpenAI en la base de datos"""
        try:
            # Crear registro de análisis
            analysis = OpenAIAnalysis.objects.create(
                image=food_image,
                prompt_sent=analysis_data.get('prompt', ''),
                response_received=json.dumps(analysis_data),
                identified_foods=analysis_data.get('foods', []),
                calculated_calories=analysis_data.get('total_calories', 0),
                confidence_score=analysis_data.get('analysis_confidence', 0.0)
            )
            
            logger.info(f"Análisis guardado para imagen {food_image.id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error guardando análisis en BD: {e}")
            raise
    
    def get_food_suggestions(self, food_name: str) -> List[Dict]:
        """Obtiene sugerencias de alimentos basadas en el nombre"""
        try:
            # Buscar alimentos similares en la base de datos
            foods = Food.objects.filter(name__icontains=food_name)[:5]
            
            suggestions = []
            for food in foods:
                suggestions.append({
                    'id': food.id,
                    'name': food.name,
                    'category': food.category.name,
                    'calories_per_100g': float(food.calories_per_100g),
                    'protein_per_100g': float(food.protein_per_100g),
                    'carbs_per_100g': float(food.carbs_per_100g),
                    'fat_per_100g': float(food.fat_per_100g)
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error obteniendo sugerencias de alimentos: {e}")
            return []
    
    def validate_api_key(self) -> bool:
        """Valida que la API key de OpenAI sea válida"""
        try:
            # Hacer una llamada simple para validar
            response = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Error validando API key de OpenAI: {e}")
            return False


class FoodAnalysisService:
    """Servicio para el análisis completo de alimentos"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def analyze_and_save(self, food_image: FoodImage) -> Tuple[OpenAIAnalysis, Dict]:
        """
        Analiza una imagen de comida y guarda los resultados
        Retorna el análisis guardado y los datos procesados
        """
        try:
            # Analizar imagen con OpenAI
            analysis_data = self.openai_service.analyze_food_image(food_image.image.path)
            
            # Guardar análisis en BD
            analysis = self.openai_service.save_analysis_to_database(food_image, analysis_data)
            
            # Procesar datos para la UI
            processed_data = self._process_analysis_for_ui(analysis_data)
            
            return analysis, processed_data
            
        except Exception as e:
            logger.error(f"Error en análisis completo: {e}")
            raise
    
    def _process_analysis_for_ui(self, analysis_data: Dict) -> Dict:
        """Procesa los datos del análisis para la interfaz de usuario"""
        try:
            foods = analysis_data.get('foods', [])
            
            # Procesar cada alimento para calcular calorías individuales
            processed_foods = []
            total_calories = 0
            
            for food in foods:
                # Calcular calorías individuales
                calories_per_100g = food.get('calories_per_100g', 0)
                estimated_grams = food.get('estimated_grams', 0)
                individual_calories = (calories_per_100g * estimated_grams) / 100
                
                # Crear item procesado con calorías calculadas
                processed_food = {
                    'name': food.get('name', 'Alimento desconocido'),
                    'quantity': estimated_grams if estimated_grams > 0 else 100,  # Valor por defecto si es 0
                    'unit': 'g',
                    'calories': round(individual_calories, 2),  # Calorías calculadas
                    'confidence': food.get('confidence', 0.5),
                    'type': 'food'  # Por defecto es comida
                }
                
                processed_foods.append(processed_food)
                total_calories += individual_calories
            
            total_grams = sum(food.get('estimated_grams', 0) for food in foods)
            
            # Agrupar por categorías
            categories = {}
            for food in foods:
                category = self._categorize_food(food.get('name', ''))
                if category not in categories:
                    categories[category] = []
                categories[category].append(food)
            
            return {
                'foods': processed_foods,  # Usar alimentos procesados
                'total_calories': round(total_calories, 2),
                'total_grams': round(total_grams, 2),
                'analysis_confidence': analysis_data.get('analysis_confidence', 0.0),
                'categories': categories,
                'notes': analysis_data.get('notes', ''),
                'food_count': len(processed_foods)
            }
            
        except Exception as e:
            logger.error(f"Error procesando datos para UI: {e}")
            return {
                'foods': [],
                'total_calories': 0,
                'total_grams': 0,
                'analysis_confidence': 0.0,
                'categories': {},
                'notes': 'Error procesando datos',
                'food_count': 0
            }
    
    def _categorize_food(self, food_name: str) -> str:
        """Categoriza un alimento basándose en su nombre"""
        food_name_lower = food_name.lower()
        
        # Mapeo de categorías
        category_mapping = {
            'frutas': ['manzana', 'plátano', 'naranja', 'fresa', 'uva', 'pera', 'piña', 'mango'],
            'verduras': ['lechuga', 'tomate', 'zanahoria', 'brócoli', 'espinaca', 'cebolla', 'pimiento'],
            'carnes': ['pollo', 'res', 'cerdo', 'pavo', 'cordero', 'ternera'],
            'pescados': ['salmón', 'atún', 'bacalao', 'trucha', 'merluza'],
            'lácteos': ['leche', 'queso', 'yogur', 'mantequilla', 'crema'],
            'cereales': ['arroz', 'pasta', 'pan', 'avena', 'trigo', 'maíz'],
            'legumbres': ['frijol', 'lenteja', 'garbanzo', 'haba', 'guisante'],
            'frutos secos': ['almendra', 'nuez', 'cacahuete', 'avellana', 'pistacho'],
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in food_name_lower for keyword in keywords):
                return category
        
        return 'otros' 