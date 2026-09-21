from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('explore/', views.explore_hata, name='explore_hata'),
    path('combos/', views.combo_list, name='combos'),
    path('magazine/', views.magazine_page, name='magazine'),
    path('magazine/submit/', views.submit_writing, name='submit_writing'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('books/<slug:slug>/review/', views.submit_review, name='submit_review'),
]
