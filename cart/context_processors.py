from .models import Cart, CartItem

from core.utils import _cart_id


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
