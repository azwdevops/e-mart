from django.contrib.admin import register, ModelAdmin

from store.models import Product


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['product_name', 'stock']
    prepopulated_fields = {'slug': ['product_name']}
