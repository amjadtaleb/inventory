# Generated by Django 5.1.1 on 2024-09-11 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaceorder',
            name='reference',
            field=models.SlugField(unique=True),
        ),
    ]
