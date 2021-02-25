from ebay.models import Product


def get_all_products():
    return Product.objects.all()
