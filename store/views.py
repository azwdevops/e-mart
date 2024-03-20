from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Product
from category.models import Category
from core.utils import get_object_or_none


def store(request, category_slug=None):
    category = None
    products = None
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        products_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        products_count = products.count()
    context = {
        'products': products,
        'products_count': products_count
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_none(
        Product, category__slug=category_slug, slug=product_slug)
    if not single_product:
        raise Http404

    context = {
        'single_product': single_product
    }
    return render(request, 'store/product_detail.html', context)
