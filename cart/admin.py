from django.contrib.admin import ModelAdmin, register

from .models import Cart, CartItem


@register(Cart)
class CartAdmin(ModelAdmin):
    list_dsiplay = ['cart_id']


@register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['product', 'cart']
