from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, Profile

class RolePermissionTests(APITestCase):
    def setUp(self):
        # 1. Create a Staff User + Profile
        self.staff = User.objects.create_user(username='staff', password='password')
        Profile.objects.get_or_create(user=self.staff, defaults={'role': 'staff'})
        
        # 2. Create a Manager User + Profile
        self.manager = User.objects.create_user(username='manager', password='password')
        Profile.objects.get_or_create(user=self.manager, defaults={'role': 'manager'})

        # 3. Create the Admin + Profile 
        self.admin = User.objects.create_superuser(username='boss', password='password', email='a@a.com')
        Profile.objects.get_or_create(user=self.admin, defaults={'role': 'admin'})

        # 4. Create a test item
        # Use the manager as owner so we can test if others can touch it
        self.item = InventoryItem.objects.create(
            name='Drill', 
            sku='H-1', 
            quantity=5, 
            owner=self.manager
        )
        self.url = f'/api/items/{self.item.id}/'

    def test_staff_cannot_delete(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_forbidden_fields(self):
        """Staff should be blocked if trying to edit Name or SKU."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.patch(self.url, {'name': 'New Name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_delete(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_bypass(self):
        """Superuser should ignore all role restrictions."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.url, {'name': 'Admin Overwrite'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)