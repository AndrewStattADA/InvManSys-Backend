from django.test import TestCase
from django.contrib.auth.models import User
from inventory_api.models import InventoryItem, Category, StockLog

# --- MODEL UNIT TESTS ---
# These tests run against a temporary database to verify model logic and relationships
class ModelTests(TestCase):
    def setUp(self):
        # Create shared resources used by multiple tests
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="Electronics")

    def test_item_creation(self):
        """Verify that an item saves correctly with a category."""
        # Create a new inventory item linked to the test user and category
        item = InventoryItem.objects.create(
            name="Laptop", 
            quantity=5, 
            category=self.category,
            owner=self.user
        )
        
        # Verify the __str__ method returns the expected name
        self.assertEqual(str(item), "Laptop")
        
        # Verify the Foreign Key relationship to Category is working correctly
        self.assertEqual(item.category.name, "Electronics")

    def test_stock_log_string_representation(self):
        """Verify the __str__ method of the StockLog."""
        # Create a log entry manually to test its display logic
        log = StockLog.objects.create(
            user=self.user,
            action="Created",
            item_name="Test Item"
        )
        
        # Check if the string representation contains the item name 
        # as defined in the StockLog model's __str__ method
        self.assertIn("Test Item", str(log))