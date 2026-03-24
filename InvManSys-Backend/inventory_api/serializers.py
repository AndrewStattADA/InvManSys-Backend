from rest_framework import serializers
from .models import InventoryItem, Category, StockLog

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class StockLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = StockLog
        fields = ['id', 'item', 'user', 'change_amount', 'reason', 'notes', 'timestamp']

# Verify this name matches exactly:
class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'sku', 'category', 'category_name', 
            'description', 'quantity', 'low_stock_threshold', 
            'created_at', 'updated_at', 'owner'
        ]