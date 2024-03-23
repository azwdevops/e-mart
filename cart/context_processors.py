from .models import Cart, CartItem

from core.utils import _cart_id

from decouple import config


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            carts = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                # we get a single cart
                cart_items = CartItem.objects.filter(cart=carts[:1])
            cart_count = sum(cart_items.values_list('quantity', flat=True))
        except Cart.DoesNotExist:
            pass
    return dict(cart_count=cart_count)


def paypal_client_id(request):
    return dict(paypal_client_id=config('PAYPAL_CLIENT_ID'))
