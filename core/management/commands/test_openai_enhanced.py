from django.core.management.base import BaseCommand
from django.conf import settings
from core.services import OpenAIService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Probar la integración mejorada con OpenAI GPT-5'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-key',
            action='store_true',
            help='Solo validar la API key',
        )
        parser.add_argument(
            '--model-info',
            action='store_true',
            help='Mostrar información del modelo',
        )

    def handle(self, *args, **options):
        if not settings.OPENAI_API_KEY:
            self.stdout.write(
                self.style.ERROR('❌ OPENAI_API_KEY no está configurada en settings')
            )
            return
        
        openai_service = OpenAIService()
        
        if options['test_key']:
            self._test_api_key(openai_service)
        elif options['model_info']:
            self._test_model_info(openai_service)
        else:
            self._test_full_integration(openai_service)

    def _test_api_key(self, openai_service):
        """Probar que la API key sea válida"""
        try:
            is_valid = openai_service.validate_api_key()
            if is_valid:
                self.stdout.write(
                    self.style.SUCCESS('✅ API Key válida - GPT-5 disponible')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ API Key inválida o modelo no disponible')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error validando API key: {e}')
            )

    def _test_model_info(self, openai_service):
        """Probar información del modelo"""
        try:
            # Intentar obtener información del modelo
            response = openai_service.client.models.list()
            gpt5_available = any(model.id == 'gpt-5' for model in response.data)
            
            if gpt5_available:
                self.stdout.write(
                    self.style.SUCCESS('✅ Modelo GPT-5 disponible')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Modelo GPT-5 no encontrado en la lista')
                )
                
            # Mostrar modelos disponibles
            self.stdout.write('\n📋 Modelos disponibles:')
            for model in response.data[:5]:  # Mostrar solo los primeros 5
                self.stdout.write(f'  - {model.id}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error obteniendo información del modelo: {e}')
            )

    def _test_full_integration(self, openai_service):
        """Probar integración completa"""
        self.stdout.write('🧪 Probando integración completa con GPT-5...')
        
        # Primero validar API key
        try:
            is_valid = openai_service.validate_api_key()
            if not is_valid:
                self.stdout.write(
                    self.style.ERROR('❌ API Key inválida')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error validando API key: {e}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('✅ API Key válida - Listo para análisis de imágenes')
        )
        
        # Mostrar información del prompt
        self.stdout.write('\n📝 Prompt de análisis:')
        self.stdout.write('  - Identifica alimentos en imágenes')
        self.stdout.write('  - Estima cantidades en gramos')
        self.stdout.write('  - Calcula calorías por 100g')
        self.stdout.write('  - Proporciona niveles de confianza')
        
        self.stdout.write('\n🚀 Para probar con una imagen real:')
        self.stdout.write('  1. Ve a http://127.0.0.1:8000/add-meal-enhanced/')
        self.stdout.write('  2. Selecciona tipo de comida')
        self.stdout.write('  3. Sube una foto de comida')
        self.stdout.write('  4. Revisa los resultados del análisis') 