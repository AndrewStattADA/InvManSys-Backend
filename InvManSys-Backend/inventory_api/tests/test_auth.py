from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, Profile

# --- ROLE & PERMISSION TEST SUITE ---
# Ensures that different user roles (Staff, Manager, Admin) have the correct access levels
class RolePermissionTests(APITestCase):
    def setUp(self):
        # 1. SETUP STAFF USER:
        # Create a user with 'staff' role. Based on your permissions, 
        # they should be able to view/edit but not create/delete.
        self.staff = User.objects.create_user(username='staff', password='password')
        Profile.objects.get_or_create(user=self.staff, defaults={'role': 'staff'})
        
        # 2. SETUP MANAGER USER:
        # Create a user with 'manager' role. They should have full CRUD access.
        self.manager = User.objects.create_user(username='manager', password='password')
        Profile.objects.get_or_create(user=self.manager, defaults={'role': 'manager'})

        # 3. SETUP SUPERUSER:
        # Create a Django superuser. They bypass all custom permission checks.
        self.admin = User.objects.create_superuser(username='boss', password='password', email='a@a.com')
        Profile.objects.get_or_create(user=self.admin, defaults={'role': 'admin'})

        # 4. SETUP TEST DATA:
        # Create a dummy inventory item to perform action tests against.
        self.item = InventoryItem.objects.create(
            name='Drill', 
            sku='H-1', 
            quantity=5, 
            owner=self.manager
        )
        self.url = f'/api/items/{self.item.id}/'

    def test_staff_cannot_delete(self):
        """Verify that staff members are restricted from deleting items."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        # Should return 403 Forbidden as per IsManagerOrReadOnly logic
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_forbidden_fields(self):
        """Staff should be blocked if trying to edit protected fields like Name or SKU."""
        self.client.force_authenticate(user=self.staff)
        # Attempting to change the identity of the item (Name)
        response = self.client.patch(self.url, {'name': 'New Name'})
        # Should return 403 because staff typically only manage quantities/stock levels
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_delete(self):
        """Verify that managers have permission to remove items from inventory."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(self.url)
        # Success for DELETE is usually 204 No Content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_bypass(self):
        """Superuser should ignore all role restrictions and be able to edit anything."""
        self.client.force_authenticate(user=self.admin)
        # Superuser attempts to overwrite the item name
        response = self.client.patch(self.url, {'name': 'Admin Overwrite'})
        # Should succeed regardless of the specific field restrictions applied to other roles
        self.assertEqual(response.status_code, status.HTTP_200_OK)