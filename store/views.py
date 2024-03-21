from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from .models import Product
from category.models import Category
from cart.models import CartItem
from core.utils import get_object_or_none, _cart_id


def store(request, category_slug=None):
    category = None
    products = None
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=category, is_available=True).order_by('id')
    else:
        products = Product.objects.filter(is_available=True).order_by('id')

    products_count = products.count()
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products': paged_products,
        'products_count': products_count
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_none(
        Product, category__slug=category_slug, slug=product_slug)
    if not single_product:
        raise Http404
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
        request), product=single_product).exists()

    context = {
        'single_product': single_product,
        'in_cart': in_cart
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(description__icontains=keyword)
    context = {
        'products': products,
        'products_count': products.count()
    }
    return render(request, 'store/store.html', context)
