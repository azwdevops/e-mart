from django.contrib.admin import register, ModelAdmin

from store.models import Product, Variation


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['product_name', 'stock']
    prepopulated_fields = {'slug': ['product_name']}


@register(Variation)
class VariationAdmin(ModelAdmin):
    list_display = ['product', 'variation_category',
                    'variation_value', 'is_active']
    list_editable = ['is_active']
    list_filter = ['product', 'variation_category', 'variation_value']
