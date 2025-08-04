from django.core.management.base import BaseCommand
from core.models import MealRecord
from decimal import Decimal

class Command(BaseCommand):
    help = 'Agregar calorías a comidas existentes que tienen 0 calorías'

    def add_arguments(self, parser):
        parser.add_argument(
            '--calories',
            type=int,
            default=300,
            help='Calorías a asignar por defecto (default: 300)',
        )

    def handle(self, *args, **options):
        default_calories = options['calories']
        
        # Obtener comidas con 0 calorías
        meals_with_zero_calories = MealRecord.objects.filter(total_calories=0)
        
        if not meals_with_zero_calories.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ No hay comidas con 0 calorías')
            )
            return
        
        self.stdout.write(f'📊 Encontradas {meals_with_zero_calories.count()} comidas con 0 calorías')
        
        # Actualizar calorías
        updated_count = 0
        for meal in meals_with_zero_calories:
            meal.total_calories = Decimal(default_calories)
            meal.save()
            updated_count += 1
            self.stdout.write(
                f'✅ Comida {meal.id} ({meal.get_meal_type_display()}) actualizada con {default_calories} kcal'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Se actualizaron {updated_count} comidas con {default_calories} kcal cada una')
        ) 