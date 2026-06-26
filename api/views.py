import json
import urllib.parse
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import update_last_login
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from store.models import Book, Category, Mood, BookReview
from core.models import SiteStat
from orders.models import Cart, CartItem, Order, OrderItem
from accounts.models import User, Wishlist
from vendors.models import Vendor

def serialize_book(book):
    return {
        'id': book.id,
        'title': book.title,
        'slug': book.slug,
        'author': book.author,
        'price': float(book.price),
        'discount_price': float(book.discount_price) if book.discount_price else None,
        'final_price': float(book.final_price),
        'cover_image': book.cover_image.url if book.cover_image else None,
        'category': book.category.name if book.category else None,
        'is_trending_in_odisha': book.is_trending_in_odisha,
        'is_odisha_heritage': book.is_odisha_heritage,
        'is_bestseller': book.is_bestseller,
        'is_popular': book.is_popular,
        'created_at': book.created_at.strftime('%Y-%m-%d') if book.created_at else None,
    }

def home_data(request):
    trending = Book.objects.select_related('category').filter(is_trending_in_odisha=True).annotate(order_count=Count('orderitem')).order_by('-order_count', '-created_at')[:8]
    heritage = Book.objects.select_related('category').filter(is_odisha_heritage=True).order_by('?')[:8]
    bestseller = Book.objects.select_related('category').filter(is_bestseller=True).order_by('-created_at')[:8]
    popular = Book.objects.select_related('category').filter(is_popular=True).order_by('-created_at')[:8]
    
    moods = [{'id': m.id, 'name': m.name, 'slug': m.slug, 'image': m.image.url if m.image else None} for m in Mood.objects.all()]
    stats = [{'id': s.id, 'label': s.label, 'value': s.value, 'icon': s.icon} for s in SiteStat.objects.all()]
    
    return JsonResponse({
        'trending_books': [serialize_book(b) for b in trending],
        'heritage_picks': [serialize_book(b) for b in heritage],
        'bestseller_books': [serialize_book(b) for b in bestseller],
        'popular_books': [serialize_book(b) for b in popular],
        'moods': moods,
        'site_stats': stats,
    })

def book_list(request):
    books = Book.objects.select_related('category').all()
    
    category_slug = request.GET.get('category')
    q = request.GET.get('q')
    mood_slug = request.GET.get('mood')
    heritage = request.GET.get('heritage')
    language = request.GET.get('language')
    sort = request.GET.get('sort')
    
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(description__icontains=q))
    if category_slug:
        books = books.filter(category__slug=category_slug)
    if mood_slug:
        books = books.filter(moods__slug=mood_slug)
    if heritage == 'true':
        books = books.filter(is_odisha_heritage=True)
    if language:
        books = books.filter(language=language)
        
    if sort == 'price_low':
        books = books.order_by('price')
    elif sort == 'price_high':
        books = books.order_by('-price')
    elif sort == 'popular':
        books = books.order_by('-is_trending_in_odisha')
    elif sort == 'newest':
        books = books.order_by('-created_at')
        
    books = books.distinct()
    
    return JsonResponse({
        'books': [serialize_book(b) for b in books]
    })

def book_filters(request):
    categories = [{'name': c.name, 'slug': c.slug} for c in Category.objects.all()]
    moods = [{'name': m.name, 'slug': m.slug} for m in Mood.objects.all()]
    return JsonResponse({
        'categories': categories,
        'moods': moods,
    })

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    related_books = Book.objects.filter(category=book.category).exclude(id=book.id)[:4]
    
    reviews = BookReview.objects.filter(book=book).select_related('user').order_by('-created_at')
    
    user_has_reviewed = False
    is_wishlisted = False
    
    if request.user.is_authenticated:
        user_has_reviewed = BookReview.objects.filter(book=book, user=request.user).exists()
        is_wishlisted = Wishlist.objects.filter(user=request.user, book=book).exists()
        
    serialized_reviews = []
    for r in reviews:
        serialized_reviews.append({
            'id': r.id,
            'user': r.user.username,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.strftime('%Y-%m-%d') if r.created_at else None,
        })
        
    return JsonResponse({
        'book': {
            'id': book.id,
            'title': book.title,
            'slug': book.slug,
            'author': book.author,
            'description': book.description,
            'price': float(book.price),
            'discount_price': float(book.discount_price) if book.discount_price else None,
            'final_price': float(book.final_price),
            'cover_image': book.cover_image.url if book.cover_image else None,
            'category': book.category.name if book.category else None,
            'stock': book.stock,
            'language': book.language,
            'publisher': book.publisher,
            'published_date': book.published_date.strftime('%Y-%m-%d') if book.published_date else None,
            'isbn': book.isbn,
            'pages': book.pages,
        },
        'related_books': [serialize_book(b) for b in related_books],
        'reviews': serialized_reviews,
        'user_has_reviewed': user_has_reviewed,
        'is_wishlisted': is_wishlisted,
    })

