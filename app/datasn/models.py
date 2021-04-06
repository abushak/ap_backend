from django.db import models
from django.utils.translation import gettext_lazy as _


class DatasnCategory(models.Model):
    title = models.CharField(unique=True, max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    parttype = models.CharField(max_length=7, verbose_name=_("PartType"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    engines_url = models.URLField(null=True, blank=True, verbose_name=_("EnginesUrl"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Category"
        verbose_name_plural = "Datasn Categories"


class DatasnManufacture(models.Model):
    title = models.CharField(unique=True, max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Manufacture"
        verbose_name_plural = "Datasn Manufactures"


class DatasnYear(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    make = models.ForeignKey(DatasnManufacture, on_delete=models.SET_NULL,
        related_name="year", verbose_name="Make")
    model_url = models.URLField(max_length=255, verbose_name=_("ModelUrl"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Year"
        verbose_name_plural = "Datasn Years"
