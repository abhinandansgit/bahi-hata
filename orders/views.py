from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import urllib.parse
from .models import (
    Cart, CartItem, ComboCartItem, MagazineCartItem,
    Order, OrderItem, ComboOrderItem, MagazineOrderItem
)
from store.models import Book, BookCombo, Offer, MagazineEdition


# ─────────────────────────────────────────────────
# CART HELPERS & SERIALIZATION
# ─────────────────────────────────────────────────

def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _serialize_cart(cart):
    items = []
    for item in cart.items.select_related('book', 'book__category').all():
        items.append({
            'id': item.id,
            'type': 'book',
            'title': item.book.title,
            'slug': item.book.slug,
            'author': item.book.author,
            'category': item.book.category.name if item.book.category else '',
            'price': float(item.book.final_price),
            'original_price': float(item.book.price),
            'quantity': item.quantity,
            'subtotal': float(item.total_price),
            'cover_image_url': item.book.cover_image_url or '',
            'stock': item.book.stock,
            'update_url': f"/orders/cart/update/{item.id}/",
            'remove_url': f"/orders/cart/remove/{item.id}/",
        })

    combo_items = []
    for ci in cart.combo_items.select_related('combo').prefetch_related('combo__books').all():
        combo_items.append({
            'id': ci.id,
            'type': 'combo',
            'name': ci.combo.name,
            'books_included': [b.title for b in ci.combo.books.all()],
            'price': float(ci.combo.combo_price),
            'quantity': ci.quantity,
            'subtotal': float(ci.total_price),
            'cover_image_url': ci.combo.cover_image_url or '',
            'remove_url': f"/orders/cart/remove-combo/{ci.id}/",
        })

    magazine_items = []
    for mi in cart.magazine_items.select_related('edition').all():
        magazine_items.append({
            'id': mi.id,
            'type': 'magazine',
            'title': mi.edition.title,
            'year': mi.edition.edition_year,
            'issue': mi.edition.issue_number,
            'language': mi.edition.get_language_display(),
            'price': float(mi.edition.final_price),
            'quantity': mi.quantity,
            'subtotal': float(mi.total_price),
            'cover_image_url': mi.edition.cover_image_url or '',
            'stock': mi.edition.stock,
            'update_url': f"/orders/cart/update-magazine/{mi.id}/",
            'remove_url': f"/orders/cart/remove-magazine/{mi.id}/",
        })

    return {
        'items': items,
        'combo_items': combo_items,
        'magazine_items': magazine_items,
        'total_items_count': cart.item_count,
        'subtotal': float(cart.total_price),
    }


def cart_data_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'authenticated': False,
            'cart': {
                'items': [],
                'combo_items': [],
                'magazine_items': [],
                'total_items_count': 0,
                'subtotal': 0.00
            }
        })
    cart = _get_cart(request.user)
    return JsonResponse({'authenticated': True, 'cart': _serialize_cart(cart)})


def add_to_cart(request, book_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

    if not request.user.is_authenticated:
        if is_ajax:
            login_url = f"/accounts/login/?next={urllib.parse.quote(request.META.get('HTTP_REFERER', '/'))}"
            return JsonResponse({'success': False, 'login_required': True, 'login_url': login_url}, status=401)
        return redirect(f"/accounts/login/?next={request.path}")

    book = get_object_or_404(Book, id=book_id)

    if not book.in_stock:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f'"{book.title}" is currently out of stock.'}, status=400)
        messages.error(request, f'"{book.title}" is currently out of stock.')
        return redirect('store:book_detail', slug=book.slug)

    cart = _get_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()
            msg = f'Added another copy of "{book.title}" to shelf.'
        else:
            msg = f'Only {book.stock} units available.'
    else:
        msg = f'"{book.title}" added to your shelf!'

    if request.GET.get('checkout') == '1':
        return redirect('orders:checkout')

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart': _serialize_cart(cart)
        })

    messages.success(request, msg)
    return redirect('orders:view_cart')


def add_combo_to_cart(request, combo_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

    if not request.user.is_authenticated:
        if is_ajax:
            login_url = f"/accounts/login/?next={urllib.parse.quote(request.META.get('HTTP_REFERER', '/'))}"
            return JsonResponse({'success': False, 'login_required': True, 'login_url': login_url}, status=401)
        return redirect(f"/accounts/login/?next={request.path}")

    combo = get_object_or_404(BookCombo, id=combo_id, is_active=True)

    if not combo.all_in_stock:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f'One or more books in "{combo.name}" are out of stock.'}, status=400)
        messages.error(request, f'One or more books in "{combo.name}" are out of stock.')
        return redirect('store:combos')

    cart = _get_cart(request.user)
    _, created = ComboCartItem.objects.get_or_create(cart=cart, combo=combo)
    if not created:
        msg = f'"{combo.name}" is already in your shelf.'
    else:
        msg = f'"{combo.name}" combo added to shelf!'

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart': _serialize_cart(cart)
        })

    messages.success(request, msg)
    return redirect('orders:view_cart')


