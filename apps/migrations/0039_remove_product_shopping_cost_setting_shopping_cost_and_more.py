# Generated by Django 5.0.6 on 2024-06-22 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0038_order_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='shopping_cost',
        ),
        migrations.AddField(
            model_name='setting',
            name='shopping_cost',
            field=models.IntegerField(default=1, verbose_name='curyer uchun beriladigan pul'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='setting',
            name='min_sum',
            field=models.IntegerField(verbose_name='eng kam yechib olish mumkin bolgan pul'),
        ),
    ]
