from django.db import models
from django.contrib.auth.models import User

# --- CATEGORY MODEL ---
# Groups inventory items into specific classifications (e.g., Electronics, Furniture)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True) # Unique name for the category
    description = models.TextField(blank=True) # Optional detailed description

    class Meta:
        # Corrects the default Django pluralization "Categorys" to "Categories"
        verbose_name_plural = "Categories"

    def __str__(self):
        # Returns the name of the category in the admin panel and shell
        return self.name

# --- INVENTORY ITEM MODEL ---
# The core model representing individual products in the inventory
class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    # Stock Keeping Unit (SKU) is optional but must be unique if provided
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # Links to Category; if a category is deleted, this field is set to NULL
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0) # Ensures stock never goes below zero
    low_stock_threshold = models.PositiveIntegerField(default=5) # Alert level for restocking
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True) # Automatically updated on every save
    # Tracks which user owns/manages this specific item
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')

    def __str__(self):
        # Returns the name and SKU (if available) for better identification
        if self.sku:
            return f"{self.name} (SKU: {self.sku})"
        return self.name

# --- STOCK LOG MODEL ---
# Records history of changes made to stock levels (Auditing)
class StockLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Who made the change
    item_name = models.CharField(max_length=200, null=True, blank=True) # Keeps record even if item is deleted
    item = models.ForeignKey(
        'InventoryItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    action = models.CharField(max_length=50) # e.g., "Added", "Removed", "Updated"
    details = models.TextField() # Specific notes about the change
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Dynamically builds a string for the log entry
        display_name = self.item_name or "Unknown Item"
        username = self.user.username if self.user else "System"
        return f"{username} - {self.action} on {display_name}"

# --- USER ACTION LOG MODEL ---
# Records administrative actions taken by one user upon another (e.g., permissions changes)
class UserActionLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions_performed')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_received')
    action_details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor.username} modified {self.target_user.username}"

# --- PROFILE MODEL ---
# Extends the default Django User model with custom roles
class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
    ]
    # One-to-One link to the built-in User model
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    # Assigns a specific permission level to the user
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"