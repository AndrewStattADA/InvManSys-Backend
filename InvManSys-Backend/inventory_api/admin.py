from django.contrib import admin
from .models import InventoryItem, Category, StockLog, Profile

admin.site.register(InventoryItem)
admin.site.register(Category)
admin.site.register(StockLog)
admin.site.register(Profile)