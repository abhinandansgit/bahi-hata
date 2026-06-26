from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg
from django.http import JsonResponse
from django.contrib import messages
from store.models import Book, Category, Mood, BookReview
from orders.models import Order, OrderItem
from vendors.models import Vendor
import json

@staff_member_required
def admin_dashboard(request):
    total_revenue = Order.objects.filter(status='Delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    total_books = Book.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_vendors = Vendor.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:8]
    
    # Category distribution for chart
    category_stats = Category.objects.annotate(book_count=Count('books')).values('name', 'book_count')
    
    # Monthly revenue (last 6 months approx)
    top_books = Book.objects.annotate(order_count=Count('orderitem')).order_by('-order_count')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_books': total_books,
        'pending_orders': pending_orders,
        'total_vendors': total_vendors,
        'recent_orders': recent_orders,
        'category_stats': list(category_stats),
        'top_books': top_books,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@staff_member_required
def manage_books(request):
    books = Book.objects.select_related('category', 'vendor').prefetch_related('moods').order_by('-created_at')
    
    # Search
    q = request.GET.get('q', '')
    cat_filter = request.GET.get('cat', '')
    vendor_filter = request.GET.get('vendor', '')

    if q:
        books = books.filter(title__icontains=q) | books.filter(author__icontains=q)
    if cat_filter:
        books = books.filter(category__id=cat_filter)
    if vendor_filter:
        books = books.filter(vendor__id=vendor_filter)
        
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    
    context = {
        'books': books,
        'categories': categories,
        'vendors': vendors,
        'q': q,
        'cat_filter': cat_filter,
        'vendor_filter': vendor_filter,
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
            
            cat_id = request.POST.get('category')
            if cat_id:
                book.category = get_object_or_404(Category, id=cat_id)
            
            # Handle cover image URL
            cover_image_url = request.POST.get('cover_image', '').strip()
            book.cover_image_url = cover_image_url
            
            # Handle moods (ManyToMany)
            mood_ids = request.POST.getlist('moods')
            book.moods.set(mood_ids)
            
            # Reset slug if title changed
            from django.utils.text import slugify
            new_slug = slugify(book.title)
            if new_slug != book.slug:
                # check uniqueness
                base_slug = new_slug
                counter = 1
                while Book.objects.filter(slug=new_slug).exclude(id=book.id).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                book.slug = new_slug
            
            book.save()
            messages.success(request, f'✅ "{book.title}" has been updated successfully.')
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
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'🗑️ "{title}" has been permanently deleted.')
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

@staff_member_required
def manage_orders(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/orders.html', context)

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('user').prefetch_related('items__book'), id=order_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            order.status = status
            order.save()
            messages.success(request, f'Order #BH-{order_id} status updated to {status}.')
            return redirect('admin_panel:admin_order_detail', order_id=order_id)
    
    context = {'order': order}
    return render(request, 'admin_panel/order_detail.html', context)

@staff_member_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        messages.success(request, f'Order #BH-{order_id} updated to {status}.')
    return redirect('admin_panel:manage_orders')

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
            image_url = request.POST.get('image', '').strip()
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
        
    context = {
        'categories': categories,
        'moods': moods,
    }
    return render(request, 'admin_panel/categories.html', context)

@staff_member_required
def manage_vendors(request):
    vendors = Vendor.objects.select_related('user').annotate(book_count=Count('books'))
    
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        action = request.POST.get('action')
        vendor = get_object_or_404(Vendor, id=vendor_id)
        if action == 'approve':
            vendor.is_approved = True
            vendor.save()
            messages.success(request, f'Vendor "{vendor.shop_name}" approved.')
        elif action == 'revoke':
            vendor.is_approved = False
            vendor.save()
            messages.warning(request, f'Vendor "{vendor.shop_name}" approval revoked.')
        return redirect('admin_panel:manage_vendors')
    
    context = {'vendors': vendors}
    return render(request, 'admin_panel/vendors.html', context)
