from django.core.management.base import BaseCommand
from ebay.models import Credential


class Command(BaseCommand):
    help = "Create eBay credential"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_id",
            type=str,
            help="AppID/ClientID that will be used to perform eBay API requests. Max length: 40"
        )
        parser.add_argument(
            "cert_id",
            type=str,
            help="CertID that will be used to perform eBay API requests. Max length: 40"
        )

    def handle(self, *args, **options):
        credential = Credential.objects.create(app_id=options["app_id"], cert_id=options["cert_id"], is_primary=True)
        self.stdout.write(self.style.SUCCESS(f"Successfully created credential <{str(credential)}>"))
