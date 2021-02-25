from rest_framework import serializers
from ebay.models import Product, ProductImage


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


class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True)

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
