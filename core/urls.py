from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('membership/', views.membership, name='membership'),
    path('toggle-language/', views.toggle_language, name='toggle_language'),
]
