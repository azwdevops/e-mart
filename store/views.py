from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from orders.models import OrderProduct
from core.utils import get_object_or_none, _cart_id
from .forms import ReviewForm


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

    try:
        user_has_purchased = OrderProduct.objects.filter(
            user=request.user, product=single_product).exists()
    except:
        user_has_purchased = False

    # get the reviews
    reviews = ReviewRating.objects.filter(product=single_product, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'user_has_purchased': user_has_purchased,
        'reviews': reviews
    }
    print(len(connection.queries))
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


@login_required
def submit_review(request, product_id):
    product_page_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(
                user=request.user, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(
                request, 'Thank you. Your review has been updated')
            #  redirect to the same page
            return redirect(product_page_url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                new_review = ReviewRating()
                new_review.subject = form.cleaned_data['subject']
                new_review.review = form.cleaned_data['review']
                new_review.rating = form.cleaned_data['rating']
                new_review.ip_address = request.META.get('REMOTE_ADDR')
                new_review.product = Product.objects.get(id=product_id)
                new_review.user = request.user
                new_review.save()
                messages.success(
                    request, 'Thank you. Your review has been submitted')

                return redirect(product_page_url)
