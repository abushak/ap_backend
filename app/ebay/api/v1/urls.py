from django.urls import path

from ebay.api.v1.views import EbaySearch

urlpatterns = [
    path('search/', EbaySearch.as_view())
]
