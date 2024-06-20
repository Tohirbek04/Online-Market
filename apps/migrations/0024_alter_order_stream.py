# Generated by Django 5.0.6 on 2024-06-19 08:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0023_remove_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stream',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream', to='apps.stream'),
        ),
    ]