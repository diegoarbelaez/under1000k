from django.core.management.base import BaseCommand
from core.models import FoodCategory, DrinkCategory


class Command(BaseCommand):
    help = 'Poblar las categorías de alimentos y bebidas con datos iniciales'

    def handle(self, *args, **options):
        # Categorías de alimentos
        food_categories = [
            {'name': 'Frutas', 'color': '#FF6B6B', 'description': 'Frutas frescas y secas'},
            {'name': 'Verduras', 'color': '#4ECDC4', 'description': 'Verduras y hortalizas'},
            {'name': 'Carnes', 'color': '#FF8A80', 'description': 'Carnes rojas y blancas'},
            {'name': 'Pescados', 'color': '#81C784', 'description': 'Pescados y mariscos'},
            {'name': 'Huevos', 'color': '#FFD54F', 'description': 'Huevos y derivados'},
            {'name': 'Lácteos', 'color': '#90A4AE', 'description': 'Leche y productos lácteos'},
            {'name': 'Legumbres', 'color': '#8D6E63', 'description': 'Legumbres y granos'},
            {'name': 'Cereales', 'color': '#D7CCC8', 'description': 'Cereales y granos'},
            {'name': 'Frutos secos', 'color': '#BCAAA4', 'description': 'Frutos secos y semillas'},
            {'name': 'Semillas', 'color': '#A5D6A7', 'description': 'Semillas y granos'},
            {'name': 'Frutos de mar', 'color': '#4FC3F7', 'description': 'Mariscos y crustáceos'},
            {'name': 'Mariscos', 'color': '#29B6F6', 'description': 'Mariscos y moluscos'},
        ]

        # Categorías de bebidas
        drink_categories = [
            {'name': 'Agua', 'color': '#2196F3', 'description': 'Agua natural y mineral'},
            {'name': 'Bebidas azucaradas', 'color': '#F44336', 'description': 'Refrescos y bebidas con azúcar'},
            {'name': 'Bebidas sin azúcar', 'color': '#4CAF50', 'description': 'Bebidas sin azúcar añadido'},
            {'name': 'Bebidas alcohólicas', 'color': '#FF9800', 'description': 'Cerveza, vino y licores'},
            {'name': 'Bebidas energéticas', 'color': '#9C27B0', 'description': 'Bebidas energéticas y estimulantes'},
            {'name': 'Bebidas deportivas', 'color': '#00BCD4', 'description': 'Bebidas isotónicas y deportivas'},
        ]

        # Crear categorías de alimentos
        for category_data in food_categories:
            category, created = FoodCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'color': category_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría de alimento creada: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Categoría de alimento ya existe: {category.name}')
                )

        # Crear categorías de bebidas
        for category_data in drink_categories:
            category, created = DrinkCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'color': category_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría de bebida creada: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Categoría de bebida ya existe: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('¡Categorías pobladas exitosamente!')
        ) 