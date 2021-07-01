from celery import shared_task
from ebay.models import Product, ProductImage, Credential, Seller, SearchProduct, Search, Vendor, SearchIndex
from ebay.utils import generate_hash

from .client import AutoCorrectBrowseAPI
from .parsers.car_parts_parser import CarParts
from .parsers.carid_parser import CarId
from .parsers.partsgeek_parser import PartsGeek


def get_vendor(name):
    vendor, created = Vendor.objects.update_or_create(
        name=name,
    )
    return vendor


@shared_task
def parse_car_parts(keywords, search_id):
    url = 'https://www.carparts.com/search?q='
    car_parts = CarParts()
    items = car_parts.find_goods(url, keywords.strip())
    images = None
    ebay_id = None
    vendor = get_vendor("carparts.com")
    if items:
        search_index = SearchIndex.objects.filter(search=search_id).first()
        search_index.vendors.add(vendor)
    for product in items:
        try:
            int(product.get('price', None))
            price = product.get('price', None)
        except ValueError:
            price = 0
        create_product.apply_async((
            {
                "ebay_id": None,
                "title": product.get('title', None),
                "location": "",
                "description": getattr(product, 'shortDescription', None),
                "condition": getattr(product, 'condition', None),
                "price": price,
                "url": product.get('url', None),
                "thumbnail_url": product.get('thumbnail_url', None),
                "country": getattr(product, 'itemLocation', None),
                "brand": product.get('brand', None),
                "part_number": product.get('part_number', None),
                "vendor_id": vendor.pk
            }, ebay_id, images, search_id, None))


@shared_task
def parse_partsgeek(keywords, search_id):
    url = 'https://www.partsgeek.com/ss/?i=1&ssq='
    partsgeek = PartsGeek()
    items = partsgeek.find_goods(url, keywords)
    images = None
    ebay_id = None
    vendor = get_vendor("partsgeek.com")
    if items:
        search_index = SearchIndex.objects.filter(search=search_id).first()
        search_index.vendors.add(vendor)
    for product in items:
        create_product.apply_async((
            {
                "ebay_id": None,
                "title": product.get('title', None),
                "location": "",
                "description": getattr(product, 'shortDescription', None),
                "condition": getattr(product, 'condition', None),
                "price": product.get('price', None),
                "url": product.get('url', None),
                "thumbnail_url": product.get('thumbnail_url', None),
                "country": getattr(product, 'itemLocation', None),
                "brand": product.get('brand', None),
                "part_number": product.get('part_number', None),
                "vendor_id": vendor.pk
            }, ebay_id, images, search_id, None))


@shared_task
def parse_carid(keywords, search_id):
    url = 'https://www.carid.com/'
    carid = CarId()
    items = carid.find_goods(url, keywords)
    images = None
    ebay_id = None
    vendor = get_vendor("carid.com")
    if items:
        search_index = SearchIndex.objects.filter(search=search_id).first()
        search_index.vendors.add(vendor)
    for product in items:
        create_product.apply_async((
            {
                "ebay_id": None,
                "title": product.get('title', None),
                "location": "",
                "description": getattr(product, 'shortDescription', None),
                "condition": getattr(product, 'condition', None),
                "price": product.get('price', None),
                "url": product.get('url', None),
                "thumbnail_url": product.get('thumbnail_url', None),
                "country": getattr(product, 'itemLocation', None),
                "brand": product.get('brand', None),
                "part_number": product.get('part_number', None),
                "vendor_id": vendor.pk
            }, ebay_id, images, search_id, None))


