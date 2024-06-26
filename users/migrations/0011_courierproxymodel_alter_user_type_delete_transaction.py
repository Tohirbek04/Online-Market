# Generated by Django 5.0.6 on 2024-06-22 18:33

from django.db import migrations, models

import users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_transaction_chek_alter_transaction_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourierProxyModel',
            fields=[
            ],
            options={
                'verbose_name': 'Courier',
                'verbose_name_plural': 'Couriers',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.user',),
            managers=[
                ('objects', users.managers.CourierProxyManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('operator', 'Operator'), ('manager', 'Manager'), ('admin', 'Admin'), ('client', 'Client'), ('courier', 'Courier')], default='client', max_length=10),
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]