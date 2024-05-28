# Generated by Django 4.2.11 on 2024-03-22 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_line_2',
            field=models.EmailField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_total',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.FloatField(null=True),
        ),
    ]