# Generated by Django 3.1.4 on 2021-03-02 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebay', '0010_auto_20210302_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand_type',
            field=models.CharField(blank=True, help_text='Brand type of the eBay item', max_length=255, null=True),
        ),
    ]
