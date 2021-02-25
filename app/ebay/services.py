from ebaysdk.exception import ConnectionError  # pylint: disable=redefined-builtin
from ebay.models import Credential
from django.utils.translation import gettext_lazy as _
from ebay.tasks import call_ebay
from django.conf import settings

from ebaysdk.finding import Connection as Finding


class EbayService:
    """
    EbayService
    """
    app_id: str
    auto_save: bool
    per_page_limit = 100
    pages_limit = 3

    def __init__(self, auto_save=True):
        """
        :param auto_save:
        """
        self.auto_save = auto_save
        self.app_id = self.check_credentials()

    @staticmethod
    def check_credentials():
        """
        :return:
        """
        try:
            credentials = Credential.objects.get(is_primary=True)
            return credentials.app_id
        except (KeyError, Credential.DoesNotExist):
            raise EbayServiceError(_("At least one primary Credential required"))

    def search(self, keywords, search_id, owner_id=None, item_filter=None, sort_order=None, zipcode=None):
        """
        :param keywords:
        :param per_page:
        :param page:
        :param owner:
        :return:
        """
        try:
            api = Finding(appid=self.app_id, config_file=None)
            data = {
                'keywords': keywords,
                'categoryId': settings.EBAY_SEARCH_CATEGORIES,
                'paginationInput': {
                    'entriesPerPage': 100,
                    'pageNumber': 1
                },
                'affiliate': {
                    'networkId': 9,
                    'trackingId': 5338731488
                },
                'domainFilter': '',
                'sortOrder': 'BestMatch',
                'outputSelector': ['AspectHistogram', 'CategoryHistogram', 'ConditionHistogram', 'SellerInfo'],
            }
            if item_filter is not None:
                data['itemFilter'] = item_filter
            if sort_order is not None:
                data['sortOrder'] = sort_order
            if zipcode is not None:
                data['buyerPostalCode'] = zipcode
            pagination_totals = self.pagination_totals(data=data)
            if pagination_totals < self.per_page_limit:
                self.per_page_limit = pagination_totals
            call_ebay.apply_async((self.app_id, data, self.per_page_limit, owner_id, search_id), countdown=0.00167)

            return True
        except ConnectionError as error:
            raise EbayServiceError(error)

    def pagination_totals(self, data):
        api = Finding(appid=self.app_id, config_file=None)
        response = api.execute('findItemsAdvanced', data)
        if response.reply.ack in ['Failure', 'PartialFailure']:
            raise EbayServiceError(response.dict()['errorMessage']['error']['message'])
        max_response_pages = int(response.dict()["paginationOutput"]["totalPages"])
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
                'IncludeSelector': 'Description'
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
