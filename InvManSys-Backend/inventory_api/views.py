from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import InventoryItem, Category, StockLog
from .serializers import (
    InventoryItemSerializer, CategorySerializer, StockLogSerializer, 
    RegisterSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        user_role = getattr(user.profile, 'role', 'user')

        if user_role == 'user' and not user.is_superuser:
            raise PermissionDenied("You do not have permission to edit items.")

        if user_role == 'staff' and not user.is_superuser:
            sent_fields = self.request.data.keys()
            forbidden_fields = ['name', 'category', 'category_name', 'price', 'sku']
            
            if any(field in sent_fields for field in forbidden_fields):
                raise PermissionDenied("Staff can only update Quantity.")

        serializer.save()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)   

class StockLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_role = getattr(self.request.user.profile, 'role', 'user')
        if user_role in ['manager', 'staff'] or self.request.user.is_superuser:
            return StockLog.objects.all().order_by('-timestamp')
        return StockLog.objects.none()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def perform_update(self, serializer):
        target_user = self.get_object() 
        requesting_user = self.request.user 
        
        if requesting_user.is_superuser:
            serializer.save()
            return

        requesting_role = getattr(requesting_user.profile, 'role', 'user')
        target_role = getattr(target_user.profile, 'role', 'user')
        new_role = self.request.data.get('role')

        if requesting_role == 'manager':
            if target_role == 'manager' or target_user.is_superuser:
                raise PermissionDenied("Managers cannot modify Manager or Admin accounts.")
            
            if new_role == 'manager':
                raise PermissionDenied("Managers are not allowed to grant the Manager role.")

        serializer.save()