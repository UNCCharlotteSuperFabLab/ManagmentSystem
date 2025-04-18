from django.contrib import admin

# Register your models here.
from .models import TrainingCategory, Training

@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'canvas_id', 'user_url')  
    search_fields = ('name',)

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('user', 'category__name', 'training_level', 'completed_on')
    list_filter = ('training_level', 'completed_on')  
    search_fields = ('user__first_name', 'user__last_name', 'category__name')  
