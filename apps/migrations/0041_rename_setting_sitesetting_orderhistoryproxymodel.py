# Generated by Django 5.0.6 on 2024-06-22 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0040_alter_archivedorderproxymodel_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Setting',
            new_name='SiteSetting',
        ),
        migrations.CreateModel(
            name='OrderHistoryProxyModel',
            fields=[
            ],
            options={
                'verbose_name': 'Order History',
                'verbose_name_plural': 'Order Histories',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('apps.order',),
        ),
    ]