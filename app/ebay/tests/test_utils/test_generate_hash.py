from django.test import TestCase
from ebay.utils import generate_hash


class GenerateHashTestCase(TestCase):
    """
    `generate_hase` test case
    """

    def test_generate_hash_defined(self):
        import ebay
        assert "generate_hash" in dir(ebay.utils) is True

    def test_generate_hash_returns_str(self):
        assert generate_hash("test") is str

    def test_generate_hash_can_generate_correct_hash(self):
        manually_generated_md5 = "098f6bcd4621d373cade4e832627b4f6"
        assert generate_hash("test") == manually_generated_md5
