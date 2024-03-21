from .models import Cart, CartItem

from core.utils import _cart_id


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = sum(cart_items.values_list('quantity', flat=True))
        except Cart.DoesNotExist:
            pass
    return dict(cart_count=cart_count)
