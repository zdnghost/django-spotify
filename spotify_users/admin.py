from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'full_name', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'full_name']
    list_filter = ['is_active', 'is_staff', 'date_joined']