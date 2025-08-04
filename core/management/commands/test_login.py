from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


class Command(BaseCommand):
    help = 'Probar funcionalidad de login directamente'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Probando funcionalidad de login...')
        
        # 1. Verificar usuarios
        self.stdout.write('📊 Verificando usuarios:')
        admin_user = User.objects.filter(username='admin').first()
        demo_user = User.objects.filter(username='demo').first()
        
        if admin_user:
            self.stdout.write(f'   - Admin: {admin_user.username} (active: {admin_user.is_active}, staff: {admin_user.is_staff})')
        else:
            self.stdout.write(self.style.ERROR('   - Admin: NO EXISTE'))
            
        if demo_user:
            self.stdout.write(f'   - Demo: {demo_user.username} (active: {demo_user.is_active}, staff: {demo_user.is_staff})')
        else:
            self.stdout.write(self.style.ERROR('   - Demo: NO EXISTE'))
        
        # 2. Probar autenticación directa
        self.stdout.write('\n🔐 Probando autenticación directa:')
        
        admin_auth = authenticate(username='admin', password='admin123')
        if admin_auth:
            self.stdout.write(self.style.SUCCESS('✅ Admin autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Admin NO se puede autenticar'))
        
        demo_auth = authenticate(username='demo', password='demo123')
        if demo_auth:
            self.stdout.write(self.style.SUCCESS('✅ Demo autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Demo NO se puede autenticar'))
        
        # 3. Probar login con Client (simula requests HTTP)
        self.stdout.write('\n🌐 Probando login con Client:')
        
        client = Client()
        
        # Obtener página de login
        login_url = reverse('admin:login')
        response = client.get(login_url, HTTP_HOST='localhost')
        self.stdout.write(f'   GET {login_url}: {response.status_code}')
        
        if response.status_code == 200:
            # Extraer CSRF token
            csrf_token = None
            if hasattr(response, 'context') and response.context:
                csrf_token = response.context.get('csrf_token')
            
            if not csrf_token:
                # Intentar extraer del contenido
                content = response.content.decode('utf-8')
                if 'csrfmiddlewaretoken' in content:
                    import re
                    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
                    if match:
                        csrf_token = match.group(1)
            
            if csrf_token:
                self.stdout.write(f'   CSRF Token: {csrf_token[:20]}...')
                
                # Intentar login con admin
                login_data = {
                    'username': 'admin',
                    'password': 'admin123',
                    'csrfmiddlewaretoken': csrf_token
                }
                
                response = client.post(login_url, data=login_data, follow=True)
                self.stdout.write(f'   POST admin login: {response.status_code}')
                
                if response.status_code == 200:
                    # Verificar si estamos en el admin
                    if 'admin' in response.content.decode('utf-8').lower():
                        self.stdout.write(self.style.SUCCESS('✅ Login admin exitoso'))
                    else:
                        self.stdout.write(self.style.ERROR('❌ Login admin falló'))
                else:
                    self.stdout.write(f'   Response: {response.status_code}')
            else:
                self.stdout.write(self.style.ERROR('❌ No se pudo obtener CSRF token'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ No se pudo acceder a {login_url}'))
        
        # 4. Verificar configuración de sesiones
        self.stdout.write('\n🔧 Verificando configuración:')
        from django.conf import settings
        self.stdout.write(f'   SESSION_ENGINE: {getattr(settings, "SESSION_ENGINE", "default")}')
        self.stdout.write(f'   SESSION_COOKIE_SECURE: {getattr(settings, "SESSION_COOKIE_SECURE", "not set")}')
        self.stdout.write(f'   SESSION_COOKIE_HTTPONLY: {getattr(settings, "SESSION_COOKIE_HTTPONLY", "not set")}')
        
        # 5. Crear usuario de prueba si es necesario
        if not admin_user:
            self.stdout.write('\n🔧 Creando usuario admin...')
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@under1000k.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuario admin creado'))
        
        self.stdout.write('\n📝 Credenciales de prueba:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Demo: demo / demo123') 