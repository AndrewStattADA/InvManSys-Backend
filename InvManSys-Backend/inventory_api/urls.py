from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, CategoryViewSet, StockLogViewSet, RegisterView, UserManagementViewSet
from . import views

# The router automatically creates the standard GET, POST, PUT, DELETE routes
router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'stock-logs', views.StockLogViewSet, basename='stocklog')
router.register(r'users', UserManagementViewSet, basename='users')
router.register(r'user-action-logs', views.UserActionLogViewSet, basename='useractionlog')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
]