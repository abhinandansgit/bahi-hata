from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),

    # Books
    path('books/', views.manage_books, name='manage_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/quick-update/', views.quick_update_book, name='quick_update_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),

    # Inventory
    path('inventory/', views.inventory_management, name='inventory'),

    # Orders
    path('orders/', views.manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),

    # Categories & Moods
    path('categories/', views.manage_categories, name='manage_categories'),

    # Combos
    path('combos/', views.manage_combos, name='manage_combos'),
    path('combos/create/', views.create_combo, name='create_combo'),
    path('combos/<int:combo_id>/edit/', views.edit_combo, name='edit_combo'),
    path('combos/<int:combo_id>/delete/', views.delete_combo, name='delete_combo'),

    # Offers & Coupons
    path('offers/', views.manage_offers, name='manage_offers'),
    path('offers/<int:offer_id>/edit/', views.edit_offer, name='edit_offer'),

    # Abhilasha Magazine
    path('magazine/', views.manage_magazine, name='manage_magazine'),
    path('magazine/<int:edition_id>/edit/', views.edit_magazine_edition, name='edit_magazine_edition'),
    path('magazine/<int:edition_id>/delete/', views.delete_magazine_edition, name='delete_magazine_edition'),
    path('magazine/quick-update/', views.quick_update_magazine, name='quick_update_magazine'),
    path('magazine/submissions/<int:submission_id>/update/', views.update_submission_status, name='update_submission_status'),
    path('magazine/submissions/<int:submission_id>/delete/', views.delete_magazine_submission, name='delete_magazine_submission'),

    # Image Upload to Supabase Storage
    path('upload-image/', views.upload_image_view, name='upload_image'),
]

