from celery import shared_task

from ebay.models import Product
from ebay.utils import generate_hash
from ebaysdk.finding import Connection as Finding
from browseapi.containers import ItemSummary
from browseapi import BrowseAPI


@shared_task
def call_ebay(app_id, cert_id, browse_api_parameters, data, per_page_limit, owner_id, search_id):
    api = BrowseAPI(app_id, cert_id, **browse_api_parameters)
    for n in range(per_page_limit):
        data[0]["offset"] = data[0]["limit"] * (n + 1)
        try:
            response = api.execute('search', data)
        except Exception as err:
            print(err)
            continue

        if not len(response):
            continue

        for product in response[0].itemSummaries:
            # TODO: Create some sort of serializer/deserializer
            # itemId return string in format "v1|id|0", make sure that in other versions of the api the same
            try:
                ebay_id = product.itemId.split('|')[1]
            except Exception as err:
                print(err)
                continue

            location = ''
            for key in 'addressLine1', 'addressLine2', 'city', 'country', 'county', 'stateOrProvince', 'postalCode':
                if getattr(product.itemLocation, key, None):
                    location += getattr(product.itemLocation, key)
                    location += ', '
            create_product.apply_async((
            {
                "ebay_id": ebay_id,
                "title": product.title,
                "location": location,
                "condition": product.condition,
                "price": product.price.value if product.price else None,
                "url": product.itemAffiliateWebUrl if product.itemAffiliateWebUrl else product.itemWebUrl,
                "thumbnail_url": product.thumbnailImages[0].imageUrl if product.thumbnailImages else None,
                # TODO: drop it if will not necessary
                # ebay returns string representation so we need to convert to bool
                # "top_rated_seller": True if product['sellerInfo']['topRatedSeller'] == "true" else False,
                # ebay returns string representation so we need to convert to bool
                # "buy_it_now": True if product['listingInfo']['buyItNowAvailable'] == "true" else False,
                "country": product.itemLocation.country \
                    if product.itemLocation and product.itemLocation.country else None,
            }, ebay_id, search_id))


@shared_task
def create_product(p_map, ebay_id, search_id) -> str:
    hash = generate_hash(str(p_map))
    p_map["search_id"] = search_id
    # TODO: Move product hash checking before single item fetching to avoid unnecessary requests
    product, created = Product.objects.update_or_create(ebay_id=ebay_id, hash=hash, defaults={**p_map})
    # Currently disable product details fetching to respect eBay calls limit (3000 requests per 5 seconds).
    # fetch_product_details.apply_async((product.pk,))
    return f"{product.pk}:{product.ebay_id}:{product.hash}"


@shared_task
def fetch_product_details(product_id):
    from ebay.services import EbayService
    es = EbayService()
    try:
        product = Product.objects.get(pk=product_id)
        single_item = es.get_item(item_id=product.ebay_id)['Item']
        product.description = single_item['Description']
        product.top_rated_seller = True if single_item['sellerInfo']['topRatedSeller'] == "true" else False
        product.buy_it_now = True if single_item['buyItNowAvailable'] == "true" else False
        product.save()
        # Uncomment this part for additional product images fetching
        # gallery = single_item['PictureURL']
        # for image in gallery:
        #     ProductImage.objects.create(product=product, url=image)
    except (KeyError, Product.DoesNotExist):
        print(f"product id {product_id} doesn't exist")