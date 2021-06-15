from django.contrib import admin

from ebay.models import Credential, Product, ProductImage, BrandType, SearchIndex


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    """
    Credential admin
    """

    list_display = ('__str__', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('app_id',)


class ProductImageAdmin(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin
    """

    list_display = ('__str__', 'hash', 'updated_at', 'created_at')
    list_filter = ('condition',)
    search_fields = ('ebay_id', 'title', 'hash',)
    inlines = (ProductImageAdmin,)


@admin.register(BrandType)
class BrandType(admin.ModelAdmin):
    """ Brand Type admin
    """
    list_display = ('id', 'name', 'active_default')


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    """
    Search index admin
    """
    pass

