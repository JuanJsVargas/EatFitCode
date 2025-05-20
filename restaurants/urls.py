from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('rate/<int:restaurant_id>/', views.rate_restaurant, name='rate_restaurant'),
    path('menu-item/<int:menu_item_id>/rate/', views.rate_menu_item, name='rate_menu_item'),
    path('menu-item/<int:menu_item_id>/', views.menu_item_detail, name='menu_item_detail'),
    path('menu-item/<int:menu_item_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('best-deals/', views.best_deals, name='best_deals'),
] 