from django.core.management.base import BaseCommand
from ebay.models import Credential
from ebaysdk.finding import Connection as Finding
from browseapi import BrowseAPI
from django.conf import settings
from json import dumps

app_id = "IhorKash-AutoPart-PRD-3c8ec7f0e-9089209e"
cert_id = "PRD-c8ec7f0e26cf-d7df-4cd6-aac6-775c"

class Command(BaseCommand):
    help = "Test eBay call"

    credential: Credential
    api: Finding
    per_page_limit = 100
    pages_limit = 100

    def handle(self, *args, **options):
        self.api = BrowseAPI(app_id, cert_id)
        self.call_ebay()

        # self.credential = Credential.objects.first()
        # self.api = Finding(appid=self.credential.app_id, config_file=None)
        # self.call_ebay()

    def call_ebay(self):
        request_data = {
            'keywords': ['VW Jetta 2019 front hood'],
            'categoryId': settings.EBAY_SEARCH_CATEGORY,
            'affiliate': {
                'networkId': 9,
                'trackingId': 5338731488
            },
            'itemFilter': [
                {
                    "name": "BuyItNowAvailable",
                    "value": "true"
                }
            ],
            'paginationInput': {
                'entriesPerPage': self.per_page_limit,
                'pageNumber': 1
            },
            'domainFilter': '',
            'outputSelector': ['AspectHistogram', 'CategoryHistogram', 'ConditionHistogram', 'SellerInfo']
        }

        respone = self.api.execute('search', [{keyword: request_data[keyword]} for keyword in request_data])
        # response = self.api.execute('findItemsAdvanced', request_data)

        # Prints total found
        # print(response.dict()['paginationOutput']['totalEntries'])

        # Prints request body
        # print(response.request.body)

        # Write response to file
        with open("response.json", 'w') as of:
            of.write(dumps(response.dict()))
