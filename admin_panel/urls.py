from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('books/', views.manage_books, name='manage_books'),
    path('books/quick-update/', views.quick_update_book, name='quick_update_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('orders/', views.manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('vendors/', views.manage_vendors, name='manage_vendors'),
]
