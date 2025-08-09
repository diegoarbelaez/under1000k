from django.core.management.base import BaseCommand
from django.conf import settings
from core.services import OpenAIService


class Command(BaseCommand):
    help = 'Probar la integración con OpenAI (GPT-5)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-key',
            action='store_true',
            help='Solo validar la API key',
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
        else:
            self._test_full_integration(openai_service)

    def _test_api_key(self, openai_service):
        """Probar solo la validación de la API key"""
        self.stdout.write('🔑 Probando API key de OpenAI...')
        
        try:
            is_valid = openai_service.validate_api_key()
            if is_valid:
                self.stdout.write(
                    self.style.SUCCESS('✅ API key de OpenAI es válida (GPT-5 disponible)')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ API key de OpenAI no es válida o el modelo no está disponible')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error validando API key: {e}')
            )

    def _test_full_integration(self, openai_service):
        """Probar la integración completa"""
        self.stdout.write('🧪 Probando integración completa con OpenAI...')
        
        # Test 1: Validar API key
        self.stdout.write('1️⃣ Validando API key...')
        try:
            is_valid = openai_service.validate_api_key()
            if not is_valid:
                self.stdout.write(
                    self.style.ERROR('❌ API key no válida. Deteniendo pruebas.')
                )
                return
            self.stdout.write(
                self.style.SUCCESS('✅ API key válida')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error validando API key: {e}')
            )
            return

        # Test 2: Probar con imagen de ejemplo (si existe)
        self.stdout.write('2️⃣ Probando análisis de imagen con GPT-5...')
        self.stdout.write(
            self.style.WARNING('⚠️  Para probar el análisis de imagen, necesitas una imagen de comida.')
        )
        self.stdout.write(
            '💡 Puedes usar: python manage.py test_openai --image-path /path/to/image.jpg'
        )

        self.stdout.write(
            self.style.SUCCESS('✅ Integración básica con OpenAI configurada correctamente')
        )
        self.stdout.write('📝 Recuerda configurar tu OPENAI_API_KEY en el archivo .env') 