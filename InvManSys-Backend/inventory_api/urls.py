from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, CategoryViewSet, StockLogViewSet, RegisterView, UserManagementViewSet, UserActionLogViewSet, request_password_reset, reset_password_confirm
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'stock-logs', views.StockLogViewSet, basename='stocklog')
router.register(r'users', UserManagementViewSet, basename='users')
router.register(r'user-action-logs', views.UserActionLogViewSet, basename='useractionlog')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('password-reset/', request_password_reset, name='password_reset'),
    path('password-reset-confirm/', reset_password_confirm, name='password_reset_confirm'),
]