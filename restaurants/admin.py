from django.contrib import admin
from .models import Restaurant, MenuItem, Rating

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

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('restaurant__name', 'comment')
    ordering = ('-created_at',)
