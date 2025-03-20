from django.contrib import admin
from .models import Restaurant, MenuItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email')
    search_fields = ('name', 'location', 'description')
    list_filter = ('location',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available', 'restaurant')
    search_fields = ('name', 'description', 'restaurant__name')
    ordering = ('restaurant', 'category', 'name')
