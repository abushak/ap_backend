from celery import shared_task

from ebay.models import Product
from ebay.utils import generate_hash
from ebaysdk.finding import Connection as Finding


@shared_task
def call_ebay(app_id, data, per_page_limit, owner_id, search_id):
    api = Finding(appid=app_id, config_file=None)
    for n in range(per_page_limit):
        data["paginationInput"]["pageNumber"] = n + 1
        response = api.execute('findItemsAdvanced', data)
        if response.reply.ack in ['Failure', 'PartialFailure']:
            print(response.dict()['errorMessage']['error']['message'])
            continue
        save_items.apply_async((response.dict(), data["keywords"], owner_id, search_id))


@shared_task
def save_items(results, keywords, owner_id, search_id):
    items = results.get('searchResult').get('item')
    for product in items:
        create_product.apply_async((product, search_id))


@shared_task
def create_product(product: dict, search_id) -> str:
    # TODO: Create some sort of serializer/deserializer
    ebay_id = product['itemId']
    p_map = {
        "ebay_id": ebay_id,
        "title": product['title'],
        "location": product['location'],
        "condition": product['condition']['conditionDisplayName'],
        "price": product['sellingStatus']['currentPrice']['value'],
        "url": product['viewItemURL'],
        "thumbnail_url": product['galleryURL'] if 'galleryURL' in product else None,
        # ebay returns string representation so we need to convert to bool
        "top_rated_seller": True if product['sellerInfo']['topRatedSeller'] == "true" else False,
        # ebay returns string representation so we need to convert to bool
        "buy_it_now": True if product['listingInfo']['buyItNowAvailable'] == "true" else False,
        "country": product['country']
    }
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
        product.save()
        # Uncomment this part for additional product images fetching
        # gallery = single_item['PictureURL']
        # for image in gallery:
        #     ProductImage.objects.create(product=product, url=image)
    except (KeyError, Product.DoesNotExist):
        print(f"product id {product_id} doesn't exist")