from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crear un superusuario para el panel de administración'

    def handle(self, *args, **options):
        self.stdout.write('👤 Creando superusuario...')
        
        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@under1000k.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Superusuario creado exitosamente!')
            )
            self.stdout.write('📝 Credenciales del admin:')
            self.stdout.write('   Usuario: admin')
            self.stdout.write('   Contraseña: admin123')
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  El superusuario admin ya existe')
            )
            self.stdout.write('📝 Credenciales del admin:')
            self.stdout.write('   Usuario: admin')
            self.stdout.write('   Contraseña: admin123') 