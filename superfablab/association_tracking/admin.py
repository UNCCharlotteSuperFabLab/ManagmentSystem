from django.contrib import admin
from .models import AssociationEntities, Association

@admin.register(AssociationEntities)
class AssociationEntitiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_name', 'contact')
    search_fields = ('short_name', 'description')
    list_filter = ('contact',)

@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'user', 'entity')
    search_fields = ('email',)
    list_filter = ('entity', 'user')
