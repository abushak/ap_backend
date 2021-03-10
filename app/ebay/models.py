import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from common.models import CoreModel

User = get_user_model()


class Credential(CoreModel):
    """
    Credential model
    """

    app_id = models.CharField(
        max_length=40,
        unique=True,
        blank=False,
        null=False,
        # default=None, null=False trick used here to work around with known
        # Django's `get_default` empty string that creates instance with empty-string
        # CharField avoiding any validation. So you are able get get an exception making Model.objects.create()
        default=None,
        verbose_name=_("AppID/ClientID"),
        help_text=_("AppID/ClientID that will be used to perform eBay API requests. Max. length 40 characters.")
    )
    cert_id = models.CharField(
        max_length=40,
        unique=True,
        # TODO: change on blank False, null=False, when db will ready.
        blank=True,
        null=True,
        # default=None, null=False trick used here to work around with known
        # Django's `get_default` empty string that creates instance with empty-string
        # CharField avoiding any validation. So you are able get get an exception making Model.objects.create()
        default=None,
        verbose_name=_("CertID"),
        help_text=_("CertID that will be used to perform eBay API requests. Max. length 40 characters.")
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary"),
        help_text=_("Only one credential can be primary at same time.")
    )

    query_count = models.IntegerField(
        default=0,
        verbose_name=_("QueryCount"),
        help_text=_("Count query to the ebay with these credentials per dey")
    )

    api_limit_mtime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("ApiLimitMTime"),
        help_text=_("Time when api limit was expired")
    )

    def save(self, *args, **kwargs):
        # Set `is_primary=False` for Credential with `is_primary=True` if instance is set to `is_primary=True`
        super().save(*args, **kwargs)

        if self.query_count > 4950 and self.api_limit_mtime == None:
            print('it was saved again')
            self.api_limit_mtime = datetime.datetime.now()
            self.is_primary = False
            new_primary = Credential.objects.filter(query_count__lte=4950, api_limit_mtime__isnull=True).first()
            if new_primary:
                new_primary.is_primary = True
                new_primary.save()
            else:
                date_from = datetime.datetime.now() - datetime.timedelta(days=1)

                new_primary = Credential.objects.filter(api_limit_mtime__lte=date_from).first()
                if new_primary:
                    new_primary.query_count = 0
                    new_primary.api_limit_mtime = None
                    new_primary.is_primary = True
                    new_primary.save()

        if self.is_primary is True:
            Credential.objects.exclude(pk=self.pk).update(is_primary=False)

    def __str__(self):
        return f"{self.pk}: {self.app_id}"


class Search(CoreModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Owner"),
        help_text=_("Search request initiator"),
    )
    keyword = models.CharField(
        max_length=255,
        verbose_name=_("Search keyword"),
        help_text=_("Max. length 255 characters."),
    )
    # hash field is being used to check if items have been updated from last fetching
    hash = models.CharField(
        max_length=32,
        editable=False,
        verbose_name=_("Hash"),
        help_text=_("Hash that allows to check if search results were changed from last update.")
    )
    session = models.UUIDField(
        default=None,
        null=True,
        editable=False,
        verbose_name=_("Session UUID"),
        help_text=_("Used to determine search query session.")
    )

    def __str__(self):
        return f"{self.keyword}: {self.hash}"


class Product(CoreModel):
    """
    Product model
    """

    ebay_id = models.BigIntegerField(
        verbose_name=_("eBay Item ID"),
        help_text=_("eBay Item ID from API")
    )
    title = models.CharField(
        max_length=80,
        verbose_name=_("Title"),
        help_text=_("Max. length 80 characters.")
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("May contain HTML tags.")
    )
    location = models.CharField(
        max_length=45,
        verbose_name=_("Location"),
        help_text=_("Max. length 45 characters.")
    )
    condition = models.CharField(
        max_length=32,
        verbose_name=_("Condition"),
        help_text=_("Max. length 32 characters.")
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Price"),
        help_text=_("All prices are in USD currency.")
    )
    url = models.URLField(
        max_length=300,
        verbose_name=_("URL"),
        help_text=_("Product URL on eBay.")
    )
    thumbnail_url = models.URLField(
        null=True,
        verbose_name=_("Thumbnail URL"),
        help_text=_("Product thumbnail URL on eBay.")
    )
    # hash field is being used to check if item has been updated from last fetching
    hash = models.CharField(
        max_length=32,
        editable=False,
        verbose_name=_("Hash"),
        help_text=_("Hash that allows to check if product was changed from last update.")
    )
    search = models.ForeignKey(
        Search,
        on_delete=models.CASCADE,
        verbose_name=_("Search request"),
        help_text=_("Search request keyword"),
    )
    top_rated_seller = models.BooleanField(
        default=False,
        verbose_name=_("Is top rated seller"),
        help_text=_("Determines that seller is top rated within eBay.")
    )
    buy_it_now = models.BooleanField(
        default=False,
        verbose_name=_("Is but it now"),
        help_text=_("Determines that product is available for buy it now option.")
    )
    country = models.CharField(
        max_length=2,
        null=True,
        help_text=_("ISO 3166 country code. Max. length 2 characters.")
    )

    seller = models.ForeignKey(
        'ebay.Seller',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Seller",
        help_text=_("Seller of the product")
    )


    def __str__(self):
        return f"{self.pk}: {self.ebay_id} - {self.title}"


def product_image_upload_path(instance, filename):
    return f"products/{instance.product.pk}/images/{instance.pk}_{filename}"


class ProductImage(CoreModel):
    """
    Product Image model
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        help_text=_("eBay product.")
    )
    url = models.URLField(
        null=True,
        verbose_name=_("URL"),
        help_text=_("Image URL on eBay")
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Primary"),
        help_text=_("Only one image can be primary at same time.")
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Set `is_primary=False` for ProductImage with `is_primary=True` if instance is set to `is_primary=True`
        if self.is_primary is True:
            ProductImage.objects.exclude(pk=self.pk).update(is_primary=False)

    def __str__(self):
        return f"{self.pk}:{self.product.pk}, {self.url}"


class Seller(CoreModel):
    username = models.CharField(
        max_length=255,
        verbose_name=_("Seller"),
        help_text=_("Username of the product seller")
    )
    feedback_percentage = models.DecimalField(
        null=True,
        blank=True,
        max_digits=4,
        decimal_places=1,
        verbose_name=_("Feedback Percentage"),
        help_text=_("Feedback percentage of the product seller")
    )
    feedback_score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Feedback Score"),
        help_text=_("Feedback score of the product seller")
    )


    class Meta:
        app_label = 'ebay'
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"


class BrandType(CoreModel):
    ''' Brand Type model, includes active default parameter
    '''
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Name of the Brand Type filter.")
    )

    active_default = models.BooleanField(default=False)


    def __str__(self):
        return f"Brand Type:{self.pk}:{self.name}"


    class Meta:
        app_label = 'ebay'
        verbose_name = "Brand Type"
        verbose_name_plural = "Brand Types"
