from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ebay.api.v1.serializers import SearchIdSerializer, SearchQuerySerializer, QueryValidationErrorSerializer
from ebay.models import Search
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ebay.services import EbayService, EbayServiceError
from django.utils.translation import gettext_lazy as _


class EbaySearch(APIView):

    """
    Starts eBay search on background and returns search_id for further usage at GraphQL subscriptions.
    """
    search_id_response = openapi.Response("search_id for further usage at GraphQL subscriptions", SearchIdSerializer)
    validation_error_response = openapi.Response("Validation error", QueryValidationErrorSerializer)

    @swagger_auto_schema(request_body=SearchQuerySerializer, responses={201: search_id_response, 400: validation_error_response})
    def post(self, request):
        if "query" not in request.data:
            raise ValidationError({"query": _("query field is missing")})
        if not request.data.get("query"):
            raise ValidationError({"query": _("query field is empty")})

        item_filter = request.data.get("item_filter", None)
        zipcode = None
        if request.data.get("nearby") is not None:
            nearby = request.data.get("nearby")
            zipcode = nearby.get("zipcode", None)
            distance = nearby.get("distance", None)

            if zipcode is None or not zipcode:
                raise ValidationError({"zipcode": _("zipcode field required")})
            if distance is None or not distance:
                raise ValidationError({"distance": _("distance field required")})

            item_filter = {
                "name": "MaxDistance",
                "value": distance
            }

        owner_id = None if request.user.is_anonymous else request.user.pk
        search = Search.objects.create(keyword=request.data.get('query'), owner_id=owner_id)
        try:
            ebay = EbayService(auto_save=True)
        except EbayServiceError as error:
            raise ValidationError({"ebay": error.__str__()})

        if request.data.get('query', None):
            try:
                ebay.search(
                    keywords=request.data.get('query'),
                    item_filter=item_filter,
                    sort_order=request.data.get('sort_order', None),
                    owner_id=owner_id,
                    search_id=search.pk,
                    zipcode=zipcode
                )
            except EbayServiceError as error:
                raise ValidationError({"query": error.__str__()})

        return Response(data={"search_id": search.pk}, status=status.HTTP_201_CREATED)
