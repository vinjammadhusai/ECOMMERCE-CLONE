from django.test import TestCase
from django.urls import reverse
from .models import Product


class ProductTests(TestCase):
    def setUp(self):
        Product.objects.create(
            name='Headphones',
            description='Wireless headphones',
            price='1500.00',
            quantity=10,
            category='Electronics',
        )

    def test_product_list_loads(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_name_is_displayed(self):
        response = self.client.get(reverse('product_list'))
        self.assertContains(response, 'Headphones')