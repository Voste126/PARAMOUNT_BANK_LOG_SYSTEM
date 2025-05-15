from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_verified')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('is_verified',)
