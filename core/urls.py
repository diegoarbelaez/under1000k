from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de comidas
    path('add-meal/', views.add_meal, name='add_meal'),
    path('add-meal-enhanced/', views.add_meal_enhanced, name='add_meal_enhanced'),
    path('meal/<int:meal_id>/analysis/', views.meal_analysis, name='meal_analysis'),
    path('meal/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('meal-history/', views.meal_history, name='meal_history'),
    
    # Gestión de bebidas
    path('add-drink/', views.add_drink, name='add_drink'),
    path('drink-history/', views.drink_history, name='drink_history'),
    
    # Configuración y estadísticas
    path('settings/', views.user_settings, name='user_settings'),
    path('statistics/', views.statistics, name='statistics'),
    
    # APIs
    path('api/analyze-image/', views.api_analyze_image, name='api_analyze_image'),
    path('api/analyze-image-enhanced/', views.api_analyze_image_enhanced, name='api_analyze_image_enhanced'),
    path('api/save-meal/', views.api_save_meal, name='api_save_meal'),
    path('api/food-suggestions/', views.api_food_suggestions, name='api_food_suggestions'),
] 