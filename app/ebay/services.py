from ebaysdk.exception import ConnectionError  # pylint: disable=redefined-builtin
from ebay.models import Credential, BrandType
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ebay.tasks import call_ebay
from django.conf import settings
from .client import AutoCorrectBrowseAPI
from ebaysdk.finding import Connection as Finding


class EbayService:
    """
    EbayService
    """
    app_id: str
    cert_id: str
    auto_save: bool
    per_page_limit = 100
    pages_limit = 3

    def __init__(self, auto_save=True):
        """
        :param auto_save:
        """
        self.auto_save = auto_save
        self.app_id, self.cert_id = self.check_credentials()

    @staticmethod
    def check_credentials():
        """
        :return:
        """
        try:
            credentials = Credential.objects.get(is_primary=True)
            if not credentials.cert_id:
                raise EbayServiceError(_("At least one primary Credential required"))
            return credentials.app_id, credentials.cert_id
        except (KeyError, Credential.DoesNotExist):
            raise EbayServiceError(_("At least one primary Credential required"))

    def search(self, keywords, brand_types, compatibility, search_id,
               owner_id=None, item_filter=None, sort_order=None, zipcode=None):
        """
        :param keywords:
        :param per_page:
        :param page:
        :param owner:
        :param item_filter: doesn't use in browse API. TODO: delete in feature
        :return:
        """
        try:
            brand_types_filter = ''
            if len(brand_types):
                brand_types_filter = "{"
                for id in brand_types:
                    if not isinstance(id, int) and not BrandType.objects.filter(id=id).first():
                        raise ValidationError({"brand_types": _("Brand types should be list of the ids")})
                    brand_type = BrandType.objects.filter(id=id).first()
                    brand_types_filter += f"{brand_type.name}|"
                brand_types_filter = brand_types_filter[:-1] + "}"

            compatibility_filter = ''
            if compatibility:
                for key, value in dict(compatibility).items():
                    compatibility_filter += f'{key.capitalize()}:{value};'

            data = [{
                'q': keywords,
                'limit': self.per_page_limit,
                'category_ids': settings.EBAY_SEARCH_CATEGORY,
                'fieldgroups': 'ASPECT_REFINEMENTS,CATEGORY_REFINEMENTS,' +
                               'CONDITION_REFINEMENTS,BUYING_OPTION_REFINEMENTS,EXTENDED,MATCHING_ITEMS',
                'aspect_filter': f'categoryId:{settings.EBAY_SEARCH_CATEGORY}, Brand Type: {brand_types_filter}' \
                    if brand_types_filter else f'categoryId:{settings.EBAY_SEARCH_CATEGORY}',
            }]

            if compatibility_filter:
                data[0]['compatibility_filter'] = compatibility_filter[:-1]

            if sort_order is not None:
                data[0]['sort'] = sort_order

            browse_api_parameters = {
                'partner_id': "5338731488",
            }

            if zipcode is not None:
                browse_api_parameters['zip_code'] = zipcode

            api = AutoCorrectBrowseAPI(self.app_id, self.cert_id, **browse_api_parameters)
            pagination_totals = self.pagination_totals(api, data=data)
            if pagination_totals < self.per_page_limit:
                self.per_page_limit = pagination_totals

            call_ebay.apply_async(
                (self.app_id, self.cert_id, browse_api_parameters, data, self.per_page_limit, owner_id, search_id),
                countdown=0.00167
            )

            return True
        except ConnectionError as error:
            raise EbayServiceError(error)

    def pagination_totals(self, api, data):
        response = api.execute('search', data)
        max_response_pages = int(response[0].total)
        if max_response_pages == 0:
            raise EbayServiceError("No products found using provided query")
        return max_response_pages

    def get_item(self, item_id):
        """
        :param item_id:
        :return:
        """
        from ebaysdk.shopping import Connection as Shopping
        try:
            api = Shopping(appid=self.app_id, config_file=None)
            response = api.execute('GetSingleItem', {
                'ItemID': item_id,
                'IncludeSelector': 'Details,ItemSpecifics'
            })
            if response.reply.Ack in ['Failure', 'PartialFailure']:
                raise EbayServiceError(response.dict()['errorMessage']['error']['message'])
            return response.dict()
        except ConnectionError as error:
            raise EbayServiceError(error)


class EbayServiceError(Exception):
    """
    EbayServiceError
    """

    def __init__(self, msg):
        """
        :param msg:
        """
        super(EbayServiceError, self).__init__(msg)
        self.message = msg

    def __str__(self):
        """
        :return:
        """
        return str(self.message)
