# Generated by Django 5.0.6 on 2024-06-25 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_user_district_alter_user_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.IntegerField(db_default=0),
        ),
    ]