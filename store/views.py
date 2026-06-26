from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Category, Mood, BookReview


def book_list(request):
    books = Book.objects.select_related('category').all()
    categories = Category.objects.all()
    moods = Mood.objects.all()

    search_query = request.GET.get('q')
    category_slug = request.GET.get('category')
    mood_slug = request.GET.get('mood')
    is_heritage = request.GET.get('heritage')
    language = request.GET.get('language')

    if search_query:
        from django.db.models import Q
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if category_slug:
        books = books.filter(category__slug=category_slug)
    if mood_slug:
        books = books.filter(moods__slug=mood_slug)
    if is_heritage == 'true':
        books = books.filter(is_odisha_heritage=True)
    if language:
        books = books.filter(language=language)

    context = {
        'books': books.distinct(),
        'categories': categories,
        'moods': moods,
        'current_query': search_query or '',
        'current_category': category_slug or '',
        'current_mood': mood_slug or '',
    }
    return render(request, 'store/book_list.html', context)


def explore_hata(request):
    sort = request.GET.get('sort', 'newest')
    category_slug = request.GET.get('category')
    
    books = Book.objects.select_related('category').all()
    
    if category_slug:
        books = books.filter(category__slug=category_slug)
    
    if sort == 'price_low':
        books = books.order_by('price')
    elif sort == 'price_high':
        books = books.order_by('-price')
    elif sort == 'popular':
        books = books.order_by('-is_trending_in_odisha', '-created_at')
    else:
        books = books.order_by('-created_at')
        
    categories = Category.objects.all()
    moods = Mood.objects.all()
    
    # Group books by category for the "Flipkart" sections feel
    categorized_books = []
    for cat in categories:
        cat_books = books.filter(category=cat)[:10]
        if cat_books.exists():
            categorized_books.append({
                'category': cat,
                'books': cat_books
            })

    context = {
        'categorized_books': categorized_books,
        'categories': categories,
        'moods': moods,
        'current_sort': sort,
        'current_category': category_slug,
    }
    return render(request, 'store/explore.html', context)


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    related_books = Book.objects.filter(category=book.category).exclude(id=book.id)[:4]
    reviews = book.reviews.select_related('user').all().order_by('-created_at')

    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()

    context = {
        'book': book,
        'related_books': related_books,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'store/book_detail.html', context)


@login_required(login_url='accounts:login')
def submit_review(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if BookReview.objects.filter(book=book, user=request.user).exists():
        return redirect('store:book_detail', slug=slug)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')

        BookReview.objects.create(
            book=book,
            user=request.user,
            rating=min(max(rating, 1), 5),
            comment=comment
        )

    return redirect('store:book_detail', slug=slug)
