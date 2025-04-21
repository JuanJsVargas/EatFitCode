from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=200)
    image = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    opening_hours = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='menu_items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=[
        ('appetizer', 'Appetizer'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
        ('other', 'Other')
    ])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    class Meta:
        ordering = ['category', 'name']

class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='restaurant_ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.rating} stars for {self.restaurant.name} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['restaurant', 'user']

class MenuItemRating(models.Model):
    menu_item = models.ForeignKey(MenuItem, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='menu_item_ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.rating} stars for {self.menu_item.name} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['menu_item', 'user']
