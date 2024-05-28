from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.db import connection

from .forms import RegistrationForm, UserProfileForm
from user.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from decouple import config
from core.utils import get_object_or_none, _cart_id
from cart.models import Cart, CartItem
from orders.models import Order

import requests


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['email'].split('@')[0]
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            user.save()

            # user activation link
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            html_content = get_template('user/account_verification_email.html')
            email_data = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            }

            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)

            body_text = f'Click this link to activate your account {domain}/user/activate/{uid}/{token}/'
            body_html = html_content.render({**email_data})
            to_email = email
            from_email = config('EMAIL_HOST_USER')

            send_email = EmailMultiAlternatives(
                mail_subject, body_text, from_email, [to_email])
            send_email.attach_alternative(body_html, "text/html")
            send_email.send(fail_silently=False)

            # messages.success(
            #     request, "Thank you for registering with us, we have sent an account activation link to your email, \
            #         please use that link to activate your account")
            return redirect(f'/user/login-user/?command=verification&email={email}')
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'user/register.html', context)


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                # get the cart items added when user was logged out
                cart_items = CartItem.objects.filter(cart=cart)
                if cart_items.exists():
                    # we need to group variations in case a user logs out adds additional items to cart and logs in again
                    # first we obtain product variations for the various cart items that exist in the cart
                    product_variations = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                    # get the cart items already associated with the user to access the existing product variations
                    user_cart_items = CartItem.objects.filter(user=user)
                    user_existing_product_variations_list = []
                    item_ids = []
                    for user_cart_item in user_cart_items:
                        current_item_existing_variations = user_cart_item.variations.all()
                        user_existing_product_variations_list.append(
                            list(current_item_existing_variations))
                        item_ids.append(user_cart_item.id)

                    for variation_item in product_variations:
                        if variation_item in user_existing_product_variations_list:
                            index = user_existing_product_variations_list.index(
                                variation_item)
                            item_id = item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            # note if we decide not to save below and instead add to a list to use bulk_update to optimize query performance
                            # this does not group the items, thus giving inconsistent results, therefore we just choose to save below
                            item.save()
                        else:
                            # if no variations already exist related to this user, we just update the user
                            cart_items.update(user=user)

            except:
                pass
            login(request, user)
            messages.success(request, "You are now logged in")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # example of query next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login_user')
    return render(request, 'user/login.html')


@login_required(login_url='login_user')
def logout_user(request):
    logout(request)
    messages.success(request, "You are now logged out")
    return redirect('login_user')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Your account has been activated successfully")
        return redirect('login_user')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')


@login_required(login_url='login_user')
def dashboard(request):
    orders_count = request.user.orderproduct_set.filter(
        ordered=True).count()
    context = {
        'orders_count': orders_count
    }
    return render(request, 'user/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_object_or_none(User, email__iexact=email)
        if user:
            # send password reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset your account password'
            html_content = get_template('user/reset_password_email.html')
            email_data = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            }

            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)

            body_text = f'Click this link to reset your account password {domain}/user/reset-password/{uid}/{token}/'
            body_html = html_content.render({**email_data})
            to_email = email
            from_email = config('EMAIL_HOST_USER')

            send_email = EmailMultiAlternatives(
                mail_subject, body_text, from_email, [to_email])
            send_email.attach_alternative(body_html, "text/html")
            send_email.send(fail_silently=False)
        messages.success(
            request, f"If {email} was found in the system, a password reset link was sent to {email}")

        return redirect('login_user')

    return render(request, 'user/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # we set this in the session so that we can access it later in the reset_password function below
        request.session['uid'] = uid
        messages.success(request, 'Proceed to reset your password')
        return redirect('reset_password')

    else:
        messages.error(request, "Invalid activation link")
        return redirect('forgot_password')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('reset_password')
        user = get_object_or_none(User, id=request.session.get('uid'))
        if not user:
            # if no user, we send them back to enter their email to get another password reset link
            messages.error(
                request, "Invalid request submitted, please try again")
            return redirect('forgot_password')
        user.set_password(password)
        user.save()
        messages.success(request, "You have successfully set your password")
        return redirect('login_user')
    return render(request, 'user/reset_password.html')


@login_required(login_url='login_user')
def my_orders(request):
    orders = request.user.order_set.filter(
        is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders
    }
    print(len(connection.queries))
    return render(request, 'user/my_orders.html', context)


@login_required(login_url='login_user')
def edit_profile(request):
    if request.method == 'POST':

        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(
                request, "Your profile has been updated successfully")
            return redirect('edit_profile')
        else:
            context = {
                'profile_form': profile_form
            }
            # print(profile_form.errors.get_context)
            # messages.error(
            #     request, "There was an error updating your profile, ensure your details are all okay")
            return render(request, 'user/edit_profile.html', context)
    else:
        profile_form = UserProfileForm(instance=request.user)
        context = {
            'profile_form': profile_form
        }

        return render(request, 'user/edit_profile.html', context)


@login_required(login_url='login_user')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password').strip()
        new_password = request.POST.get('new_password').strip()
        confirm_new_password = request.POST.get('confirm_new_password').strip()
        if not current_password or not new_password:
            messages.error(
                request, "current password and new password cannot be empty")
            return render(request, 'user/change_password.html')
        if not request.user.check_password(current_password):
            messages.error(request, "current password is incorrect")
            return render(request, 'user/change_password.html')
        if new_password != confirm_new_password:
            messages.error(
                request, "new password and confirm new password should match")
            return render(request, 'user/change_password.html')
        request.user.set_password(new_password)
        request.user.save()
        messages.success(
            request, "Your password has been updated successfully")
        return redirect('change_password')

    return render(request, 'user/change_password.html')


@login_required(login_url='login_user')
def order_details(request, orderNumber):
    order = get_object_or_none(Order, order_number=orderNumber)
    if not order:
        return redirect('my_orders')
    context = {
        'order': order,
        'order_sub_total': round(order.order_total - order.tax)
    }
    return render(request, 'user/order_details.html', context)
