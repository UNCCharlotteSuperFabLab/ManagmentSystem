from django.contrib import admin

from .models import Visit

class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'enter_time', 'exit_time', 'description', 'forgot_to_signout')  # Replace with actual field names
    search_fields = ('user',)           # Fields to enable search
    list_filter = ('still_in_the_space','forgot_to_signout')                      # Fields to filter by

# Register your models here.
admin.site.register(Visit, VisitAdmin)