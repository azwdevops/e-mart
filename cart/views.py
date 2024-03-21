from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse

from store.models import Product, Variation
from cart.models import Cart, CartItem
from core.utils import get_object_or_none, _cart_id


def add_to_cart(request, product_id):
    product = get_object_or_none(Product, id=product_id)
    requested_product_variations = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product,
                                                  variation_category__iexact=key, variation_value__iexact=value)
                requested_product_variations.append(variation)
            except:
                pass
    # get the cart using the cart id present in the session
    cart = get_object_or_none(Cart, cart_id=_cart_id(request))

    if not cart:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    cart_items = CartItem.objects.filter(
        product=product, cart=cart)
    if cart_items.exists():
        # existing variations -> database
        # current variation -> product_variation
        # item_id -> database
        existing_variations_list = []
        # cart_item_ids = []  # cart item ids
        for item in cart_items:
            current_item_variations = item.variations.all()
            existing_variations_list.append(list(current_item_variations))
            # cart_item_ids.append(item.id)

        if requested_product_variations in existing_variations_list:
            # the index of the variation is going to be the same as the index of item in cart_items since we are looping through
            # cart items and adding the variations as we loop
            index = existing_variations_list.index(
                requested_product_variations)
            # item_id = cart_item_ids[index]
            # item = CartItem.objects.get(product=product, id=item_id)
            item = cart_items[index]
            # increase cart item quantity
            item.quantity += 1
            item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)
            if len(requested_product_variations) > 0:
                cart_item.variations.add(*requested_product_variations)
    else:
        # means this product does not exist in the cart, thus we add it to the cart
        cart_item = CartItem.objects.create(
            product=product, quantity=1, cart=cart)
        if len(requested_product_variations) > 0:
            cart_item.variations.add(*requested_product_variations)

    return redirect('cart')


def reduce_cart_item(request, cart_item_id):
    cart_item = get_object_or_none(CartItem, id=cart_item_id)
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_none(CartItem, id=cart_item_id)
    if cart_item:
        cart_item.delete()

    return redirect('cart')


def cart(request, totals=0, quantity=0, cart_items=[]):
    tax = 0
    grand_totals = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            totals += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        # we charge VAT here at the rate of 16%
        tax = 16 * totals/100
        grand_totals = totals + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'totals': totals,
        'quantity': quantity,
        'tax': tax,
        'grand_totals': grand_totals,
    }
    return render(request, 'store/cart.html', context)
