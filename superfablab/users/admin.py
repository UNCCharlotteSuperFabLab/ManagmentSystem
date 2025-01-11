from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from .models import SpaceUser

class SpaceUserAdmin(UserAdmin):
    model = SpaceUser
    list_display = ['niner_id', 'first_name', 'last_name', 'email', 'is_staff']
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ['niner_id', 'email', 'first_name', 'last_name']
    ordering = ['first_name']
    
    fieldsets = (
        (None, {'fields': ('niner_id', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'canvas_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('niner_id', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    # Remove unnecessary fields from filter_horizontal
    filter_horizontal = []
    list_filter = ['is_staff', 'is_active']


admin.site.register(SpaceUser, SpaceUserAdmin)
