from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, StockLog, Profile

class InventoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password')
        Profile.objects.get_or_create(user=self.user, defaults={'role': 'manager'})
        self.client.force_authenticate(user=self.user)
        self.url = '/api/items/'

    def test_create_item_triggers_log(self):
        """Ensure creating an item via API creates a StockLog entry."""
        data = {'name': 'Tablet', 'quantity': 10, 'price': '299.99'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StockLog.objects.filter(item_name='Tablet').exists())

    def test_update_quantity_logs_change(self):
        """Ensure changing quantity creates a log with details."""
        item = InventoryItem.objects.create(name="Mouse", quantity=50, owner=self.user)
        response = self.client.patch(f'{self.url}{item.id}/', {'quantity': 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = StockLog.objects.latest('timestamp')
        self.assertIn("Changed from 50 to 40", log.details)