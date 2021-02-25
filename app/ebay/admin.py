from django.contrib import admin

from ebay.models import Credential, Product, ProductImage


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
