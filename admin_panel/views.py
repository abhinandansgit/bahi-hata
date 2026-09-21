from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from store.models import Book, Category, Mood, BookReview, BookCombo, Offer, MagazineEdition, MagazineSubmission
from orders.models import Order, OrderItem
import json


# ─────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    total_revenue = Order.objects.filter(status='Delivered').aggregate(
        Sum('final_amount'))['final_amount__sum'] or 0
    total_orders = Order.objects.count()
    total_books = Book.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    low_stock_count = Book.objects.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock = Book.objects.filter(stock=0).count()
    active_offers = Offer.objects.filter(is_active=True, valid_until__gte=timezone.now()).count()
    active_combos = BookCombo.objects.filter(is_active=True).count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]
    category_stats = Category.objects.annotate(book_count=Count('books')).values('name', 'book_count')
    top_books = Book.objects.annotate(order_count=Count('orderitem')).order_by('-order_count')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_books': total_books,
        'pending_orders': pending_orders,
        'low_stock_count': low_stock_count,
        'out_of_stock': out_of_stock,
        'active_offers': active_offers,
        'active_combos': active_combos,
        'recent_orders': recent_orders,
        'category_stats': list(category_stats),
        'top_books': top_books,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ─────────────────────────────────────────────────
# BOOKS
# ─────────────────────────────────────────────────

@staff_member_required
def manage_books(request):
    books = Book.objects.select_related('category').prefetch_related('moods').order_by('-created_at')

    q = request.GET.get('q', '')
    cat_filter = request.GET.get('cat', '')
    stock_filter = request.GET.get('stock', '')

    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q))
    if cat_filter:
        books = books.filter(category__id=cat_filter)
    if stock_filter == 'low':
        books = books.filter(stock__lte=5, stock__gt=0)
    elif stock_filter == 'out':
        books = books.filter(stock=0)

    categories = Category.objects.all()

    context = {
        'books': books,
        'categories': categories,
        'q': q,
        'cat_filter': cat_filter,
        'stock_filter': stock_filter,
    }
    return render(request, 'admin_panel/books.html', context)


@staff_member_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    categories = Category.objects.all()
    moods = Mood.objects.all()
    reviews = book.reviews.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action', 'update_book')

        if action == 'update_book':
            book.title = request.POST.get('title', book.title).strip()
            book.author = request.POST.get('author', book.author).strip()
            book.description = request.POST.get('description', book.description).strip()
            book.price = request.POST.get('price', book.price)
            book.discount_percentage = request.POST.get('discount_percentage', book.discount_percentage)
            book.stock = request.POST.get('stock', book.stock)
            book.language = request.POST.get('language', book.language)
            book.is_trending_in_odisha = request.POST.get('is_trending_in_odisha') == 'on'
            book.is_odisha_heritage = request.POST.get('is_odisha_heritage') == 'on'
            book.is_bestseller = request.POST.get('is_bestseller') == 'on'
            book.is_popular = request.POST.get('is_popular') == 'on'

            # Product Images (up to 3, 500x500)
            cover_url = request.POST.get('cover_image', '').strip() or request.POST.get('cover_image_url', '').strip()
            if cover_url or 'cover_image' in request.POST:
                book.cover_image_url = cover_url

            img2_url = request.POST.get('image_2_url', '').strip()
            if img2_url or 'image_2_url' in request.POST:
                book.image_2_url = img2_url

            img3_url = request.POST.get('image_3_url', '').strip()
            if img3_url or 'image_3_url' in request.POST:
                book.image_3_url = img3_url

            cat_id = request.POST.get('category')
            if cat_id:
                book.category = get_object_or_404(Category, id=cat_id)

            mood_ids = request.POST.getlist('moods')
            book.moods.set(mood_ids)

            # Slug update if title changed
            from django.utils.text import slugify
            new_slug = slugify(book.title)
            if new_slug != book.slug:
                base_slug = new_slug
                counter = 1
                while Book.objects.filter(slug=new_slug).exclude(id=book.id).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                book.slug = new_slug

            book.save()
            messages.success(request, f'✅ "{book.title}" updated successfully.')
            return redirect('admin_panel:edit_book', book_id=book.id)

        elif action == 'delete_review':
            review_id = request.POST.get('review_id')
            review = get_object_or_404(BookReview, id=review_id, book=book)
            review.delete()
            messages.success(request, '🗑️ Review deleted.')
            return redirect('admin_panel:edit_book', book_id=book.id)

    context = {
        'book': book,
        'categories': categories,
        'moods': moods,
        'reviews': reviews,
        'selected_mood_ids': list(book.moods.values_list('id', flat=True)),
    }
    return render(request, 'admin_panel/edit_book.html', context)


