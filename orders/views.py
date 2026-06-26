from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import urllib.parse
from .models import Cart, CartItem, Order, OrderItem
from store.models import Book


@login_required(login_url='accounts:login')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book', 'book__category').all()

    total = sum([item.book.final_price * item.quantity for item in items])

    context = {
        'items': items,
        'total': round(total, 2),
        'cart': cart
    }
    return render(request, 'orders/cart.html', context)


@login_required(login_url='accounts:login')
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.GET.get('action', '')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('orders:view_cart')


@login_required(login_url='accounts:login')
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book').all()

    if not items:
        return redirect('orders:view_cart')

    total = sum([item.book.final_price * item.quantity for item in items])

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '')

        shipping_address = f"{full_name}\n{phone}\n{address}\n{city} - {pincode}"

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=round(total, 2),
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
            item_details.append(f"- {item.quantity} x {item.book.title} (₹{item.book.final_price * item.quantity})")
            
            if item.book.stock >= item.quantity:
                item.book.stock -= item.quantity
            else:
                item.book.stock = 0
            item.book.save()

        cart.items.all().delete()

        # Build WhatsApp message
        message = f"Hello Bahi Hata,\n\nI would like to place an order (Order #{order.id}):\n\n*Items:*\n"
        message += "\n".join(item_details)
        message += f"\n\n*Total Amount:* ₹{total}\n\n*Shipping Address:*\n{shipping_address}"
        
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/917978398598?text={encoded_message}"

        return redirect(whatsapp_url)

    context = {
        'items': items,
        'total': round(total, 2),
        'user': request.user,
    }
    return render(request, 'orders/checkout.html', context)
