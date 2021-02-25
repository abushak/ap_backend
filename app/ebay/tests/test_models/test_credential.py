from django.db import IntegrityError
from django.test import TestCase
from ebay.models import Credential


class CredentialTestCase(TestCase):
    """
    Credential test case
    """

    def test_credential_cant_be_created_with_empty_app_id(self):
        try:
            Credential.objects.create()
            self.fail()
        except IntegrityError:
            pass

    def test_credential_can_be_created(self):
        assert Credential.objects.count() == 0

        Credential.objects.create(app_id="test-app-id")

        assert Credential.objects.count() == 1

    def test_credential_cant_create_with_non_unique_app_id(self):
        Credential.objects.create(app_id="test-non-unique-app-id")
        try:
            Credential.objects.create(app_id="test-non-unique-app-id")
            self.fail()
        except IntegrityError:
            pass

    def test_credential_can_be_primary(self):
        credential = Credential.objects.create(app_id="test-app-id")

        assert credential.is_primary is False

        credential.is_primary = True
        credential.save()

        assert credential.is_primary is True
