from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Category, Mood, BookReview, BookCombo, Offer


def book_list(request):
    books = Book.objects.select_related('category').all()
    categories = Category.objects.all()
    moods = Mood.objects.all()

    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    mood_slug = request.GET.get('mood', '').strip()
    is_heritage = request.GET.get('heritage', '').strip()
    language = request.GET.get('language', '').strip()

    if search_query:
        from django.db.models import Q
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    if category_slug:
        books = books.filter(category__slug=category_slug)
    if mood_slug:
        books = books.filter(moods__slug=mood_slug)
    if is_heritage == 'true':
        books = books.filter(is_odisha_heritage=True)
    if language:
        books = books.filter(language=language)

    books_list = books.distinct()
    suggested_books = None
    if not books_list.exists():
        suggested_books = Book.objects.select_related('category').filter(is_trending_in_odisha=True)[:4]
        if not suggested_books.exists():
            suggested_books = Book.objects.select_related('category').all()[:4]

    context = {
        'books': books_list,
        'suggested_books': suggested_books,
        'categories': categories,
        'moods': moods,
        'current_query': search_query,
        'current_category': category_slug,
        'current_mood': mood_slug,
        'current_heritage': is_heritage == 'true',
        'current_language': language,
        'total_count': books_list.count(),
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


def combo_list(request):
    """Storefront combos page — shows all active combos with savings info."""
    combos = BookCombo.objects.filter(is_active=True).prefetch_related('books')
    context = {'combos': combos}
    return render(request, 'store/combos.html', context)


def magazine_page(request):
    """
    Dedicated showcase page for Abhilasha Annual Magazine (Hindi / Odia).
    Features current and past editions, order options, and author writings submission block.
    """
    from .models import MagazineEdition, MagazineSubmission
    
    current_edition = MagazineEdition.objects.filter(is_active=True, is_current_edition=True).first()
    if not current_edition:
        current_edition = MagazineEdition.objects.filter(is_active=True).order_by('-edition_year').first()
        
    other_editions = MagazineEdition.objects.filter(is_active=True).exclude(
        pk=current_edition.pk if current_edition else None
    ).order_by('-edition_year')

    context = {
        'current_edition': current_edition,
        'other_editions': other_editions,
        'all_editions_count': MagazineEdition.objects.filter(is_active=True).count(),
        'editorial_email': 'theabhilasha14@gmail.com',
        'whatsapp_number': '6372202830',
    }
    return render(request, 'store/magazine.html', context)


def submit_writing(request):
    """
    Handles writer submissions for Abhilasha Annual Magazine (Hindi/Odia).
    """
    from django.contrib import messages
    from .models import MagazineSubmission
    
    if request.method == 'POST':
        author_name = request.POST.get('author_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        language = request.POST.get('language', 'OD').strip()
        genre = request.POST.get('genre', 'POETRY').strip()
        title_of_work = request.POST.get('title_of_work', '').strip()
        content_text = request.POST.get('content_text', '').strip()
        author_bio = request.POST.get('author_bio', '').strip()

        if not all([author_name, email, phone_number, title_of_work, content_text]):
            messages.error(request, 'Please complete all required fields (*).')
            return redirect('store:magazine')

        MagazineSubmission.objects.create(
            author_name=author_name,
            email=email,
            phone_number=phone_number,
            language=language,
            genre=genre,
            title_of_work=title_of_work,
            content_text=content_text,
            author_bio=author_bio,
            status='RECEIVED',
        )

        messages.success(
            request,
            '✦ Thank you! Your submission for Abhilasha Magazine has been successfully received by our editorial board. '
            'You may also email additional drafts or attachments to theabhilasha14@gmail.com.'
        )
        return redirect('/store/magazine/#submit-writings')

    return redirect('store:magazine')
