import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    UserProfile, MealRecord, DrinkRecord, FoodImage, 
    OpenAIAnalysis, Food, Drink, UserSettings, ActivityLog, DrinkCategory, FoodCategory, MealDetail
)
from .services import FoodAnalysisService

logger = logging.getLogger(__name__)


def index(request):
    """Vista principal - redirige al dashboard si está autenticado"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/index.html')


@login_required
def dashboard(request):
    """Dashboard principal con resumen de calorías del día"""
    today = timezone.now().date()
    
    # Obtener o crear perfil de usuario
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'daily_calorie_goal': 1000}
    )
    
    # Obtener registros del día
    today_meals = MealRecord.objects.filter(
        user=request.user,
        date=today
    )
    
    today_drinks = DrinkRecord.objects.filter(
        user=request.user,
        date=today
    )
    
    # Calcular totales
    total_meal_calories = today_meals.aggregate(
        total=Sum('total_calories')
    )['total'] or 0
    
    total_drink_calories = today_drinks.aggregate(
        total=Sum('total_calories')
    )['total'] or 0
    
    total_calories = total_meal_calories + total_drink_calories
    remaining_calories = user_profile.daily_calorie_goal - total_calories
    
    # Calcular porcentaje
    percentage_used = (total_calories / user_profile.daily_calorie_goal) * 100 if user_profile.daily_calorie_goal > 0 else 0
    
    # Obtener últimas comidas
    recent_meals = today_meals.order_by('-time')[:5]
    recent_drinks = today_drinks.order_by('-time')[:5]
    
    # Estadísticas de la semana
    week_start = today - timedelta(days=today.weekday())
    week_meals = MealRecord.objects.filter(
        user=request.user,
        date__gte=week_start
    )
    
    weekly_calories = week_meals.aggregate(
        total=Sum('total_calories')
    )['total'] or 0
    
    context = {
        'user_profile': user_profile,
        'total_calories': total_calories,
        'remaining_calories': remaining_calories,
        'percentage_used': round(percentage_used, 1),
        'recent_meals': recent_meals,
        'recent_drinks': recent_drinks,
        'weekly_calories': weekly_calories,
        'today': today,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def add_meal(request):
    """Vista para agregar una nueva comida"""
    if request.method == 'POST':
        # Procesar formulario de comida
        meal_type = request.POST.get('meal_type')
        notes = request.POST.get('notes', '')
        estimated_calories = request.POST.get('estimated_calories', 350)
        
        # Validar calorías
        try:
            estimated_calories = int(estimated_calories)
            if estimated_calories < 50 or estimated_calories > 2000:
                estimated_calories = 350
        except (ValueError, TypeError):
            estimated_calories = 350
        
        # Crear registro de comida
        meal = MealRecord.objects.create(
            user=request.user,
            meal_type=meal_type,
            notes=notes,
            total_calories=estimated_calories  # Usar calorías estimadas
        )
        
        # Registrar actividad
        ActivityLog.objects.create(
            user=request.user,
            action='meal_added',
            details={'meal_id': meal.id, 'meal_type': meal_type, 'estimated_calories': estimated_calories}
        )
        
        messages.success(request, f'Comida registrada exitosamente con {estimated_calories} kcal estimadas')
        return redirect('core:meal_analysis', meal_id=meal.id)
    
    return render(request, 'core/add_meal.html')


@login_required
def add_meal_enhanced(request):
    """Nueva vista mejorada para agregar comidas con análisis de IA"""
    return render(request, 'core/add_meal_enhanced.html')


@login_required
def meal_analysis(request, meal_id):
    """Vista para analizar una comida con imagen"""
    meal = get_object_or_404(MealRecord, id=meal_id, user=request.user)
    
    if request.method == 'POST':
        # Procesar subida de imagen
        if 'food_image' in request.FILES:
            image_file = request.FILES['food_image']
            
            # Crear registro de imagen
            food_image = FoodImage.objects.create(
                user=request.user,
                image=image_file,
                original_name=image_file.name,
                file_size=image_file.size,
                mime_type=image_file.content_type
            )
            
            try:
                # Analizar imagen con OpenAI
                analysis_service = FoodAnalysisService()
                analysis, processed_data = analysis_service.analyze_and_save(food_image)
                
                # Actualizar comida con los resultados
                meal.image = food_image
                meal.total_calories = processed_data['total_calories']
                meal.save()
                
                # Registrar actividad
                ActivityLog.objects.create(
                    user=request.user,
                    action='analysis_requested',
                    details={
                        'meal_id': meal.id,
                        'analysis_id': analysis.id,
                        'calories_found': processed_data['total_calories']
                    }
                )
                
                messages.success(request, 'Análisis completado exitosamente')
                return redirect('core:meal_detail', meal_id=meal.id)
                
            except Exception as e:
                logger.error(f"Error en análisis de comida: {e}")
                messages.error(request, 'Error al analizar la imagen. Inténtalo de nuevo.')
                food_image.delete()
    
    return render(request, 'core/meal_analysis.html', {'meal': meal})


@login_required
def meal_detail(request, meal_id):
    """Vista para ver detalles de una comida"""
    meal = get_object_or_404(MealRecord, id=meal_id, user=request.user)
    
    # Obtener análisis si existe
    analysis = None
    if meal.image:
        analysis = getattr(meal.image, 'analysis', None)
    
    context = {
        'meal': meal,
        'analysis': analysis,
    }
    
    return render(request, 'core/meal_detail.html', context)


@login_required
def add_drink(request):
    """Vista para agregar una nueva bebida"""
    if request.method == 'POST':
        drink_id = request.POST.get('drink')
        quantity_ml = request.POST.get('quantity_ml')
        notes = request.POST.get('notes', '')
        
        try:
            drink = Drink.objects.get(id=drink_id)
            total_calories = (float(quantity_ml) * float(drink.calories_per_100ml)) / 100
            
            drink_record = DrinkRecord.objects.create(
                user=request.user,
                drink=drink,
                quantity_ml=quantity_ml,
                total_calories=total_calories,
                notes=notes
            )
            
            # Registrar actividad
            ActivityLog.objects.create(
                user=request.user,
                action='drink_added',
                details={
                    'drink_id': drink.id,
                    'quantity_ml': quantity_ml,
                    'calories': total_calories
                }
            )
            
            messages.success(request, 'Bebida registrada exitosamente')
            return redirect('core:dashboard')
            
        except (Drink.DoesNotExist, ValueError) as e:
            messages.error(request, 'Error al registrar la bebida')
            logger.error(f"Error registrando bebida: {e}")
    
    # Obtener todas las bebidas para el formulario
    drinks = Drink.objects.all().order_by('category__name', 'name')
    
    return render(request, 'core/add_drink.html', {'drinks': drinks})


@login_required
def meal_history(request):
    """Vista para ver historial de comidas"""
    # Filtros
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    meal_type = request.GET.get('meal_type')
    
    # Construir query
    meals = MealRecord.objects.filter(user=request.user)
    
    if date_from:
        meals = meals.filter(date__gte=date_from)
    if date_to:
        meals = meals.filter(date__lte=date_to)
    if meal_type:
        meals = meals.filter(meal_type=meal_type)
    
    # Ordenar y paginar
    meals = meals.order_by('-date', '-time')
    paginator = Paginator(meals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_calories = meals.aggregate(total=Sum('total_calories'))['total'] or 0
    total_meals = meals.count()
    
    context = {
        'meals': page_obj,
        'total_calories': total_calories,
        'total_meals': total_meals,
        'avg_calories': total_calories / total_meals if total_meals > 0 else 0,
        'days_count': meals.values('date').distinct().count(),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'meal_type': meal_type,
        }
    }
    
    return render(request, 'core/meal_history.html', context)


@login_required
def drink_history(request):
    """Vista para ver historial de bebidas"""
    # Filtros
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    drink_category = request.GET.get('drink_category')
    
    # Construir query
    drinks = DrinkRecord.objects.filter(user=request.user)
    
    if date_from:
        drinks = drinks.filter(date__gte=date_from)
    if date_to:
        drinks = drinks.filter(date__lte=date_to)
    if drink_category:
        drinks = drinks.filter(drink__category__name=drink_category)
    
    # Ordenar y paginar
    drinks = drinks.order_by('-date', '-time')
    paginator = Paginator(drinks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_calories = drinks.aggregate(total=Sum('total_calories'))['total'] or 0
    total_drinks = drinks.count()
    
    context = {
        'drinks': page_obj,
        'total_calories': total_calories,
        'total_drinks': total_drinks,
        'total_volume': drinks.aggregate(total=Sum('quantity_ml'))['total'] or 0,
        'avg_drink_calories': total_calories / total_drinks if total_drinks > 0 else 0,
        'days_count': drinks.values('date').distinct().count(),
        'drink_categories': DrinkCategory.objects.all(),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'drink_category': drink_category,
        }
    }
    
    return render(request, 'core/drink_history.html', context)


@login_required
def user_settings(request):
    """Vista para configuraciones del usuario"""
    user_settings, created = UserSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'daily_calorie_goal': 1000,
            'notifications_enabled': True,
            'ui_theme': 'light',
            'language': 'es'
        }
    )
    
    if request.method == 'POST':
        user_settings.daily_calorie_goal = int(request.POST.get('daily_calorie_goal', 1000))
        user_settings.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
        user_settings.ui_theme = request.POST.get('ui_theme', 'light')
        user_settings.language = request.POST.get('language', 'es')
        user_settings.save()
        
        # Actualizar también el perfil
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_profile.daily_calorie_goal = user_settings.daily_calorie_goal
        user_profile.save()
        
        # Registrar actividad
        ActivityLog.objects.create(
            user=request.user,
            action='settings_updated',
            details={'settings_updated': True}
        )
        
        messages.success(request, 'Configuración actualizada exitosamente')
        return redirect('core:user_settings')
    
    return render(request, 'core/user_settings.html', {'user_settings': user_settings})


@login_required
def statistics(request):
    """Vista para estadísticas detalladas"""
    # Período de análisis
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Obtener datos
    meals = MealRecord.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    drinks = DrinkRecord.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Calcular estadísticas
    total_meal_calories = meals.aggregate(total=Sum('total_calories'))['total'] or 0
    total_drink_calories = drinks.aggregate(total=Sum('total_calories'))['total'] or 0
    total_calories = total_meal_calories + total_drink_calories
    
    # Promedio diario
    avg_daily_calories = total_calories / days if days > 0 else 0
    
    # Comidas por tipo
    meals_by_type = meals.values('meal_type').annotate(
        count=Count('id'),
        total_calories=Sum('total_calories')
    )
    
    context = {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'total_calories': total_calories,
        'total_meal_calories': total_meal_calories,
        'total_drink_calories': total_drink_calories,
        'avg_daily_calories': round(avg_daily_calories, 2),
        'meals_by_type': meals_by_type,
        'total_meals': meals.count(),
        'total_drinks': drinks.count(),
    }
    
    return render(request, 'core/statistics.html', context)


# API Views para AJAX
@login_required
def quick_meal_capture(request):
    """Vista minimalista para captura rápida de comidas"""
    return render(request, 'core/quick_meal_capture.html')


@login_required
def quick_meal_summary(request, analysis_id):
    """Vista de resumen para análisis rápido de comidas"""
    try:
        analysis = get_object_or_404(OpenAIAnalysis, id=analysis_id, image__user=request.user)
        
        # Procesar datos del análisis para mostrar
        # Los datos están en response_received (JSON string) y identified_foods (JSON field)
        try:
            response_data = json.loads(analysis.response_received) if analysis.response_received else {}
        except:
            response_data = {}
        
        identified_foods = analysis.identified_foods if isinstance(analysis.identified_foods, list) else []
        
        # Formatear items para la vista
        items = []
        for food_data in identified_foods:
            # Calcular calorías por alimento
            grams = food_data.get('estimated_grams', 0)
            cal_per_100g = food_data.get('calories_per_100g', 0)
            calories = (grams * cal_per_100g) / 100 if grams and cal_per_100g else 0
            
            items.append({
                'name': food_data.get('name', 'Alimento desconocido'),
                'quantity': grams,
                'calories': int(calories),
                'confidence': int(food_data.get('confidence', 0.5) * 100)
            })
        
        context = {
            'analysis': analysis,
            'items': items,
            'total_calories': int(float(analysis.calculated_calories)),
            'analysis_confidence': int(float(analysis.confidence_score) * 100),
            'notes': response_data.get('notes', '')
        }
        
        return render(request, 'core/quick_meal_summary.html', context)
        
    except Exception as e:
        logger.error(f"Error en resumen rápido: {e}")
        messages.error(request, 'Error al cargar el análisis. Inténtalo de nuevo.')
        return redirect('core:quick_meal_capture')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_image(request):
    """API para analizar imagen con OpenAI"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No se proporcionó imagen'}, status=400)
        
        image_file = request.FILES['image']
        
        # Crear registro de imagen
        food_image = FoodImage.objects.create(
            user=request.user,
            image=image_file,
            original_name=image_file.name,
            file_size=image_file.size,
            mime_type=image_file.content_type
        )
        
        # Analizar imagen
        analysis_service = FoodAnalysisService()
        analysis, processed_data = analysis_service.analyze_and_save(food_image)
        
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'data': processed_data
        })
        
    except Exception as e:
        logger.error(f"Error en API de análisis: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_save_meal(request):
    """API para guardar comidas con análisis de IA"""
    try:
        data = json.loads(request.body)
        meal_type = data.get('meal_type')
        notes = data.get('notes', '')
        total_calories = data.get('total_calories', 0)
        items = data.get('items', [])
        custom_date = data.get('custom_date')
        custom_time = data.get('custom_time')
        analysis_id = data.get('analysis_id')
        
        # Validar datos
        if not meal_type:
            return JsonResponse({'success': False, 'error': 'Tipo de comida requerido'})
        
        if total_calories <= 0:
            return JsonResponse({'success': False, 'error': 'Calorías totales deben ser mayores a 0'})
        
        # Obtener la imagen si existe un análisis
        food_image = None
        if analysis_id:
            try:
                analysis = OpenAIAnalysis.objects.get(id=analysis_id, image__user=request.user)
                food_image = analysis.image
            except OpenAIAnalysis.DoesNotExist:
                pass  # Continuar sin imagen si no se encuentra el análisis
        
        # Procesar fecha y hora personalizadas
        from datetime import datetime
        if custom_date and custom_time:
            try:
                # Combinar fecha y hora
                date_time_str = f"{custom_date} {custom_time}"
                custom_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
                
                # Crear registro de comida con fecha personalizada
                meal = MealRecord.objects.create(
                    user=request.user,
                    meal_type=meal_type,
                    notes=notes,
                    total_calories=total_calories,
                    date=custom_datetime.date(),
                    time=custom_datetime.time(),
                    image=food_image
                )
            except ValueError as e:
                return JsonResponse({'success': False, 'error': f'Formato de fecha/hora inválido: {str(e)}'})
        else:
            # Crear registro de comida con fecha actual
            meal = MealRecord.objects.create(
                user=request.user,
                meal_type=meal_type,
                notes=notes,
                total_calories=total_calories,
                image=food_image
            )
        
        # Procesar items detectados y manuales
        for item in items:
            item_type = item.get('type')  # 'food' o 'drink'
            name = item.get('name')
            quantity = item.get('quantity', 0)
            unit = item.get('unit', 'g')
            calories = item.get('calories', 0)
            confidence = item.get('confidence', 1.0)
            
            if item_type == 'food':
                # Buscar o crear alimento
                food, created = Food.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': FoodCategory.objects.first(),  # Usar primera categoría por defecto
                        'calories_per_100g': calories * 100 / quantity if quantity > 0 else 0
                    }
                )
                
                # Crear detalle de comida
                MealDetail.objects.create(
                    meal_record=meal,
                    food=food,
                    quantity_g=quantity if unit == 'g' else quantity * 1.0,  # Campo correcto del modelo
                    calculated_calories=calories,
                    confidence=confidence
                )
            elif item_type == 'drink':
                # Buscar o crear bebida
                drink, created = Drink.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': DrinkCategory.objects.first(),  # Usar primera categoría por defecto
                        'calories_per_100ml': calories * 100 / quantity if quantity > 0 else 0
                    }
                )
                
                # Crear registro de bebida
                DrinkRecord.objects.create(
                    user=request.user,
                    drink=drink,
                    quantity_ml=quantity if unit == 'ml' else quantity * 1.0,  # Convertir si es necesario
                    total_calories=calories,
                    notes=f"Agregado desde análisis de comida: {meal.get_meal_type_display()}"
                )
        
        # Registrar actividad
        ActivityLog.objects.create(
            user=request.user,
            action='meal_added',
            details={
                'meal_id': meal.id,
                'meal_type': meal_type,
                'total_calories': total_calories,
                'items_count': len(items)
            }
        )
        
        messages.success(request, f'Comida guardada exitosamente con {total_calories} kcal')
        
        return JsonResponse({
            'success': True,
            'meal_id': meal.id,
            'message': f'Comida guardada con {total_calories} kcal'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'})
    except Exception as e:
        logger.error(f"Error guardando comida: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_image_enhanced(request):
    """API mejorada para análisis de imágenes con OpenAI"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'})
        
        image_file = request.FILES['image']
        
        # Crear registro de imagen
        food_image = FoodImage.objects.create(
            user=request.user,
            image=image_file,
            original_name=image_file.name,
            file_size=image_file.size,
            mime_type=image_file.content_type
        )
        
        # Analizar imagen con OpenAI
        analysis_service = FoodAnalysisService()
        analysis, processed_data = analysis_service.analyze_and_save(food_image)
        
        # Formatear resultados para la nueva interfaz
        items = []
        for food_data in processed_data.get('foods', []):
            items.append({
                'type': 'food',
                'name': food_data.get('name', 'Alimento desconocido'),
                'quantity': food_data.get('estimated_grams', 0),
                'unit': 'g',
                'calories': food_data.get('calories', 0),
                'confidence': food_data.get('confidence', 0.5)
            })
        
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'items': items,
            'total_calories': processed_data.get('total_calories', 0),
            'analysis_confidence': processed_data.get('analysis_confidence', 0.5)
        })
        
    except Exception as e:
        logger.error(f"Error en análisis de imagen: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_food_suggestions(request):
    """API para obtener sugerencias de alimentos"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'suggestions': []})
    
    foods = Food.objects.filter(name__icontains=query)[:10]
    suggestions = [
        {
            'id': food.id,
            'name': food.name,
            'category': food.category.name,
            'calories_per_100g': float(food.calories_per_100g)
        }
        for food in foods
    ]
    
    return JsonResponse({'suggestions': suggestions})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_quick_save_meal(request):
    """API para guardar comida desde análisis rápido"""
    try:
        analysis_id = request.POST.get('analysis_id')
        if not analysis_id:
            return JsonResponse({'success': False, 'error': 'ID de análisis requerido'})
        
        analysis = get_object_or_404(OpenAIAnalysis, id=analysis_id, image__user=request.user)
        
        # Obtener datos del análisis
        try:
            response_data = json.loads(analysis.response_received) if analysis.response_received else {}
        except:
            response_data = {}
        
        identified_foods = analysis.identified_foods if isinstance(analysis.identified_foods, list) else []
        
        # Crear registro de comida
        meal = MealRecord.objects.create(
            user=request.user,
            date=timezone.now().date(),
            meal_type='other',
            total_calories=analysis.calculated_calories,
            image=analysis.image,
            notes=f"Análisis rápido - {response_data.get('notes', '')}"
        )
        
        # Crear detalles de la comida
        for food_data in identified_foods:
            # Calcular calorías por alimento
            grams = food_data.get('estimated_grams', 0)
            cal_per_100g = food_data.get('calories_per_100g', 0)
            calories = (grams * cal_per_100g) / 100 if grams and cal_per_100g else 0
            food_name = food_data.get('name', 'Alimento desconocido')
            
            # Buscar o crear alimento
            food, created = Food.objects.get_or_create(
                name=food_name,
                defaults={
                    'category': FoodCategory.objects.first(),  # Usar primera categoría por defecto
                    'calories_per_100g': cal_per_100g if cal_per_100g > 0 else 100
                }
            )
            
            # Crear detalle de comida con los nombres de campo correctos
            MealDetail.objects.create(
                meal_record=meal,  # Nombre correcto del campo
                food=food,         # ForeignKey al objeto Food
                quantity_g=grams,  # Nombre correcto del campo
                calculated_calories=calories,  # Nombre correcto del campo
                confidence=food_data.get('confidence', 0.5)
            )
        
        # Registrar actividad
        ActivityLog.objects.create(
            user=request.user,
            action='quick_meal_saved',
            details={
                'meal_id': meal.id,
                'analysis_id': analysis.id,
                'total_calories': float(meal.total_calories)
            }
        )
        
        return JsonResponse({
            'success': True,
            'meal_id': meal.id,
            'message': 'Comida guardada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error guardando comida rápida: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
