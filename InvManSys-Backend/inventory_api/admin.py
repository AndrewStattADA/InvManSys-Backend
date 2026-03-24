from django.contrib import admin
from .models import InventoryItem, Category, StockLog

admin.site.register(InventoryItem)
admin.site.register(Category)
admin.site.register(StockLog)