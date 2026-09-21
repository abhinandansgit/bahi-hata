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


import json
import re
import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from accounts.models import User

@csrf_exempt
def google_auth_view(request):
    """
    Handles Passwordless Google Sign-In & Registration.
    Accepts Google Identity Services ID token (JWT) or instant email verification.
    """
    if request.method != 'POST':
        return redirect('accounts:login')

    credential = request.POST.get('credential')
    email = None
    first_name = ''
    last_name = ''
    picture = ''

    # 1. Parse JSON body if sent via fetch
    if not credential and request.content_type == 'application/json':
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            credential = body_data.get('credential')
            email = body_data.get('email')
            first_name = body_data.get('first_name', '')
            last_name = body_data.get('last_name', '')
            picture = body_data.get('picture', '')
        except Exception:
            pass

    # 2. If Google Credential token provided, verify with Google
    if credential:
        try:
            verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            resp = requests.get(verify_url, timeout=6)
            if resp.status_code == 200:
                payload = resp.json()
                email = payload.get('email')
                first_name = payload.get('given_name') or payload.get('name', '').split(' ')[0]
                last_name = payload.get('family_name') or ' '.join(payload.get('name', '').split(' ')[1:])
                picture = payload.get('picture', '')
            else:
                return JsonResponse({'success': False, 'error': 'Google token validation failed'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Google verification error: {str(e)}'}, status=500)

    # Fallback to direct POST email (instant passwordless sign-in)
    if not email:
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

    if not email:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': 'No email address provided by Google'}, status=400)
        messages.error(request, 'Google sign-in failed: No email received.')
        return redirect('accounts:login')

    # 3. Find or Create User
    email = email.strip().lower()
    user = User.objects.filter(email__iexact=email).first()

    if not user:
        # Base username on email prefix
        base_username = email.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '_', base_username)
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{suffix}"
            suffix += 1

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_picture_url=picture or None,
            is_customer=True,
            is_active=True
        )
        user.set_unusable_password()  # No password required for Google auth!
        user.save()
    else:
        updated = False
        if not user.first_name and first_name:
            user.first_name = first_name
            updated = True
        if not user.last_name and last_name:
            user.last_name = last_name
            updated = True
        if not user.profile_picture_url and picture:
            user.profile_picture_url = picture
            updated = True
        if updated:
            user.save()

    # 4. Authenticate & Log in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if next_url in ['accounts:login', 'accounts:register', '/accounts/login/', '/accounts/register/']:
        next_url = '/'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'redirect_url': '/' if next_url == 'home' else next_url})

    return redirect(next_url)


from django.conf import settings

@csrf_exempt
def supabase_auth_sync(request):
    """
    Synchronizes a Supabase Google authenticated user into Django session.
    Accepts access_token or user details from the Supabase client SDK.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    email = data.get('email')
    full_name = data.get('full_name') or data.get('name') or ''
    avatar_url = data.get('avatar_url') or data.get('picture') or ''
    access_token = data.get('access_token')

    supabase_url = getattr(settings, 'SUPABASE_URL', '')
    supabase_anon_key = getattr(settings, 'SUPABASE_ANON_KEY', '')

    if access_token and supabase_url and supabase_anon_key:
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'apikey': supabase_anon_key
            }
            resp = requests.get(f"{supabase_url.rstrip('/')}/auth/v1/user", headers=headers, timeout=6)
            if resp.status_code == 200:
                user_info = resp.json()
                email = user_info.get('email') or email
                user_meta = user_info.get('user_metadata', {})
                full_name = user_meta.get('full_name') or user_meta.get('name') or full_name
                avatar_url = user_meta.get('avatar_url') or user_meta.get('picture') or avatar_url
        except Exception as e:
            print(f"Supabase auth check: {e}")

    if not email:
        return JsonResponse({'success': False, 'error': 'No email returned from Supabase Auth'}, status=400)

    email = email.strip().lower()
    first_name = full_name.split(' ')[0] if full_name else ''
    last_name = ' '.join(full_name.split(' ')[1:]) if full_name and ' ' in full_name else ''

    user = User.objects.filter(email__iexact=email).first()

    if not user:
        base_username = email.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '_', base_username)
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{suffix}"
            suffix += 1

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_picture_url=avatar_url or None,
            is_customer=True,
            is_active=True
        )
        user.set_unusable_password()
        user.save()
    else:
        updated = False
        if not user.first_name and first_name:
            user.first_name = first_name
            updated = True
        if not user.last_name and last_name:
            user.last_name = last_name
            updated = True
        if not user.profile_picture_url and avatar_url:
            user.profile_picture_url = avatar_url
            updated = True
        if updated:
            user.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return JsonResponse({'success': True, 'redirect_url': '/'})


def supabase_callback_view(request):
    """
    Renders callback receiver template that extracts Supabase OAuth token from URL hash fragment.
    """
    return render(request, 'accounts/supabase_callback.html')


