# Generated by Django 5.1.1 on 2024-09-11 14:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0003_alter_article_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('reference', models.SlugField(primary_key=True, serialize=False)),
                ('value', models.DecimalField(decimal_places=3, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaceOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.SlugField()),
                ('created_at', models.DateTimeField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryarticle')),
                ('purchace_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', related_query_name='article', to='sales.purchaceorder')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateTimeField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.category')),
                ('tax', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.tax')),
            ],
        ),
    ]
