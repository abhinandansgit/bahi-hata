from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib import messages
from store.models import Book, Mood
from .models import SiteStat, ReaderStory

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
    reader_stories = ReaderStory.objects.filter(is_approved=True).order_by('-created_at')
    
    context = {
        'trending_books': trending_books,
        'heritage_picks': heritage_picks,
        'bestseller_books': bestseller_books,
        'popular_books': popular_books,
        'moods': moods,
        'site_stats': site_stats,
        'reader_stories': reader_stories,
    }
    return render(request, 'core/home.html', context)

def submit_story(request):
    """
    Handles visitor and customer reviews/stories submission on the homepage.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip() or 'Bhubaneswar, Odisha'
        rating = int(request.POST.get('rating', 5))
        review_text = request.POST.get('review_text', '').strip()

        if not name or not review_text:
            messages.error(request, 'Please provide your name and your reading experience.')
            return redirect('/#reader-stories')

        ReaderStory.objects.create(
            name=name,
            location=location,
            rating=min(max(rating, 1), 5),
            review_text=review_text,
            is_approved=True,
        )

        messages.success(request, '✦ Dhanyabad! Your story has been posted on Bahi Hata reader stories.')
        return redirect('/#reader-stories')

    return redirect('/#reader-stories')

def toggle_language(request):
    """
    Toggle between English and Odia.
    """
    current_lang = request.session.get('language', 'en')
    new_lang = 'or' if current_lang == 'en' else 'en'
    request.session['language'] = new_lang
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', '/'))

def privacy_policy(request):
    """
    Renders DPDP Act 2023 compliant Privacy Policy.
    """
    return render(request, 'legal/privacy_policy.html')

def terms_and_conditions(request):
    """
    Renders Terms & Conditions page.
    """
    return render(request, 'legal/terms.html')

def cookies_policy(request):
    """
    Renders Cookies & Local Storage Policy page.
    """
    return render(request, 'legal/cookies_policy.html')



