# Generated by Django 3.1.4 on 2021-06-15 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ebay', '0021_auto_20210615_0911'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchindex',
            options={'verbose_name': 'Search index', 'verbose_name_plural': 'Search indexes'},
        ),
        migrations.AddField(
            model_name='searchindex',
            name='search',
            field=models.ForeignKey(blank=True, help_text='Search id', null=True, on_delete=django.db.models.deletion.CASCADE, to='ebay.search'),
        ),
    ]
