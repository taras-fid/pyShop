# Generated by Django 4.1.7 on 2023-03-04 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default=None, upload_to='static/images/products_img'),
        ),
    ]
