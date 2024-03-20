from django.shortcuts import render, redirect
from django.http import HttpResponse

from store.models import Product
from cart.models import Cart, CartItem
from core.utils import get_object_or_none


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_to_cart(request, product_id):
    product = get_object_or_none(Product, id=product_id)
    # get the cart using the cart id present in the session
    cart = get_object_or_none(Cart, cart_id=_cart_id(request))

    if not cart:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    cart_item = get_object_or_none(CartItem, product=product, cart=cart)
    if not cart_item:
        cart_item = CartItem.objects.create(
            cart=cart, product=product, quantity=1)
        cart_item.save()
    else:
        cart_item.quantity += 1
        cart_item.save()
    return HttpResponse(cart_item.product)
    return redirect('cart')


def cart(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart)
    context = {
        'cart_items': cart_items
    }
    return render(request, 'store/cart.html', context)
