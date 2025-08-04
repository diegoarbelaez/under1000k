from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Food, Drink, FoodCategory, DrinkCategory, MealRecord, DrinkRecord
from decimal import Decimal


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo'

    def handle(self, *args, **options):
        self.stdout.write('🍽️  Poblando datos de ejemplo...')
        
        # Obtener categorías
        try:
            frutas_cat = FoodCategory.objects.get(name='Frutas')
            verduras_cat = FoodCategory.objects.get(name='Verduras')
            carnes_cat = FoodCategory.objects.get(name='Carnes')
            lacteos_cat = FoodCategory.objects.get(name='Lácteos')
            cereales_cat = FoodCategory.objects.get(name='Cereales')
            
            agua_cat = DrinkCategory.objects.get(name='Agua')
            bebidas_azucaradas_cat = DrinkCategory.objects.get(name='Bebidas azucaradas')
            bebidas_sin_azucar_cat = DrinkCategory.objects.get(name='Bebidas sin azúcar')
        except FoodCategory.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Primero ejecuta: python manage.py populate_categories')
            )
            return
        
        # Crear alimentos de ejemplo
        foods_data = [
            {'name': 'Manzana', 'category': frutas_cat, 'calories_per_100g': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2},
            {'name': 'Plátano', 'category': frutas_cat, 'calories_per_100g': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3},
            {'name': 'Naranja', 'category': frutas_cat, 'calories_per_100g': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1},
            {'name': 'Lechuga', 'category': verduras_cat, 'calories_per_100g': 15, 'protein': 1.4, 'carbs': 2.9, 'fat': 0.1},
            {'name': 'Tomate', 'category': verduras_cat, 'calories_per_100g': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
            {'name': 'Pollo (pechuga)', 'category': carnes_cat, 'calories_per_100g': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6},
            {'name': 'Arroz blanco', 'category': cereales_cat, 'calories_per_100g': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
            {'name': 'Pan integral', 'category': cereales_cat, 'calories_per_100g': 247, 'protein': 13, 'carbs': 41, 'fat': 4.2},
            {'name': 'Leche entera', 'category': lacteos_cat, 'calories_per_100g': 61, 'protein': 3.2, 'carbs': 4.8, 'fat': 3.3},
            {'name': 'Yogur natural', 'category': lacteos_cat, 'calories_per_100g': 59, 'protein': 10, 'carbs': 3.6, 'fat': 0.4},
        ]
        
        for food_data in foods_data:
            food, created = Food.objects.get_or_create(
                name=food_data['name'],
                category=food_data['category'],
                defaults={
                    'calories_per_100g': food_data['calories_per_100g'],
                    'protein_per_100g': food_data['protein'],
                    'carbs_per_100g': food_data['carbs'],
                    'fat_per_100g': food_data['fat'],
                    'description': f'{food_data["name"]} - {food_data["category"].name}'
                }
            )
            if created:
                self.stdout.write(f'✅ Alimento creado: {food.name}')
            else:
                self.stdout.write(f'⚠️  Alimento ya existe: {food.name}')
        
        # Crear bebidas de ejemplo
        drinks_data = [
            {'name': 'Agua mineral', 'category': agua_cat, 'calories_per_100ml': 0},
            {'name': 'Coca-Cola', 'category': bebidas_azucaradas_cat, 'calories_per_100ml': 42},
            {'name': 'Pepsi', 'category': bebidas_azucaradas_cat, 'calories_per_100ml': 41},
            {'name': 'Té verde', 'category': bebidas_sin_azucar_cat, 'calories_per_100ml': 1},
            {'name': 'Café negro', 'category': bebidas_sin_azucar_cat, 'calories_per_100ml': 2},
            {'name': 'Zumo de naranja', 'category': bebidas_sin_azucar_cat, 'calories_per_100ml': 45},
        ]
        
        for drink_data in drinks_data:
            drink, created = Drink.objects.get_or_create(
                name=drink_data['name'],
                category=drink_data['category'],
                defaults={
                    'calories_per_100ml': drink_data['calories_per_100ml'],
                    'description': f'{drink_data["name"]} - {drink_data["category"].name}'
                }
            )
            if created:
                self.stdout.write(f'✅ Bebida creada: {drink.name}')
            else:
                self.stdout.write(f'⚠️  Bebida ya existe: {drink.name}')
        
        # Crear usuario de ejemplo si no existe
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@under1000k.com',
                'first_name': 'Usuario',
                'last_name': 'Demo'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write('✅ Usuario demo creado (usuario: demo, contraseña: demo123)')
        else:
            self.stdout.write('⚠️  Usuario demo ya existe')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Datos de ejemplo poblados exitosamente!')
        )
        self.stdout.write('📝 Puedes iniciar sesión con:')
        self.stdout.write('   Usuario: demo')
        self.stdout.write('   Contraseña: demo123') 