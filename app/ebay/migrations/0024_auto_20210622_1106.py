# Generated by Django 3.1.4 on 2021-06-22 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebay', '0023_auto_20210622_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='condition',
            field=models.CharField(help_text='Max. length 32 characters.', max_length=32, null=True, verbose_name='Condition'),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(help_text='Max. length 80 characters.', max_length=255, verbose_name='Title'),
        ),
    ]
