# Generated by Django 5.1.1 on 2024-09-11 20:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_fullarticle'),
        ('sales', '0004_detailedpurchaceorder_alter_orderarticle_article_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderarticle',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.article'),
        ),
    ]
