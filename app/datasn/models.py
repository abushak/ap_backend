from django.db import models
from django.utils.translation import gettext_lazy as _


class DatasnCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    parttype = models.CharField(max_length=7, verbose_name=_("PartType"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    engines_url = models.URLField(max_length=1000, null=True, blank=True, verbose_name=_("EnginesUrl"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Category"
        verbose_name_plural = "Datasn Categories"


class DatasnMake(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Make"
        verbose_name_plural = "Datasn Make"


class DatasnYear(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    make = models.ManyToManyField(DatasnMake, null=True, blank=True,
        related_name="year", verbose_name="Make")
    model_url = models.CharField(max_length=1000, verbose_name=_("ModelUrl"))


    class Meta:
        app_label = "datasn"
        verbose_name = "Datasn Year"
        verbose_name_plural = "Datasn Years"
        unique_together = ('title', 'model_url',)
