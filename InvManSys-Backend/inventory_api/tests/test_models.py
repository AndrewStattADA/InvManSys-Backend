from django.test import TestCase
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, Category, StockLog

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="Electronics")

    def test_item_creation(self):
        """Verify that an item saves correctly with a category."""
        item = InventoryItem.objects.create(
            name="Laptop", 
            quantity=5, 
            category=self.category,
            owner=self.user
        )
        self.assertEqual(str(item), "Laptop")
        self.assertEqual(item.category.name, "Electronics")

    def test_stock_log_string_representation(self):
        """Verify the __str__ method of the StockLog."""
        log = StockLog.objects.create(
            user=self.user,
            action="Created",
            item_name="Test Item"
        )
        self.assertIn("Test Item", str(log))