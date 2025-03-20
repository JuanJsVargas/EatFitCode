from django.shortcuts import render, get_object_or_404
from .models import Restaurant, MenuItem

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
    menu_items = restaurant.menu_items.all()
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items
    })
