from django.shortcuts import render, redirect
from django.db.models import Count
from store.models import Book, Mood
from .models import SiteStat

def home(request):
    # Order trending books by sales count (Count of associated OrderItems)
    trending_books = Book.objects.filter(is_trending_in_odisha=True)\
        .annotate(order_count=Count('orderitem'))\
        .order_by('-order_count', '-created_at')[:8]
        
    heritage_picks = Book.objects.filter(is_odisha_heritage=True).order_by('?')[:8]
    bestseller_books = Book.objects.filter(is_bestseller=True).order_by('-created_at')[:8]
    popular_books = Book.objects.filter(is_popular=True).order_by('-created_at')[:8]
    moods = Mood.objects.all()
    site_stats = SiteStat.objects.all()
    
    context = {
        'trending_books': trending_books,
        'heritage_picks': heritage_picks,
        'bestseller_books': bestseller_books,
        'popular_books': popular_books,
        'moods': moods,
        'site_stats': site_stats,
    }
    return render(request, 'core/home.html', context)

def membership(request):
    return render(request, 'core/membership.html')

def toggle_language(request):
    """
    Toggle between English and Odia.
    """
    current_lang = request.session.get('language', 'en')
    new_lang = 'or' if current_lang == 'en' else 'en'
    request.session['language'] = new_lang
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', '/'))
