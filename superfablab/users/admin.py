from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from .models import SpaceUser, Keyholder, KeyholderHistory

class SpaceUserAdmin(UserAdmin):
    model = SpaceUser
    list_display = ['niner_id', 'first_name', 'last_name', 'email', 'is_staff', 'user_picture']
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ['niner_id', 'email', 'first_name', 'last_name']
    ordering = ['first_name']
    
    fieldsets = (
        (None, {'fields': ('niner_id', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'canvas_id', 'user_picture')}),
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

class KeyholderAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_keyholder', 'priority')
    list_filter = ('is_keyholder', 'priority')
    search_fields = ('user__first_name', 'user__last_name', 'user__niner_id')
    raw_id_fields = ('user',)  # Use raw ID for ForeignKey to avoid heavy queries in large databases
    ordering = ('user',)

class KeyholderHistoryAdmin(admin.ModelAdmin):
    list_display = ('keyholder', 'start_time', 'exit_time')
    list_filter = ('start_time', 'exit_time')
    search_fields = ('keyholder__first_name', 'keyholder__last_name', 'keyholder__niner_id')
    raw_id_fields = ('keyholder',)
    ordering = ('-start_time',)  # Order by start_time descending for most recent keyholder history

admin.site.register(Keyholder, KeyholderAdmin)
admin.site.register(KeyholderHistory, KeyholderHistoryAdmin)
admin.site.register(SpaceUser, SpaceUserAdmin)
