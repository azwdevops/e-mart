from django.contrib.admin import register, ModelAdmin

from .models import Category


@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['category_name']
    prepopulated_fields = {'slug': ['category_name']}
