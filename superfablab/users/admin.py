from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from .models import SpaceUser

class SpaceUserAdmin(UserAdmin):
    model = SpaceUser
    list_display = ['niner_id', 'first_name', 'last_name', 'email', 'is_staff']
    search_fields = ['niner_id', 'email', 'first_name', 'last_name']
    ordering = ['first_name']
    
        # Remove the default fields that are looking for 'username' and 'date_joined'
    fieldsets = (
        (None, {'fields': ('niner_id', 'first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('niner_id', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    # Remove unnecessary fields from filter_horizontal
    filter_horizontal = []
    list_filter = ['is_staff', 'is_active']


admin.site.register(SpaceUser, SpaceUserAdmin)
