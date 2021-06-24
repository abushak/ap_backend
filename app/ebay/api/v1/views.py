import ast
import datetime

from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ebay.api.v1.serializers import SearchIdSerializer, SearchQuerySerializer, QueryValidationErrorSerializer
from ebay.models import Search, SearchProduct
from ebay.services import EbayService, EbayServiceError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ebay.tasks import parse_partsgeek, parse_carid


class EbayProductDetailsView(APIView):
    """ Make request to the eBay and get detail information about the product
    """
    @swagger_auto_schema()
    def get(self, request, id, *args, **kwargs):
        try:
            ebay = EbayService(auto_save=True)
        except EbayServiceError as error:
            raise ValidationError({"ebay": error.__str__()})

        item_details = ebay.get_item(id)

        return Response(data=item_details, status=status.HTTP_201_CREATED)


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

        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        search = Search.objects.filter(
            keyword=request.data.get('query'),
            brand_types=request.data.get('brand_types', None),
            compatibility=request.data.get('compatibility', None),
            max_delivery_cost=request.data.get('maxDeliveryCost', False),
            created_at__gte=date_from
        ).first()
        call_ebay = False
        if not search or not SearchProduct.objects.filter(search=search).all():
            call_ebay = True
            search = Search.objects.create(
                keyword=request.data.get('query'),
                owner_id=owner_id,
                brand_types=request.data.get('brand_types', None),
                compatibility=request.data.get('compatibility', None),
                max_delivery_cost=request.data.get('maxDeliveryCost', False),
            )
        try:
            ebay = EbayService(auto_save=True)
        except EbayServiceError as error:
            raise ValidationError({"ebay": error.__str__()})
        data = {
            "search_id": search.pk
        }

        if search.conditions:
            data.update({
                'conditions': ast.literal_eval(search.conditions)
            })
        if request.data.get('query', None) and call_ebay:
            try:
                conditions = ebay.search(
                    keywords=request.data.get('query'),
                    brand_types=request.data.get('brand_types', None),
                    compatibility=request.data.get('compatibility', None),
                    max_delivery_cost=request.data.get('maxDeliveryCost', False),
                    item_filter=item_filter,
                    sort_order=request.data.get('sort_order', None),
                    owner_id=owner_id,
                    search_id=search.pk,
                    zipcode=zipcode
                )
                if conditions:
                    data.update({
                        'conditions': conditions
                    })
                    search.conditions = str(conditions)
                    search.save()
            except EbayServiceError as error:
                raise ValidationError({"query": error.__str__()})
            try:
                parse_partsgeek.apply_async((request.data.get('query'), search.pk), countdown=0.00168)
            except:
                raise ValidationError({"partsgeek": "Something went wrong during parsing PartsGeek"})
            try:
                parse_carid.apply_async((request.data.get('query'), search.pk), countdown=0.00168)
            except:
                raise ValidationError({"carid": "Something went wrong during parsing CarId"})
        return Response(data=data, status=status.HTTP_201_CREATED)