@csrf_exempt
def submit_review(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    book = get_object_or_404(Book, slug=slug)
    
    if BookReview.objects.filter(book=book, user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'You have already reviewed this book'}, status=400)
        
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            rating = int(body.get('rating', 5))
            rating = max(1, min(5, rating))
            comment = body.get('comment', '')
            
            review = BookReview.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                comment=comment
            )
            
            return JsonResponse({
                'status': 'success',
                'review': {
                    'id': review.id,
                    'user': review.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.strftime('%Y-%m-%d') if review.created_at else None,
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

@csrf_exempt
def toggle_wishlist(request, book_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    book = get_object_or_404(Book, id=book_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    
    added = True
    if not created:
        wishlist_item.delete()
        added = False
        
    return JsonResponse({
        'added': added,
        'book_title': book.title
    })

def view_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book', 'book__category').all()
    
    serialized_items = []
    total = 0.0
    for item in items:
        subtotal = float(item.book.final_price) * item.quantity
        total += subtotal
        serialized_items.append({
            'id': item.id,
            'book': serialize_book(item.book),
            'quantity': item.quantity,
            'subtotal': round(subtotal, 2)
        })
        
    return JsonResponse({
        'items': serialized_items,
        'total': round(total, 2),
        'cart_count': sum(item.quantity for item in items)
    })

@csrf_exempt
def add_to_cart(request, book_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    return JsonResponse({
        'status': 'success',
        'message': f'"{book.title}" added to cart'
    })

@csrf_exempt
def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        body = json.loads(request.body)
        action = body.get('action', '')
        
        if action == 'increase':
            item.quantity += 1
            item.save()
            return JsonResponse({'status': 'success', 'quantity': item.quantity})
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                return JsonResponse({'status': 'success', 'quantity': item.quantity})
            else:
                item.delete()
                return JsonResponse({'status': 'success', 'deleted': True})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return JsonResponse({'status': 'success'})

@csrf_exempt
def checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            items = cart.items.select_related('book').all()
            
            if not items.exists():
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)
                
            body = json.loads(request.body)
            full_name = body.get('full_name', '')
            phone = body.get('phone', '')
            address = body.get('address', '')
            city = body.get('city', '')
            pincode = body.get('pincode', '')
            
            shipping_address = f"{full_name}\nPhone: {phone}\n{address}\n{city} - {pincode}"
            
            total = sum(float(item.book.final_price) * item.quantity for item in items)
            total = round(total, 2)
            
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=total,
                status='Pending',
                payment_method='WHATSAPP'
            )
            
            item_details = []
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    price=item.book.final_price,
                    quantity=item.quantity
                )
                item_details.append(f"- {item.book.title} x {item.quantity} (₹{item.book.final_price})")
                
                if item.book.stock >= item.quantity:
                    item.book.stock -= item.quantity
                else:
                    item.book.stock = 0
                item.book.save()
                
            items.delete()
            
            items_str = "\n".join(item_details)
            message = (
                f"Hello Bahi Hata,\n\n"
                f"I would like to place an order (Order #{order.id}):\n\n"
                f"*Items:*\n{items_str}\n\n"
                f"*Total Amount:* ₹{total}\n\n"
                f"*Shipping Address:*\n{shipping_address}"
            )
            
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/917978398598?text={encoded_message}"
            
            return JsonResponse({
                'success': True,
                'whatsapp_url': whatsapp_url
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

def auth_status(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book')
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        serialized_orders = []
        for o in orders:
            serialized_orders.append({
                'id': o.id,
                'total_amount': float(o.total_amount),
                'status': o.status,
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else None,
                'shipping_address': o.shipping_address,
            })
            
        user_data = {
            'username': request.user.username,
            'email': request.user.email,
            'phone_number': request.user.phone_number if getattr(request.user, 'phone_number', '') else '',
            'address': request.user.address if getattr(request.user, 'address', '') else '',
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        
        return JsonResponse({
            'is_authenticated': True,
            'user': user_data,
            'wishlist': [serialize_book(w.book) for w in wishlist_items],
            'orders': serialized_orders,
        })
        
    return JsonResponse({'is_authenticated': False})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            username = body.get('username', '')
            password = body.get('password', '')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                update_last_login(None, user)
                return JsonResponse({
                    'success': True,
                    'username': user.username
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            username = body.get('username', '')
            email = body.get('email', '')
            password = body.get('password', '')
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
                
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({
                'success': True,
                'username': user.username
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True})

@csrf_exempt
def profile_update(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            first_name = body.get('first_name', '')
            last_name = body.get('last_name', '')
            email = body.get('email', '')
            phone_number = body.get('phone_number', '')
            address = body.get('address', '')
            
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.phone_number = phone_number
            request.user.address = address
            request.user.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

@csrf_exempt
def change_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            old_password = body.get('old_password', '')
            new_password = body.get('new_password', '')
            
            if not request.user.check_password(old_password):
                return JsonResponse({'status': 'error', 'message': 'Incorrect current password'}, status=400)
                
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)