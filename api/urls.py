from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('home/', views.home_data, name='home_data'),
    path('books/', views.book_list, name='book_list'),
    path('books/filters/', views.book_filters, name='book_filters'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('books/<slug:slug>/review/', views.submit_review, name='submit_review'),
    path('books/wishlist/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('auth/status/', views.auth_status, name='auth_status'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/update/', views.profile_update, name='profile_update'),
    path('auth/password/change/', views.change_password, name='change_password'),
]