def add_magazine_to_cart(request, edition_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

    if not request.user.is_authenticated:
        if is_ajax:
            login_url = f"/accounts/login/?next={urllib.parse.quote(request.META.get('HTTP_REFERER', '/'))}"
            return JsonResponse({'success': False, 'login_required': True, 'login_url': login_url}, status=401)
        return redirect(f"/accounts/login/?next={request.path}")

    edition = get_object_or_404(MagazineEdition, id=edition_id, is_active=True)
    if edition.stock <= 0:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f'Sorry, "{edition.title}" is out of stock.'}, status=400)
        messages.error(request, f'Sorry, "{edition.title}" is currently out of stock.')
        return redirect('store:magazine')

    cart = _get_cart(request.user)
    item, created = MagazineCartItem.objects.get_or_create(cart=cart, edition=edition)
    if not created:
        if item.quantity < edition.stock:
            item.quantity += 1
            item.save()
            msg = f'Updated "{edition.title}" quantity in shelf.'
        else:
            msg = f'Maximum stock ({edition.stock}) reached for this magazine edition.'
    else:
        msg = f'"{edition.title}" added to your shelf!'

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart': _serialize_cart(cart)
        })

    messages.success(request, msg)
    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def view_cart(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related('book', 'book__category').all()
    combo_items = cart.combo_items.select_related('combo').prefetch_related('combo__books').all()
    magazine_items = cart.magazine_items.select_related('edition').all()

    total = cart.total_price

    # Coupon session
    coupon_code = request.session.get('coupon_code', '')
    coupon_discount = 0
    coupon_obj = None
    coupon_error = None

    if coupon_code:
        try:
            coupon_obj = Offer.objects.get(code=coupon_code.upper())
            if coupon_obj.is_valid_now and total >= coupon_obj.minimum_order_value:
                coupon_discount = coupon_obj.calculate_discount(total)
            else:
                coupon_error = 'Coupon is no longer valid or minimum order value not met.'
                del request.session['coupon_code']
                coupon_obj = None
                coupon_code = ''
        except Offer.DoesNotExist:
            del request.session['coupon_code']
            coupon_code = ''

    final_total = round(total - coupon_discount, 2)

    context = {
        'items': items,
        'combo_items': combo_items,
        'magazine_items': magazine_items,
        'total': total,
        'coupon_discount': round(coupon_discount, 2),
        'final_total': final_total,
        'coupon_code': coupon_code,
        'coupon_obj': coupon_obj,
        'coupon_error': coupon_error,
        'cart': cart,
    }
    return render(request, 'orders/cart.html', context)


@login_required(login_url='accounts:login')
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').upper().strip()
        if code:
            try:
                offer = Offer.objects.get(code=code, is_active=True)
                if not offer.is_valid_now:
                    messages.error(request, 'This coupon has expired or reached its usage limit.')
                else:
                    request.session['coupon_code'] = code
                    messages.success(request, f'Coupon "{code}" applied!')
            except Offer.DoesNotExist:
                messages.error(request, f'Coupon "{code}" is not valid.')
        else:
            # Remove coupon
            request.session.pop('coupon_code', None)
            messages.info(request, 'Coupon removed.')
    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.GET.get('action', '')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

    if action == 'increase':
        if item.quantity < item.book.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(request, f'Maximum stock reached for "{item.book.title}".')
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    if is_ajax:
        cart = _get_cart(request.user)
        return JsonResponse({'success': True, 'cart': _serialize_cart(cart)})

    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if is_ajax:
        cart = _get_cart(request.user)
        return JsonResponse({'success': True, 'message': 'Book removed from shelf', 'cart': _serialize_cart(cart)})
    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def remove_combo_from_cart(request, item_id):
    item = get_object_or_404(ComboCartItem, id=item_id, cart__user=request.user)
    item.delete()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if is_ajax:
        cart = _get_cart(request.user)
        return JsonResponse({'success': True, 'message': 'Combo removed from shelf', 'cart': _serialize_cart(cart)})
    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def update_magazine_cart_item(request, item_id):
    item = get_object_or_404(MagazineCartItem, id=item_id, cart__user=request.user)
    action = request.GET.get('action', '')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

    if action == 'increase':
        if item.quantity < item.edition.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(request, f'Maximum stock reached for "{item.edition.title}".')
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    if is_ajax:
        cart = _get_cart(request.user)
        return JsonResponse({'success': True, 'cart': _serialize_cart(cart)})

    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def remove_magazine_from_cart(request, item_id):
    item = get_object_or_404(MagazineCartItem, id=item_id, cart__user=request.user)
    item.delete()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if is_ajax:
        cart = _get_cart(request.user)
        return JsonResponse({'success': True, 'message': 'Magazine removed from shelf', 'cart': _serialize_cart(cart)})
    return redirect('orders:view_cart')


# ─────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────

@login_required(login_url='accounts:login')
def checkout(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related('book').all()
    combo_items = cart.combo_items.select_related('combo').prefetch_related('combo__books').all()
    magazine_items = cart.magazine_items.select_related('edition').all()

    if not items.exists() and not combo_items.exists() and not magazine_items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('orders:view_cart')

    # Stock validation
    for item in items:
        if item.book.stock < item.quantity:
            messages.error(
                request,
                f'"{item.book.title}" only has {item.book.stock} unit(s) left. '
                'Please update your cart.'
            )
            return redirect('orders:view_cart')

    for ci in combo_items:
        if not ci.combo.all_in_stock:
            messages.error(
                request,
                f'One or more books in combo "{ci.combo.name}" are out of stock.'
            )
            return redirect('orders:view_cart')

    for mi in magazine_items:
        if mi.edition.stock < mi.quantity:
            messages.error(
                request,
                f'"{mi.edition.title}" only has {mi.edition.stock} copies left. '
                'Please update your cart.'
            )
            return redirect('orders:view_cart')

    subtotal = cart.total_price

    # Coupon
    coupon_code = request.session.get('coupon_code', '')
    coupon_obj = None
    coupon_discount = 0
    if coupon_code:
        try:
            coupon_obj = Offer.objects.get(code=coupon_code.upper())
            if coupon_obj.is_valid_now and subtotal >= coupon_obj.minimum_order_value:
                coupon_discount = coupon_obj.calculate_discount(subtotal)
        except Offer.DoesNotExist:
            pass

    final_total = round(subtotal - coupon_discount, 2)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        if not all([full_name, phone, address, city, pincode]):
            messages.error(request, 'Please fill in all shipping details.')
            return redirect('orders:checkout')

        shipping_address = f"{full_name}\n{phone}\n{address}\n{city} - {pincode}"

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=subtotal,
            discount_amount=round(coupon_discount, 2),
            final_amount=final_total,
            status='Pending',
            payment_method='WHATSAPP',
            coupon=coupon_obj,
            coupon_code_used=coupon_code,
        )

        # Increment coupon usage
        if coupon_obj:
            coupon_obj.times_used += 1
            coupon_obj.save(update_fields=['times_used'])

        wa_lines = []

        # Book items
        for item in items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                price=item.book.final_price,
                quantity=item.quantity,
            )
            wa_lines.append(
                f"- {item.quantity} × {item.book.title} @ ₹{item.book.final_price} "
                f"= ₹{item.total_price}"
            )
            # Deduct stock
            item.book.stock = max(0, item.book.stock - item.quantity)
            item.book.save(update_fields=['stock'])

        # Combo items
        for ci in combo_items:
            ComboOrderItem.objects.create(
                order=order,
                combo=ci.combo,
                price=ci.combo.combo_price,
                quantity=ci.quantity,
                combo_name_snapshot=ci.combo.name,
            )
            wa_lines.append(
                f"- 🎁 COMBO × {ci.quantity}: {ci.combo.name} @ ₹{ci.combo.combo_price} "
                f"= ₹{ci.total_price}"
            )
            # Deduct stock from each book in the combo
            for book in ci.combo.books.all():
                book.stock = max(0, book.stock - ci.quantity)
                book.save(update_fields=['stock'])

        # Magazine items
        for mi in magazine_items:
            MagazineOrderItem.objects.create(
                order=order,
                edition=mi.edition,
                price=mi.edition.final_price,
                quantity=mi.quantity,
                title_snapshot=mi.edition.title,
            )
            wa_lines.append(
                f"- 📖 MAGAZINE × {mi.quantity}: {mi.edition.title} @ ₹{mi.edition.final_price} "
                f"= ₹{mi.total_price}"
            )
            # Deduct stock
            mi.edition.stock = max(0, mi.edition.stock - mi.quantity)
            mi.edition.save(update_fields=['stock'])

        # Clear cart
        cart.items.all().delete()
        cart.combo_items.all().delete()
        cart.magazine_items.all().delete()
        request.session.pop('coupon_code', None)

        # Build WhatsApp message
        message = (
            f"Hello Bahi Hata! 📚\n\n"
            f"*Order #{order.id}*\n"
            f"─────────────────\n"
            f"*Items:*\n" + "\n".join(wa_lines) +
            f"\n─────────────────\n"
        )
        if coupon_discount > 0:
            message += f"Subtotal: ₹{subtotal}\nDiscount ({coupon_code}): -₹{round(coupon_discount,2)}\n"
        message += (
            f"*Total: ₹{final_total}*\n\n"
            f"*Delivery Address:*\n{shipping_address}\n\n"
            f"Please confirm availability and delivery details. Thank you! 🙏"
        )

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/916372202830?text={encoded_message}"
        return redirect(whatsapp_url)

    context = {
        'items': items,
        'combo_items': combo_items,
        'magazine_items': magazine_items,
        'subtotal': subtotal,
        'coupon_discount': round(coupon_discount, 2),
        'final_total': final_total,
        'coupon_code': coupon_code,
        'coupon_obj': coupon_obj,
        'user': request.user,
    }
    return render(request, 'orders/checkout.html', context)


# ─────────────────────────────────────────────────
# AJAX — Cart count for header badge
# ─────────────────────────────────────────────────

def cart_count_api(request):
    if request.user.is_authenticated:
        try:
            count = request.user.cart.item_count
        except Exception:
            count = 0
    else:
        count = 0
    return JsonResponse({'count': count})
