# Generated by Django 5.0.6 on 2024-06-20 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0033_order_referral_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='competition',
            old_name='active',
            new_name='is_active',
        ),
    ]
