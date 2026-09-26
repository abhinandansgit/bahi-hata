from django.urls import path
from . import views
from store import views as store_views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('cookies-policy/', views.cookies_policy, name='cookies_policy'),
    path('submit-story/', views.submit_story, name='submit_story'),
    path('magazine/', store_views.magazine_page, name='magazine'),
    path('toggle-language/', views.toggle_language, name='toggle_language'),
]


