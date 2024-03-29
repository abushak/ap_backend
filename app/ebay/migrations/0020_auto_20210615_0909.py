# Generated by Django 3.1.4 on 2021-06-15 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ebay', '0019_auto_20210323_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('keyword', models.CharField(help_text='Max. length 255 characters.', max_length=255, verbose_name='Search index keyword')),
                ('description', models.TextField(blank=True, help_text='May contain HTML tags.', null=True, verbose_name='Description')),
                ('image', models.URLField(help_text='Image URL', null=True, verbose_name='Image url')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Name of the product vendor', max_length=255, verbose_name='Vendor')),
                ('url', models.URLField(help_text='Product Vendor Link', null=True, verbose_name='Link')),
            ],
            options={
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
            },
        ),
        migrations.AlterField(
            model_name='product',
            name='ebay_id',
            field=models.BigIntegerField(blank=True, help_text='eBay Item ID from API', null=True, verbose_name='eBay Item ID'),
        ),
        migrations.AddField(
            model_name='product',
            name='vendor_id',
            field=models.ForeignKey(blank=True, help_text='Product vendor', null=True, on_delete=django.db.models.deletion.CASCADE, to='ebay.vendor', verbose_name='Vendor'),
        ),
    ]
