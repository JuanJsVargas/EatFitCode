from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, MenuItem, Rating, MenuItemRating, Favorite
from .forms import RatingForm
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, StdDev, FloatField
from django.db.models.functions import Coalesce

# Create your views here.

def restaurant_list(request):
    query = request.GET.get('q', '')
    if query:
        restaurants = Restaurant.objects.filter(name__icontains=query)
    else:
        restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'query': query
    })

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.all().prefetch_related('ratings')
    ratings = restaurant.ratings.all()
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            # Check if user has already rated this restaurant
            existing_rating = Rating.objects.filter(restaurant=restaurant, user=request.user).first()
            if existing_rating:
                # Update existing rating
                existing_rating.rating = form.cleaned_data['rating']
                existing_rating.comment = form.cleaned_data['comment']
                existing_rating.save()
            else:
                # Create new rating
                rating = form.save(commit=False)
                rating.restaurant = restaurant
                rating.user = request.user
                rating.save()
            messages.success(request, 'Thank you for your rating!')
            return redirect('restaurants:restaurant_detail', pk=pk)
    else:
        form = RatingForm()
    
    # Calculate average rating
    average_rating = restaurant.ratings.aggregate(models.Avg('rating'))['rating__avg']

    # Get user's favorite menu item IDs
    favorite_menu_item_ids = []
    if request.user.is_authenticated:
        favorite_menu_item_ids = list(Favorite.objects.filter(user=request.user, menu_item__restaurant=restaurant).values_list('menu_item_id', flat=True))
    
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'ratings': ratings,
        'form': form,
        'average_rating': average_rating,
        'favorite_menu_item_ids': favorite_menu_item_ids,
    })

@login_required
def rate_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            # Check if user has already rated this restaurant
            existing_rating = Rating.objects.filter(restaurant=restaurant, user=request.user).first()
            if existing_rating:
                existing_rating.rating = rating
                existing_rating.comment = comment
                existing_rating.save()
            else:
                Rating.objects.create(
                    restaurant=restaurant,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def rate_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            # Check if user has already rated this menu item
            existing_rating = MenuItemRating.objects.filter(menu_item=menu_item, user=request.user).first()
            if existing_rating:
                existing_rating.rating = rating
                existing_rating.comment = comment
                existing_rating.save()
                rating_obj = existing_rating
            else:
                rating_obj = MenuItemRating.objects.create(
                    menu_item=menu_item,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
            
            return JsonResponse({
                'success': True,
                'rating': rating_obj.rating,
                'comment': rating_obj.comment,
                'created_at': rating_obj.created_at.strftime('%B %d, %Y'),
                'user': request.user.username
            })
    
    return JsonResponse({'success': False})

@login_required
def toggle_favorite(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, menu_item=menu_item)
    
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    return redirect('menu_item_detail', menu_item_id=menu_item_id)

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('menu_item', 'menu_item__restaurant')
    return render(request, 'restaurants/favorites_list.html', {
        'favorites': favorites
    })

def menu_item_detail(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, menu_item=menu_item).exists()
    
    return render(request, 'restaurants/menu_item_detail.html', {
        'menu_item': menu_item,
        'is_favorite': is_favorite
    })

def best_deals(request):
    # Get all menu items with their average rating
    menu_items = MenuItem.objects.all().annotate(
        avg_rating=Coalesce(Avg('ratings__rating', output_field=FloatField()), 0.0)
    )
    # Gather all ratings and prices for Z-score calculation
    ratings = [item.avg_rating for item in menu_items]
    prices = [float(item.price) for item in menu_items]
    if not ratings or not prices:
        return render(request, 'restaurants/best_deals.html', {'menu_items': []})
    mean_rating = sum(ratings) / len(ratings)
    std_rating = (sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)) ** 0.5 or 1
    mean_price = sum(prices) / len(prices)
    std_price = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5 or 1
    # Calculate ValueScore for each item
    items_with_score = []
    for item in menu_items:
        z_rating = (item.avg_rating - mean_rating) / std_rating
        z_price = (float(item.price) - mean_price) / std_price
        value_score = z_rating - z_price
        items_with_score.append((item, value_score, item.avg_rating, item.price))
    # Sort by ValueScore descending
    items_with_score.sort(key=lambda x: x[1], reverse=True)
    return render(request, 'restaurants/best_deals.html', {
        'items_with_score': items_with_score
    })
