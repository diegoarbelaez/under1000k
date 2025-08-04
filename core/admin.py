from django.contrib import admin
from .models import (
    UserProfile, FoodCategory, DrinkCategory, Food, Drink,
    FoodImage, OpenAIAnalysis, MealRecord, DrinkRecord,
    MealDetail, UserSettings, ActivityLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_calorie_goal', 'notifications_enabled', 'created_at']
    list_filter = ['notifications_enabled', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(DrinkCategory)
class DrinkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    list_select_related = ['category']


@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100ml', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category__name']
    list_select_related = ['category']


@admin.register(FoodImage)
class FoodImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_name', 'file_size', 'mime_type', 'created_at']
    list_filter = ['created_at', 'mime_type']
    search_fields = ['user__username', 'original_name']
    readonly_fields = ['file_size', 'mime_type']


@admin.register(OpenAIAnalysis)
class OpenAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['image', 'calculated_calories', 'confidence_score', 'created_at']
    list_filter = ['confidence_score', 'created_at']
    readonly_fields = ['prompt_sent', 'response_received', 'identified_foods']


@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time', 'meal_type', 'total_calories', 'created_at']
    list_filter = ['meal_type', 'date', 'created_at']
    search_fields = ['user__username', 'notes']
    list_select_related = ['user', 'image']
    date_hierarchy = 'date'


@admin.register(DrinkRecord)
class DrinkRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time', 'drink', 'quantity_ml', 'total_calories', 'created_at']
    list_filter = ['date', 'created_at', 'drink__category']
    search_fields = ['user__username', 'drink__name', 'notes']
    list_select_related = ['user', 'drink']
    date_hierarchy = 'date'


@admin.register(MealDetail)
class MealDetailAdmin(admin.ModelAdmin):
    list_display = ['meal_record', 'food', 'quantity_g', 'calculated_calories', 'created_at']
    list_filter = ['created_at', 'food__category']
    search_fields = ['food__name', 'meal_record__user__username']
    list_select_related = ['meal_record', 'food']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_calorie_goal', 'notifications_enabled', 'ui_theme', 'language', 'created_at']
    list_filter = ['notifications_enabled', 'ui_theme', 'language', 'created_at']
    search_fields = ['user__username']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'action']
    readonly_fields = ['ip_address', 'user_agent', 'details']
    date_hierarchy = 'created_at'
