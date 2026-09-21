from django.urls import path
from . import views
from store import views as store_views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-story/', views.submit_story, name='submit_story'),
    path('magazine/', store_views.magazine_page, name='magazine'),
    path('toggle-language/', views.toggle_language, name='toggle_language'),
]

