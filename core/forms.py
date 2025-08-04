from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MealRecord, DrinkRecord, UserSettings, FoodImage


class UserRegistrationForm(UserCreationForm):
    """Formulario de registro de usuario"""
    email = forms.EmailField(required=True)
    daily_calorie_goal = forms.IntegerField(
        min_value=500,
        max_value=5000,
        initial=1000,
        help_text="Objetivo de calorías diarias"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'daily_calorie_goal')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Crear perfil de usuario
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                daily_calorie_goal=self.cleaned_data['daily_calorie_goal']
            )
        return user


class MealRecordForm(forms.ModelForm):
    """Formulario para registrar comidas"""
    meal_type = forms.ChoiceField(
        choices=MealRecord.MEAL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = MealRecord
        fields = ['meal_type', 'notes']


class DrinkRecordForm(forms.ModelForm):
    """Formulario para registrar bebidas"""
    drink = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecciona una bebida"
    )
    quantity_ml = forms.IntegerField(
        min_value=1,
        max_value=5000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad en ml'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = DrinkRecord
        fields = ['drink', 'quantity_ml', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Drink
        self.fields['drink'].queryset = Drink.objects.all().order_by('category__name', 'name')


class FoodImageUploadForm(forms.ModelForm):
    """Formulario para subir imágenes de comida"""
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'food-image-input'
        }),
        help_text="Sube una foto de tu comida (JPEG, PNG, WEBP)"
    )
    
    class Meta:
        model = FoodImage
        fields = ['image']
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validar tamaño (máximo 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede ser mayor a 10MB")
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                raise forms.ValidationError("Solo se permiten imágenes JPEG, PNG o WEBP")
        
        return image


class UserSettingsForm(forms.ModelForm):
    """Formulario para configuraciones de usuario"""
    daily_calorie_goal = forms.IntegerField(
        min_value=500,
        max_value=5000,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    notifications_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    ui_theme = forms.ChoiceField(
        choices=UserSettings._meta.get_field('ui_theme').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    language = forms.ChoiceField(
        choices=UserSettings._meta.get_field('language').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserSettings
        fields = ['daily_calorie_goal', 'notifications_enabled', 'ui_theme', 'language']


class MealHistoryFilterForm(forms.Form):
    """Formulario para filtrar historial de comidas"""
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    meal_type = forms.ChoiceField(
        choices=[('', 'Todos')] + MealRecord.MEAL_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class DrinkHistoryFilterForm(forms.Form):
    """Formulario para filtrar historial de bebidas"""
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    drink_category = forms.ChoiceField(
        choices=[('', 'Todas')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import DrinkCategory
        categories = DrinkCategory.objects.all()
        self.fields['drink_category'].choices = [('', 'Todas')] + [
            (cat.name, cat.name) for cat in categories
        ] 