from django.urls import path

from ebay.api.v1.views import EbaySearch, EbayProductDetailsView

urlpatterns = [
    path('search/', EbaySearch.as_view()),
    path('product/<id>', EbayProductDetailsView.as_view())
]
