# Generated by Django 5.0.6 on 2024-06-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0011_order_courier_order_description_order_operator_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='extra_balance',
            field=models.FloatField(db_default=0.0),
        ),
    ]