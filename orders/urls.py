from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add-combo/<int:combo_id>/', views.add_combo_to_cart, name='add_combo_to_cart'),
    path('cart/add-magazine/<int:edition_id>/', views.add_magazine_to_cart, name='add_magazine_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/update-magazine/<int:item_id>/', views.update_magazine_cart_item, name='update_magazine_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/remove-combo/<int:item_id>/', views.remove_combo_from_cart, name='remove_combo_from_cart'),
    path('cart/remove-magazine/<int:item_id>/', views.remove_magazine_from_cart, name='remove_magazine_from_cart'),
    path('cart/coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/cart-count/', views.cart_count_api, name='cart_count_api'),
    path('api/cart-data/', views.cart_data_api, name='cart_data_api'),
]
