from rest_framework import viewsets, permissions, generics 
from rest_framework.permissions import AllowAny
from .models import InventoryItem, Category, StockLog
from django.contrib.auth.models import User
from .serializers import InventoryItemSerializer, CategorySerializer, StockLogSerializer, RegisterSerializer, MyTokenObtainPairSerializer
from .permissions import IsManagerOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrReadOnly]

    def perform_update(self, serializer):
        user_role = self.request.user.profile.role
        
        # Staff Role: Only allow quantity updates
        if user_role == 'staff' and not self.request.user.is_superuser:
            # Checks if they tried to change name or category
            if 'name' in self.request.data or 'category_name' in self.request.data:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Staff can only update the Quantity.")
        
        serializer.save()

class StockLogViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StockLog.objects.filter(item__owner=self.request.user)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer