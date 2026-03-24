from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, CategoryViewSet, StockLogViewSet

# The router automatically creates the standard GET, POST, PUT, DELETE routes
router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'logs', StockLogViewSet, basename='stocklog')

urlpatterns = [
    path('', include(router.urls)),
]