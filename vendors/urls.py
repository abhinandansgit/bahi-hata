from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('add-book/', views.add_book, name='add_book'),
]
