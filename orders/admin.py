from django.contrib.admin import ModelAdmin, register, TabularInline

from .models import Payment, Order, OrderProduct


@register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ['payment_id']


class OrderProductInline(TabularInline):
    model = OrderProduct
    readonly_fields = ['payment', 'user', 'product',
                       'quantity', 'product_price', 'ordered']
    extra = 0


@register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email',
                    'city', 'order_total', 'tax', 'status', 'is_ordered']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name',
                     'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]


@register(OrderProduct)
class OrderProductAdmin(ModelAdmin):
    list_display = ['payment', 'product']
