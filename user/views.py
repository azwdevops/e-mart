from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template

from .forms import RegistrationForm
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
            mail_subject = 'Activate you account'
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
            login(request, user)
            messages.success(request, "You are now logged in")
            return redirect('home')
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
