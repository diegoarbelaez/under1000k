from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Modelo para el perfil extendido del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    daily_calorie_goal = models.IntegerField(default=1000, help_text="Objetivo de calorías diarias")
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


class FoodCategory(models.Model):
    """Categorías de alimentos"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff", help_text="Color en formato hexadecimal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría de Alimento"
        verbose_name_plural = "Categorías de Alimentos"


class DrinkCategory(models.Model):
    """Categorías de bebidas"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#28a745", help_text="Color en formato hexadecimal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría de Bebida"
        verbose_name_plural = "Categorías de Bebidas"


class Food(models.Model):
    """Modelo para alimentos"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='foods')
    calories_per_100g = models.DecimalField(max_digits=6, decimal_places=2)
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Alimento"
        verbose_name_plural = "Alimentos"
        unique_together = ['name', 'category']


class Drink(models.Model):
    """Modelo para bebidas"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(DrinkCategory, on_delete=models.CASCADE, related_name='drinks')
    calories_per_100ml = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Bebida"
        verbose_name_plural = "Bebidas"
        unique_together = ['name', 'category']


class FoodImage(models.Model):
    """Modelo para almacenar imágenes de comidas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_images')
    image = models.ImageField(upload_to='food_images/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="Tamaño del archivo en bytes")
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Imagen de {self.user.username} - {self.original_name}"

    class Meta:
        verbose_name = "Imagen de Comida"
        verbose_name_plural = "Imágenes de Comidas"


class OpenAIAnalysis(models.Model):
    """Modelo para almacenar análisis de OpenAI"""
    image = models.OneToOneField(FoodImage, on_delete=models.CASCADE, related_name='analysis')
    prompt_sent = models.TextField()
    response_received = models.TextField()
    identified_foods = models.JSONField(default=dict, help_text="Alimentos identificados en formato JSON")
    calculated_calories = models.DecimalField(max_digits=8, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, help_text="Puntuación de confianza (0-1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Análisis de {self.image.original_name}"

    class Meta:
        verbose_name = "Análisis de OpenAI"
        verbose_name_plural = "Análisis de OpenAI"


class MealRecord(models.Model):
    """Modelo para registrar comidas"""
    MEAL_TYPES = [
        ('breakfast', 'Desayuno'),
        ('lunch', 'Almuerzo'),
        ('dinner', 'Cena'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_records')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    image = models.ForeignKey(FoodImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='meal_records')
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} - {self.date}"

    class Meta:
        verbose_name = "Registro de Comida"
        verbose_name_plural = "Registros de Comidas"
        ordering = ['-date', '-time']


class DrinkRecord(models.Model):
    """Modelo para registrar bebidas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drink_records')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE, related_name='records')
    quantity_ml = models.IntegerField(help_text="Cantidad en mililitros")
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.drink.name} - {self.date}"

    class Meta:
        verbose_name = "Registro de Bebida"
        verbose_name_plural = "Registros de Bebidas"
        ordering = ['-date', '-time']


class MealDetail(models.Model):
    """Modelo para detalles de comidas (alimentos específicos en una comida)"""
    meal_record = models.ForeignKey(MealRecord, on_delete=models.CASCADE, related_name='details')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='meal_details')
    quantity_g = models.DecimalField(max_digits=6, decimal_places=2, help_text="Cantidad en gramos")
    calculated_calories = models.DecimalField(max_digits=8, decimal_places=2)
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, help_text="Nivel de confianza del análisis (0-1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food.name} - {self.quantity_g}g ({self.calculated_calories} kcal)"

    class Meta:
        verbose_name = "Detalle de Comida"
        verbose_name_plural = "Detalles de Comidas"


class UserSettings(models.Model):
    """Modelo para configuraciones de usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    daily_calorie_goal = models.IntegerField(default=1000)
    notifications_enabled = models.BooleanField(default=True)
    ui_theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
    ])
    language = models.CharField(max_length=10, default='es', choices=[
        ('es', 'Español'),
        ('en', 'English'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración de {self.user.username}"

    class Meta:
        verbose_name = "Configuración de Usuario"
        verbose_name_plural = "Configuraciones de Usuario"


class ActivityLog(models.Model):
    """Modelo para registrar actividad del usuario"""
    ACTION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('meal_added', 'Comida agregada'),
        ('drink_added', 'Bebida agregada'),
        ('photo_uploaded', 'Foto subida'),
        ('analysis_requested', 'Análisis solicitado'),
        ('settings_updated', 'Configuración actualizada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at}"

    class Meta:
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"
        ordering = ['-created_at']
