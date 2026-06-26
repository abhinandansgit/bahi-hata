from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import Wishlist
from vendors.models import Vendor
from store.models import Book
from orders.models import Order


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_vendor:
                Vendor.objects.create(user=user, shop_name=f"{user.username}'s Shop")
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='accounts:login')
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist = Wishlist.objects.filter(user=request.user).select_related('book', 'book__category')

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.phone_number = request.POST.get('phone_number', '')
        request.user.address = request.POST.get('address', '')
        request.user.save()
        return redirect('accounts:profile')

    context = {
        'orders': orders,
        'wishlist': wishlist,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts:login')
def toggle_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, book=book)

    if not created:
        wishlist_item.delete()
        added = False
    else:
        added = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'book_title': book.title})

    return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))


@login_required(login_url='accounts:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'accounts/order_detail.html', context)
@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})
