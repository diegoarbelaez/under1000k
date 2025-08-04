from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.conf import settings


class Command(BaseCommand):
    help = 'Verificar configuración de CSRF y probar funcionalidad'

    def handle(self, *args, **options):
        self.stdout.write('🔒 Verificando configuración de CSRF...')
        
        # 1. Verificar configuración de CSRF
        self.stdout.write('📋 Configuración de CSRF:')
        self.stdout.write(f'   CSRF_COOKIE_SECURE: {getattr(settings, "CSRF_COOKIE_SECURE", "not set")}')
        self.stdout.write(f'   CSRF_COOKIE_HTTPONLY: {getattr(settings, "CSRF_COOKIE_HTTPONLY", "not set")}')
        self.stdout.write(f'   CSRF_COOKIE_SAMESITE: {getattr(settings, "CSRF_COOKIE_SAMESITE", "not set")}')
        self.stdout.write(f'   SESSION_COOKIE_SECURE: {getattr(settings, "SESSION_COOKIE_SECURE", "not set")}')
        self.stdout.write(f'   SESSION_COOKIE_HTTPONLY: {getattr(settings, "SESSION_COOKIE_HTTPONLY", "not set")}')
        self.stdout.write(f'   SESSION_COOKIE_SAMESITE: {getattr(settings, "SESSION_COOKIE_SAMESITE", "not set")}')
        
        # 2. Probar obtención de página de login
        self.stdout.write('\n🌐 Probando obtención de página de login:')
        client = Client()
        
        try:
            response = client.get(reverse('admin:login'), HTTP_HOST='localhost')
            self.stdout.write(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Página de login accesible'))
                
                # Verificar si hay CSRF token en la respuesta
                content = response.content.decode('utf-8')
                if 'csrfmiddlewaretoken' in content:
                    self.stdout.write(self.style.SUCCESS('✅ CSRF token encontrado en la página'))
                    
                    # Extraer CSRF token
                    import re
                    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
                    if match:
                        csrf_token = match.group(1)
                        self.stdout.write(f'   CSRF Token: {csrf_token[:20]}...')
                        
                        # Probar login con CSRF token
                        self.stdout.write('\n🔐 Probando login con CSRF token:')
                        login_data = {
                            'username': 'admin',
                            'password': 'admin123',
                            'csrfmiddlewaretoken': csrf_token
                        }
                        
                        response = client.post(reverse('admin:login'), data=login_data, HTTP_HOST='localhost')
                        self.stdout.write(f'   Status: {response.status_code}')
                        
                        if response.status_code == 302:
                            self.stdout.write(self.style.SUCCESS('✅ Login exitoso con CSRF'))
                        elif response.status_code == 200:
                            # Verificar si hay mensaje de error CSRF
                            content = response.content.decode('utf-8')
                            if 'CSRF verification failed' in content:
                                self.stdout.write(self.style.ERROR('❌ Error CSRF en login'))
                            else:
                                self.stdout.write(self.style.WARNING('⚠️  Login falló por otra razón'))
                        else:
                            self.stdout.write(f'   Response: {response.status_code}')
                    else:
                        self.stdout.write(self.style.ERROR('❌ No se pudo extraer CSRF token'))
                else:
                    self.stdout.write(self.style.ERROR('❌ No se encontró CSRF token en la página'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error al acceder a página de login: {response.status_code}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante la prueba: {str(e)}'))
        
        # 3. Verificar middleware
        self.stdout.write('\n🔧 Verificando middleware:')
        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
        
        if csrf_middleware in middleware_classes:
            self.stdout.write(self.style.SUCCESS('✅ CSRF middleware activo'))
        else:
            self.stdout.write(self.style.ERROR('❌ CSRF middleware NO activo'))
        
        # 4. Verificar configuración de cookies
        self.stdout.write('\n🍪 Verificando configuración de cookies:')
        self.stdout.write(f'   DEBUG: {settings.DEBUG}')
        self.stdout.write(f'   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        
        self.stdout.write('\n📝 Recomendaciones:')
        if not settings.DEBUG:
            self.stdout.write('   - En producción, asegúrate de que las cookies se configuren correctamente')
            self.stdout.write('   - Verifica que el dominio esté en ALLOWED_HOSTS')
            self.stdout.write('   - Considera usar HTTPS para cookies seguras')
        else:
            self.stdout.write('   - En desarrollo, las cookies funcionan normalmente')
            self.stdout.write('   - Para producción, configura CSRF_COOKIE_SECURE=True') 