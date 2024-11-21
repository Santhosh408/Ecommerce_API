# Generated by Django 5.1.2 on 2024-11-15 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce_app', '0004_order_orderitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='price',
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
