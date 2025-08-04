from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import connection


class Command(BaseCommand):
    help = 'Diagnóstico de autenticación para verificar problemas de login'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Iniciando diagnóstico de autenticación...')
        
        # 1. Verificar usuarios existentes
        self.stdout.write('📊 Usuarios en la base de datos:')
        users = User.objects.all()
        for user in users:
            self.stdout.write(f'   - {user.username} (superuser: {user.is_superuser}, staff: {user.is_staff}, active: {user.is_active})')
        
        # 2. Verificar configuración de base de datos
        self.stdout.write('\n🗄️  Configuración de base de datos:')
        self.stdout.write(f'   - Engine: {connection.settings_dict["ENGINE"]}')
        self.stdout.write(f'   - Name: {connection.settings_dict["NAME"]}')
        
        # 3. Probar autenticación
        self.stdout.write('\n🔐 Probando autenticación:')
        
        # Probar admin
        admin_user = authenticate(username='admin', password='admin123')
        if admin_user:
            self.stdout.write(self.style.SUCCESS('✅ Admin autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Admin NO se puede autenticar'))
        
        # Probar demo
        demo_user = authenticate(username='demo', password='demo123')
        if demo_user:
            self.stdout.write(self.style.SUCCESS('✅ Demo autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Demo NO se puede autenticar'))
        
        # 4. Verificar si los usuarios están activos
        self.stdout.write('\n👤 Estado de usuarios:')
        admin_obj = User.objects.filter(username='admin').first()
        demo_obj = User.objects.filter(username='demo').first()
        
        if admin_obj:
            self.stdout.write(f'   - Admin: is_active={admin_obj.is_active}, is_staff={admin_obj.is_staff}, is_superuser={admin_obj.is_superuser}')
        else:
            self.stdout.write(self.style.ERROR('   - Admin: NO EXISTE'))
            
        if demo_obj:
            self.stdout.write(f'   - Demo: is_active={demo_obj.is_active}, is_staff={demo_obj.is_staff}, is_superuser={demo_obj.is_superuser}')
        else:
            self.stdout.write(self.style.ERROR('   - Demo: NO EXISTE'))
        
        # 5. Intentar recrear usuarios si hay problemas
        self.stdout.write('\n🔧 Intentando recrear usuarios...')
        
        # Recrear admin
        if admin_obj:
            admin_obj.delete()
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@under1000k.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        self.stdout.write(self.style.SUCCESS('✅ Admin recreado'))
        
        # Recrear demo
        if demo_obj:
            demo_obj.delete()
        demo_user = User.objects.create_user(
            username='demo',
            email='demo@under1000k.com',
            password='demo123',
            first_name='Usuario',
            last_name='Demo'
        )
        self.stdout.write(self.style.SUCCESS('✅ Demo recreado'))
        
        # 6. Probar autenticación nuevamente
        self.stdout.write('\n🔐 Probando autenticación después de recrear:')
        
        admin_user = authenticate(username='admin', password='admin123')
        if admin_user:
            self.stdout.write(self.style.SUCCESS('✅ Admin autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Admin NO se puede autenticar'))
        
        demo_user = authenticate(username='demo', password='demo123')
        if demo_user:
            self.stdout.write(self.style.SUCCESS('✅ Demo autenticado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Demo NO se puede autenticar'))
        
        self.stdout.write('\n📝 Credenciales finales:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Demo: demo / demo123') 