@shared_task
def call_ebay(app_id, cert_id, browse_api_parameters, data, per_page_limit, pages_limit, owner_id, search_id):
    vendor = get_vendor("ebay.com")
    api = AutoCorrectBrowseAPI(app_id, cert_id, **browse_api_parameters)
    query_counter = 2
    for n in range(pages_limit):
        data[0]["offset"] = data[0]["limit"] * n
        try:
            response = api.execute('search', data)
            query_counter += 1
        except Exception as err:
            print(err)
            continue

        if not len(response):
            continue
        search_index = SearchIndex.objects.filter(search=search_id).first()
        search_index.vendors.add(vendor)
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
            location = location[:-2]

            images = None
            if getattr(product, 'additionalImages', None):
                images = [image.imageUrl for image in product.additionalImages]

            seller = None
            if getattr(product, 'seller') and product.seller.username:
                seller = Seller.objects.update_or_create(username=product.seller.username, defaults={**{
                    'feedback_percentage': product.seller.feedbackPercentage,
                    'feedback_score': product.seller.feedbackScore
                }})

            create_product.apply_async((
                {
                    "ebay_id": ebay_id,
                    "title": getattr(product, 'title', None),
                    "location": location,
                    "description": getattr(product, 'shortDescription', None),
                    "condition": getattr(product, 'condition', None),
                    "price": product.price.value if getattr(product, 'price', None) else None,
                    "url": product.itemAffiliateWebUrl \
                        if getattr(product, 'itemAffiliateWebUrl', None) else product.itemWebUrl,
                    "thumbnail_url": product.thumbnailImages[0].imageUrl \
                        if getattr(product, 'thumbnailImages', None) else None,
                    "vendor_id": vendor.pk,
                    # TODO: drop it if will not necessary
                    # ebay returns string representation so we need to convert to bool
                    # "top_rated_seller": True if product['sellerInfo']['topRatedSeller'] == "true" else False,
                    # ebay returns string representation so we need to convert to bool
                    # "buy_it_now": True if product['listingInfo']['buyItNowAvailable'] == "true" else False,
                    "country": product.itemLocation.country if getattr(product, 'itemLocation', None) \
                                                               and getattr(product.itemLocation, 'country',
                                                                           None) else None,
                }, ebay_id, images, search_id, seller[0].id if seller else None))
    active_credential = Credential.objects.get(app_id=app_id)
    active_credential.query_count = active_credential.query_count + query_counter
    active_credential.save()


@shared_task
def create_product(p_map, ebay_id, images, search_id, seller_id) -> str:
    if seller_id:
        p_map["seller"] = Seller.objects.get(id=seller_id)
    hash = generate_hash(str(p_map))

    # TODO: Move product hash checking before single item fetching to avoid unnecessary requests
    product, created = Product.objects.update_or_create(
        ebay_id=ebay_id,
        hash=hash,
        defaults={**p_map}
    )
    if product and search_id and Search.objects.filter(id=search_id).first():
        search_product = SearchProduct.objects.create(
            product=product, search=Search.objects.filter(id=search_id).first()
        )

    # Currently disable product details fetching to respect eBay calls limit (3000 requests per 5 seconds).
    # fetch_product_details.apply_async((product.pk,))
    if images:
        # check images which already were saved
        product_images = [image.url for image in ProductImage.objects.filter(product=product).all()]
        new_images = list(set(images) - set(product_images))
        if new_images:
            for image in new_images:
                ProductImage.objects.create(product=product, url=image)

    return f"{product.pk}:{product.ebay_id}:{product.hash}"


@shared_task
def fetch_product_details(product_id):
    from ebay.services import EbayService
    es = EbayService()
    try:
        product = Product.objects.get(pk=product_id)
        single_item = es.get_item(item_id=product.ebay_id)['Item']
        product.top_rated_seller = True if single_item['Seller']['TopRatedSeller'] == "true" else False
        product.buy_it_now = True if int(single_item['Quantity']) > 0 else False
        # for name_value_dict in single_item["ItemSpecifics"]["NameValueList"]:
        #     if name_value_dict["Name"] == "Brand":
        #         product.brand_type = name_value_dict["Brand"]
        #         break
        product.save()
        # Uncomment this part for additional product images fetching
        # gallery = single_item['PictureURL']
        # for image in gallery:
        #     ProductImage.objects.create(product=product, url=image)
    except (KeyError, Product.DoesNotExist):
        print(f"product id {product_id} doesn't exist")
