from django.db import models


class Category(models.Model):
    category_name = models.CharField(
        max_length=50, unique=True, db_collation='case_insensitive')
    slug = models.SlugField(unique=True, db_collation='case_insensitive')
    description = models.TextField(blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
