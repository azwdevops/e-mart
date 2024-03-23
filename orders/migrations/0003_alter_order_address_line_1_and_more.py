# Generated by Django 4.2.11 on 2024-03-22 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_address_line_2_alter_order_order_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_line_1',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='country',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_note',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(max_length=50),
        ),
    ]
