from django.db import models

from category.models import Category
from django.urls import reverse
from .choices import variation_category_choices


class Product(models.Model):
    product_name = models.CharField(
        max_length=200, unique=True, db_collation='case_insensitive')
    slug = models.SlugField(unique=True, db_collation='case_insensitive')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(blank=True, upload_to='photos/products')
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product_detail', kwargs={'category_slug': self.category.slug, 'product_slug': self.slug})


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
