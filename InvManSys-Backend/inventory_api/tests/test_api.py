from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, StockLog, Profile

# --- INVENTORY API TEST SUITE ---
# Uses APITestCase to simulate API requests and verify database side-effects
class InventoryAPITests(APITestCase):
    def setUp(self):
        # Create a test user and ensure they have a 'manager' role for full access
        self.user = User.objects.create_user(username='admin', password='password')
        Profile.objects.get_or_create(user=self.user, defaults={'role': 'manager'})
        
        # Authenticate the client so all requests in this class appear to come from this user
        self.client.force_authenticate(user=self.user)
        self.url = '/api/items/'

    def test_create_item_triggers_log(self):
        """Ensure creating an item via API creates a StockLog entry."""
        # Define sample payload for a new inventory item
        data = {'name': 'Tablet', 'quantity': 10, 'price': '299.99'}
        
        # Perform the POST request to the item creation endpoint
        response = self.client.post(self.url, data)
        
        # Verify the item was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that an automated audit log was generated for this specific action
        self.assertTrue(StockLog.objects.filter(item_name='Tablet').exists())

    def test_update_quantity_logs_change(self):
        """Ensure changing quantity creates a log with details."""
        # Setup: Manually create an item to be updated
        item = InventoryItem.objects.create(name="Mouse", quantity=50, owner=self.user)
        
        # Perform a partial update (PATCH) to change only the quantity field
        response = self.client.patch(f'{self.url}{item.id}/', {'quantity': 40})
        
        # Verify the update request was accepted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Retrieve the most recent log to verify it captured the quantity difference
        log = StockLog.objects.latest('timestamp')
        self.assertIn("Changed from 50 to 40", log.details)