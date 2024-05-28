import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.db import connection
from decouple import config
from django.contrib.auth.decorators import login_required

from cart.models import CartItem
import datetime

from .forms import OrderForm
from .models import Order, Payment, OrderProduct


def place_order(request):
    current_user = request.user
    # if the cart count is less than or equal to 0, then redirect back to store
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')
    totals = 0
    tax = 0
    grand_totals = 0
    for item in cart_items:
        totals += item.product.price * item.quantity
    tax = 16 * totals/100
    grand_totals = totals + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            # get the cleaned data and store it
            new_order = Order()
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.email = form.cleaned_data['email']
            new_order.phone = form.cleaned_data['phone']
            new_order.address_line_1 = form.cleaned_data['address_line_1']
            new_order.address_line_2 = form.cleaned_data['address_line_2']
            new_order.city = form.cleaned_data['city']
            new_order.state = form.cleaned_data['state']
            new_order.country = form.cleaned_data['country']
            new_order.order_note = form.cleaned_data['order_note']
            new_order.order_total = grand_totals
            new_order.tax = tax
            new_order.ip = request.META.get('REMOTE_ADDR')
            new_order.user = request.user
            new_order.save()

            # generate order number
            year_item = int(datetime.date.today().strftime('%Y'))
            day_item = int(datetime.date.today().strftime('%d'))
            month_item = int(datetime.date.today().strftime('%m'))
            date_obj = datetime.date(year_item, month_item, day_item)
            current_date = date_obj.strftime('%Y%m%d')
            order_number = f'{current_date}{new_order.id}'

            new_order.order_number = order_number
            new_order.save()

            context = {
                'order': new_order,
                'sub_totals': grand_totals - tax,
                'tax': tax,
                'grand_totals': grand_totals,
                'cart_items': cart_items,
            }

            return render(request, 'orders/make_payment.html', context)
        else:
            print(form.errors)
            return HttpResponse('error occurred')

    else:
        return redirect('checkout')


def make_payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])
    # store transaction details inside payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move the cart items to order products table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = item.product
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product.variations.add(*product_variation)

        # reduce the quantity of sold products
        product = item.product
        product.stock -= item.quantity
        product.save()

    # clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # send order received email to customer
    mail_subject = 'Thank you for your order.'
    html_content = get_template('orders/order_received_email.html')
    email_data = {
        'user': request.user,
        'order': order
    }

    body_text = f'Your order has been received'
    body_html = html_content.render({**email_data})
    to_email = request.user.email
    from_email = config('EMAIL_HOST_USER')

    send_email = EmailMultiAlternatives(
        mail_subject, body_text, from_email, [to_email])
    send_email.attach_alternative(body_html, "text/html")
    send_email.send(fail_silently=False)

    # send order number and transaction id to sendData method on frontend via JsonResponse
    data = {
        'order_number': order.order_number,
        'payment_id': payment.payment_id
    }

    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    payment = Payment.objects.get(payment_id=payment_id)
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        context = {
            'order': order,
            'payment': payment,
            'order_sub_total': round(order.order_total - order.tax)
        }
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
