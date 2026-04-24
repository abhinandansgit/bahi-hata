from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor
from store.models import Book, Category

@login_required(login_url='accounts:login')
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('home') # Not a vendor
        
    books = vendor.books.all()
    
    context = {
        'vendor': vendor,
        'books': books
    }
    return render(request, 'vendors/dashboard.html', context)

@login_required(login_url='accounts:login')
def add_book(request):
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        
        category = get_object_or_404(Category, id=category_id)
        cover_image = request.FILES.get('cover_image')
        
        book = Book.objects.create(
            vendor=vendor,
            title=title,
            author=author,
            description=description,
            price=price,
            stock=stock,
            category=category,
            language='EN',
            cover_image=cover_image
        )
        return redirect('vendors:dashboard')
        
    categories = Category.objects.all()
    return render(request, 'vendors/add_book.html', {'categories': categories})
