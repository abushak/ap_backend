from rest_framework import serializers
from ebay.models import Product, ProductImage, BrandType


class ProductImageSerializer(serializers.ModelSerializer):
    """
    `ProductImage` model serializer
    """

    class Meta:
        model = ProductImage
        exclude = ('product',)


class ProductSerializer(serializers.ModelSerializer):
    """
    `Product` model serializer
    """

    product_images = ProductImageSerializer(many=True, source='productimage_set')

    class Meta:
        model = Product
        fields = '__all__'


class SearchIdSerializer(serializers.Serializer):
    search_id = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class CompatibilitySerializer(serializers.Serializer):
    year = serializers.CharField(required=False)
    make = serializers.CharField(required=False)
    model = serializers.CharField(required=False)


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    brand_types = serializers.ListField(
        required=False,
        child=serializers.IntegerField()
    )
    compatibility = CompatibilitySerializer(required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class QueryValidationErrorSerializer(serializers.Serializer):
    query = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
