from django.urls import path

from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('order-complete/', views.order_complete, name='order_complete'),

]
