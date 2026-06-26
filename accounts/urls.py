from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('wishlist/toggle/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('change-password/', views.change_password, name='change_password'),
]
