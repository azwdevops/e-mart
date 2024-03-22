from django.urls import path

from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('reduce-cart-item/<int:cart_item_id>/',
         views.reduce_cart_item, name='reduce_cart_item'),
    path('remove-cart-item/<int:cart_item_id>/',
         views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
]