@staff_member_required
def add_book(request):
    categories = Category.objects.all()
    moods = Mood.objects.all()

    if request.method == 'POST':
        from django.utils.text import slugify
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', 0)
        discount_percentage = request.POST.get('discount_percentage', 0)
        stock = request.POST.get('stock', 0)
        language = request.POST.get('language', 'EN')
        cover_image_url = request.POST.get('cover_image', '').strip() or request.POST.get('cover_image_url', '').strip()
        image_2_url = request.POST.get('image_2_url', '').strip()
        image_3_url = request.POST.get('image_3_url', '').strip()
        cat_id = request.POST.get('category')

        if not all([title, author, description, price, cat_id]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('admin_panel:add_book')

        category = get_object_or_404(Category, id=cat_id)
        book = Book.objects.create(
            title=title,
            author=author,
            description=description,
            price=price,
            discount_percentage=discount_percentage,
            stock=stock,
            language=language,
            cover_image_url=cover_image_url,
            image_2_url=image_2_url,
            image_3_url=image_3_url,
            category=category,
            is_trending_in_odisha=request.POST.get('is_trending_in_odisha') == 'on',
            is_odisha_heritage=request.POST.get('is_odisha_heritage') == 'on',
            is_bestseller=request.POST.get('is_bestseller') == 'on',
            is_popular=request.POST.get('is_popular') == 'on',
        )
        mood_ids = request.POST.getlist('moods')
        if mood_ids:
            book.moods.set(mood_ids)

        messages.success(request, f'📚 "{book.title}" added successfully!')
        return redirect('admin_panel:edit_book', book_id=book.id)

    context = {'categories': categories, 'moods': moods}
    return render(request, 'admin_panel/add_book.html', context)


@staff_member_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'🗑️ "{title}" permanently deleted.')
        return redirect('admin_panel:manage_books')
    return redirect('admin_panel:manage_books')


