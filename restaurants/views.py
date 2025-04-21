from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant, MenuItem, Rating, MenuItemRating
from .forms import RatingForm
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
    
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'ratings': ratings,
        'form': form,
        'average_rating': average_rating,
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
