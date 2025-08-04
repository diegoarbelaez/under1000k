from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from core.models import Food, Drink, FoodCategory, DrinkCategory, MealRecord, DrinkRecord
from decimal import Decimal


class Command(BaseCommand):
    help = 'Configuración completa para producción: migraciones, categorías, datos y usuarios'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando configuración completa para producción...')
        
        # 1. Ejecutar migraciones
        self.stdout.write('📊 Ejecutando migraciones...')
        call_command('migrate')
        
        # 2. Poblar categorías
        self.stdout.write('📂 Poblando categorías...')
        call_command('populate_categories')
        
        # 3. Poblar datos de ejemplo
        self.stdout.write('🍽️  Poblando datos de ejemplo...')
        call_command('populate_sample_data')
        
        # 4. Crear superusuario admin
        self.stdout.write('👤 Creando superusuario admin...')
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@under1000k.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superusuario admin creado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Superusuario admin ya existe'))
        
        # 5. Crear usuario demo
        self.stdout.write('👤 Creando usuario demo...')
        if not User.objects.filter(username='demo').exists():
            demo_user = User.objects.create_user(
                username='demo',
                email='demo@under1000k.com',
                password='demo123',
                first_name='Usuario',
                last_name='Demo'
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuario demo creado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Usuario demo ya existe'))
        
        # 6. Verificar datos
        self.stdout.write('🔍 Verificando datos...')
        user_count = User.objects.count()
        food_count = Food.objects.count()
        drink_count = Drink.objects.count()
        category_count = FoodCategory.objects.count() + DrinkCategory.objects.count()
        
        self.stdout.write(f'📊 Resumen de datos:')
        self.stdout.write(f'   - Usuarios: {user_count}')
        self.stdout.write(f'   - Alimentos: {food_count}')
        self.stdout.write(f'   - Bebidas: {drink_count}')
        self.stdout.write(f'   - Categorías: {category_count}')
        
        self.stdout.write(self.style.SUCCESS('🎉 Configuración completa exitosa!'))
        self.stdout.write('📝 Credenciales disponibles:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Demo: demo / demo123') 