@staff_member_required
def quick_update_book(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book_id = data.get('id')
        price = data.get('price')
        stock = data.get('stock')

        book = get_object_or_404(Book, id=book_id)
        if price is not None:
            book.price = price
        if stock is not None:
            book.stock = stock
        book.save()
        return JsonResponse({'status': 'success', 'price': str(book.price), 'stock': book.stock})
    return JsonResponse({'status': 'error'}, status=400)


# ─────────────────────────────────────────────────
# INVENTORY MANAGEMENT
# ─────────────────────────────────────────────────

@staff_member_required
def inventory_management(request):
    """Bulk stock update page with low-stock alerts."""
    stock_filter = request.GET.get('filter', 'all')
    books = Book.objects.select_related('category').order_by('stock', 'title')

    if stock_filter == 'low':
        books = books.filter(stock__gt=0, stock__lte=5)
    elif stock_filter == 'out':
        books = books.filter(stock=0)
    elif stock_filter == 'ok':
        books = books.filter(stock__gt=5)

    total_books = Book.objects.count()
    low_stock = Book.objects.filter(stock__gt=0, stock__lte=5).count()
    out_of_stock = Book.objects.filter(stock=0).count()
    in_stock = Book.objects.filter(stock__gt=5).count()

    if request.method == 'POST':
        updated = 0
        for book in Book.objects.all():
            new_stock = request.POST.get(f'stock_{book.id}')
            if new_stock is not None and new_stock.strip().isdigit():
                new_val = int(new_stock)
                if new_val != book.stock:
                    book.stock = new_val
                    book.save(update_fields=['stock'])
                    updated += 1
        messages.success(request, f'✅ Inventory updated — {updated} book(s) changed.')
        return redirect('admin_panel:inventory')

    context = {
        'books': books,
        'total_books': total_books,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'in_stock': in_stock,
        'stock_filter': stock_filter,
    }
    return render(request, 'admin_panel/inventory.html', context)


# ─────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────

@staff_member_required
def manage_orders(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/orders.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user', 'coupon')
                     .prefetch_related('items__book', 'combo_items__combo'),
        id=order_id
    )

    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            order.status = status
            order.save(update_fields=['status'])
            messages.success(request, f'Order #BH-{order_id} status → {status}.')
            return redirect('admin_panel:admin_order_detail', order_id=order_id)

    context = {'order': order}
    return render(request, 'admin_panel/order_detail.html', context)


@staff_member_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save(update_fields=['status'])
        messages.success(request, f'Order #BH-{order_id} → {status}.')
    return redirect('admin_panel:manage_orders')


# ─────────────────────────────────────────────────
# CATEGORIES & MOODS
# ─────────────────────────────────────────────────

@staff_member_required
def manage_categories(request):
    categories = Category.objects.annotate(book_count=Count('books'))
    moods = Mood.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if action == 'add_category' and name:
            Category.objects.create(name=name, description=description)
            messages.success(request, f'Category "{name}" added.')
        elif action == 'add_mood' and name:
            image_url = request.POST.get('image_url', '').strip()
            Mood.objects.create(name=name, image_url=image_url)
            messages.success(request, f'Mood "{name}" added.')
        elif action == 'delete_category':
            cat_id = request.POST.get('cat_id')
            cat = get_object_or_404(Category, id=cat_id)
            cat.delete()
            messages.success(request, 'Category deleted.')
        elif action == 'delete_mood':
            mood_id = request.POST.get('mood_id')
            mood = get_object_or_404(Mood, id=mood_id)
            mood.delete()
            messages.success(request, 'Mood deleted.')
        return redirect('admin_panel:manage_categories')

    context = {'categories': categories, 'moods': moods}
    return render(request, 'admin_panel/categories.html', context)


# ─────────────────────────────────────────────────
# COMBOS
# ─────────────────────────────────────────────────

@staff_member_required
def manage_combos(request):
    combos = BookCombo.objects.prefetch_related('books').order_by('-created_at')
    books = Book.objects.all().order_by('title')
    context = {'combos': combos, 'books': books}
    return render(request, 'admin_panel/combos.html', context)


@staff_member_required
def create_combo(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        combo_price = request.POST.get('combo_price', '0').strip()
        cover_image_url = request.POST.get('cover_image_url', '').strip()
        book_ids = request.POST.getlist('books')
        is_active = request.POST.get('is_active') == 'on'

        if not name or not combo_price or len(book_ids) < 2:
            messages.error(request, 'Combo requires a name, price, and at least 2 books.')
            return redirect('admin_panel:manage_combos')

        combo = BookCombo.objects.create(
            name=name,
            description=description,
            combo_price=combo_price,
            cover_image_url=cover_image_url,
            is_active=is_active,
        )
        combo.books.set(book_ids)
        messages.success(request, f'🎁 Combo "{combo.name}" created!')
        return redirect('admin_panel:manage_combos')

    return redirect('admin_panel:manage_combos')


@staff_member_required
def edit_combo(request, combo_id):
    combo = get_object_or_404(BookCombo, id=combo_id)
    all_books = Book.objects.all().order_by('title')

    if request.method == 'POST':
        combo.name = request.POST.get('name', combo.name).strip()
        combo.description = request.POST.get('description', combo.description).strip()
        combo.combo_price = request.POST.get('combo_price', combo.combo_price)
        combo.cover_image_url = request.POST.get('cover_image_url', '').strip()
        combo.is_active = request.POST.get('is_active') == 'on'
        book_ids = request.POST.getlist('books')

        if len(book_ids) < 2:
            messages.error(request, 'A combo must include at least 2 books.')
            return redirect('admin_panel:edit_combo', combo_id=combo.id)

        combo.books.set(book_ids)
        combo.save()
        messages.success(request, f'🎁 Combo "{combo.name}" updated.')
        return redirect('admin_panel:manage_combos')

    context = {
        'combo': combo,
        'all_books': all_books,
        'selected_book_ids': list(combo.books.values_list('id', flat=True)),
    }
    return render(request, 'admin_panel/edit_combo.html', context)


@staff_member_required
def delete_combo(request, combo_id):
    combo = get_object_or_404(BookCombo, id=combo_id)
    if request.method == 'POST':
        name = combo.name
        combo.delete()
        messages.success(request, f'🗑️ Combo "{name}" deleted.')
    return redirect('admin_panel:manage_combos')


# ─────────────────────────────────────────────────
# OFFERS & COUPONS
# ─────────────────────────────────────────────────

@staff_member_required
def manage_offers(request):
    now = timezone.now()
    offers = Offer.objects.select_related('applies_to_category').order_by('-created_at')
    categories = Category.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_offer':
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            offer_type = request.POST.get('offer_type', 'PERCENTAGE')
            discount_value = request.POST.get('discount_value', 0)
            minimum_order_value = request.POST.get('minimum_order_value', 0)
            max_discount_cap = request.POST.get('max_discount_cap', '') or None
            valid_from = request.POST.get('valid_from')
            valid_until = request.POST.get('valid_until')
            usage_limit = request.POST.get('usage_limit', '') or None
            per_user_limit = request.POST.get('per_user_limit', 1)
            applies_to_combos_only = request.POST.get('applies_to_combos_only') == 'on'
            cat_id = request.POST.get('applies_to_category') or None
            is_active = request.POST.get('is_active') == 'on'

            if not name or not valid_from or not valid_until:
                messages.error(request, 'Name, valid-from and valid-until are required.')
                return redirect('admin_panel:manage_offers')

            category = get_object_or_404(Category, id=cat_id) if cat_id else None
            Offer.objects.create(
                name=name,
                code=code,
                offer_type=offer_type,
                discount_value=discount_value,
                minimum_order_value=minimum_order_value,
                max_discount_cap=max_discount_cap,
                valid_from=valid_from,
                valid_until=valid_until,
                usage_limit=usage_limit,
                per_user_limit=per_user_limit,
                applies_to_combos_only=applies_to_combos_only,
                applies_to_category=category,
                is_active=is_active,
            )
            messages.success(request, '🏷️ Offer created successfully.')
            return redirect('admin_panel:manage_offers')

        elif action == 'toggle_offer':
            offer_id = request.POST.get('offer_id')
            offer = get_object_or_404(Offer, id=offer_id)
            offer.is_active = not offer.is_active
            offer.save(update_fields=['is_active'])
            state = 'activated' if offer.is_active else 'deactivated'
            messages.success(request, f'Offer "{offer.name}" {state}.')
            return redirect('admin_panel:manage_offers')

        elif action == 'delete_offer':
            offer_id = request.POST.get('offer_id')
            offer = get_object_or_404(Offer, id=offer_id)
            offer.delete()
            messages.success(request, 'Offer deleted.')
            return redirect('admin_panel:manage_offers')

    context = {
        'offers': offers,
        'categories': categories,
        'now': now,
        'offer_types': Offer.OFFER_TYPE_CHOICES,
    }
    return render(request, 'admin_panel/offers.html', context)


@staff_member_required
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        offer.name = request.POST.get('name', offer.name).strip()
        offer.code = request.POST.get('code', offer.code).strip().upper()
        offer.offer_type = request.POST.get('offer_type', offer.offer_type)
        offer.discount_value = request.POST.get('discount_value', offer.discount_value)
        offer.minimum_order_value = request.POST.get('minimum_order_value', offer.minimum_order_value)
        offer.max_discount_cap = request.POST.get('max_discount_cap', '') or None
        offer.valid_from = request.POST.get('valid_from', offer.valid_from)
        offer.valid_until = request.POST.get('valid_until', offer.valid_until)
        offer.usage_limit = request.POST.get('usage_limit', '') or None
        offer.per_user_limit = request.POST.get('per_user_limit', offer.per_user_limit)
        offer.applies_to_combos_only = request.POST.get('applies_to_combos_only') == 'on'
        offer.is_active = request.POST.get('is_active') == 'on'
        cat_id = request.POST.get('applies_to_category') or None
        offer.applies_to_category = get_object_or_404(Category, id=cat_id) if cat_id else None
        offer.save()
        messages.success(request, f'Offer "{offer.name}" updated.')
        return redirect('admin_panel:manage_offers')

    context = {'offer': offer, 'categories': categories, 'offer_types': Offer.OFFER_TYPE_CHOICES}
    return render(request, 'admin_panel/edit_offer.html', context)


# ─────────────────────────────────────────────────
# ABHILASHA MAGAZINE MANAGEMENT
# ─────────────────────────────────────────────────

@staff_member_required
def manage_magazine(request):
    """
    Control center for Abhilasha Magazine:
    1. Manage Print Editions (stock, pricing, multi-image covers, flagship edition).
    2. Review & Process Writer Submissions (Hindi / Odia) with contact tools.
    """
    editions = MagazineEdition.objects.all().order_by('-edition_year', '-created_at')
    submissions = MagazineSubmission.objects.all().order_by('-submitted_at')

    # Submissions Filters
    sub_lang = request.GET.get('sub_lang', '')
    sub_status = request.GET.get('sub_status', '')
    active_tab = request.GET.get('tab', 'editions')

    if sub_lang:
        submissions = submissions.filter(language=sub_lang)
    if sub_status:
        submissions = submissions.filter(status=sub_status)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_edition':
            title = request.POST.get('title', '').strip()
            edition_year = request.POST.get('edition_year', '2026').strip()
            issue_number = request.POST.get('issue_number', 'Annual Edition').strip()
            language = request.POST.get('language', 'BI')
            price = request.POST.get('price', '199.00')
            discount_percentage = request.POST.get('discount_percentage', '0.00')
            stock = request.POST.get('stock', '50')
            cover_image_url = request.POST.get('cover_image_url', '').strip()
            image_2_url = request.POST.get('image_2_url', '').strip()
            image_3_url = request.POST.get('image_3_url', '').strip()
            total_pages = request.POST.get('total_pages', '128') or 128
            chief_editor = request.POST.get('chief_editor', 'Abhilasha Editorial Board').strip()
            description = request.POST.get('description', '').strip()
            is_current = request.POST.get('is_current_edition') == 'on'
            is_active = request.POST.get('is_active') == 'on'

            if not title or not price:
                messages.error(request, 'Please provide Title and Price for the edition.')
                return redirect('admin_panel:manage_magazine')

            edition = MagazineEdition.objects.create(
                title=title,
                edition_year=edition_year,
                issue_number=issue_number,
                language=language,
                price=price,
                discount_percentage=discount_percentage or 0,
                stock=stock or 0,
                cover_image_url=cover_image_url or None,
                image_2_url=image_2_url or None,
                image_3_url=image_3_url or None,
                total_pages=total_pages,
                chief_editor=chief_editor,
                description=description,
                is_current_edition=is_current,
                is_active=is_active,
            )
            messages.success(request, f'Magazine edition "{edition.title}" added successfully.')
            return redirect('admin_panel:manage_magazine')

    # Aggregates
    total_copies_in_stock = editions.aggregate(Sum('stock'))['stock__sum'] or 0
    total_submissions_count = MagazineSubmission.objects.count()
    pending_review_count = MagazineSubmission.objects.filter(status='RECEIVED').count()
    selected_count = MagazineSubmission.objects.filter(status='SELECTED').count()

    context = {
        'editions': editions,
        'submissions': submissions,
        'sub_lang': sub_lang,
        'sub_status': sub_status,
        'active_tab': active_tab,
        'total_copies_in_stock': total_copies_in_stock,
        'total_submissions_count': total_submissions_count,
        'pending_review_count': pending_review_count,
        'selected_count': selected_count,
        'language_choices': MagazineEdition.LANGUAGE_CHOICES,
        'submission_language_choices': MagazineSubmission.LANGUAGE_CHOICES,
        'submission_status_choices': MagazineSubmission.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/magazine.html', context)


@staff_member_required
def edit_magazine_edition(request, edition_id):
    edition = get_object_or_404(MagazineEdition, id=edition_id)

    if request.method == 'POST':
        edition.title = request.POST.get('title', edition.title).strip()
        edition.edition_year = request.POST.get('edition_year', edition.edition_year).strip()
        edition.issue_number = request.POST.get('issue_number', edition.issue_number).strip()
        edition.language = request.POST.get('language', edition.language)
        edition.price = request.POST.get('price', edition.price)
        edition.discount_percentage = request.POST.get('discount_percentage', edition.discount_percentage) or 0
        edition.stock = request.POST.get('stock', edition.stock) or 0
        edition.cover_image_url = request.POST.get('cover_image_url', '').strip() or None
        edition.image_2_url = request.POST.get('image_2_url', '').strip() or None
        edition.image_3_url = request.POST.get('image_3_url', '').strip() or None
        edition.total_pages = request.POST.get('total_pages', edition.total_pages) or None
        edition.chief_editor = request.POST.get('chief_editor', edition.chief_editor).strip()
        edition.description = request.POST.get('description', edition.description).strip()
        edition.is_current_edition = request.POST.get('is_current_edition') == 'on'
        edition.is_active = request.POST.get('is_active') == 'on'
        edition.save()

        messages.success(request, f'Magazine edition "{edition.title}" updated.')
        return redirect('admin_panel:manage_magazine')

    context = {
        'edition': edition,
        'language_choices': MagazineEdition.LANGUAGE_CHOICES,
    }
    return render(request, 'admin_panel/edit_magazine.html', context)


@staff_member_required
def delete_magazine_edition(request, edition_id):
    edition = get_object_or_404(MagazineEdition, id=edition_id)
    title = edition.title
    edition.delete()
    messages.success(request, f'🗑️ Magazine edition "{title}" was deleted.')
    return redirect('admin_panel:manage_magazine')


@staff_member_required
def delete_magazine_submission(request, submission_id):
    submission = get_object_or_404(MagazineSubmission, id=submission_id)
    title = submission.title_of_work
    author = submission.author_name
    submission.delete()
    messages.success(request, f'🗑️ Submission "{title}" by {author} was deleted.')
    return redirect('/admin-portal/magazine/?tab=submissions')


@staff_member_required
def quick_update_magazine(request):
    """AJAX endpoint to update stock or price for magazine editions."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            edition_id = data.get('edition_id')
            field = data.get('field')
            val = data.get('value')

            edition = get_object_or_404(MagazineEdition, id=edition_id)
            if field == 'stock':
                edition.stock = max(0, int(val))
                edition.save(update_fields=['stock'])
                return JsonResponse({'status': 'ok', 'new_value': edition.stock, 'in_stock': edition.in_stock})
            elif field == 'price':
                edition.price = max(0, float(val))
                edition.save(update_fields=['price'])
                return JsonResponse({'status': 'ok', 'new_value': str(edition.final_price)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@staff_member_required
def update_submission_status(request, submission_id):
    """Update status and editorial notes for a writer submission."""
    submission = get_object_or_404(MagazineSubmission, id=submission_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')

        if new_status:
            submission.status = new_status
        submission.admin_notes = admin_notes
        submission.save()

        messages.success(request, f'Updated review status for "{submission.title_of_work}" by {submission.author_name}.')
    return redirect('/admin-portal/magazine/?tab=submissions')


@staff_member_required
def upload_image_view(request):
    """
    Handles image uploads directly to Supabase Storage.
    Converts uploaded image to optimized WebP format with low byte-size for fast edge loading.
    """
    if request.method == 'POST':
        image_file = request.FILES.get('image') or request.FILES.get('file')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image file provided.'}, status=400)
        
        folder = request.POST.get('folder', 'books').strip()
        prefix = request.POST.get('prefix', 'item').strip()
        
        from core.supabase_storage import upload_to_supabase
        result = upload_to_supabase(image_file, folder=folder, filename_prefix=prefix)
        
        if result.get('success'):
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=500)
            
    return JsonResponse({'success': False, 'error': 'POST method required.'}, status=405)


