from rest_framework import viewsets, permissions
from .models import InventoryItem, Category, StockLog
from .serializers import InventoryItemSerializer, CategorySerializer, StockLogSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        # Users only see their own items
        return InventoryItem.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # set the owner to the logged-in user
        serializer.save(owner=self.request.user)

class StockLogViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StockLog.objects.filter(item__owner=self.request.user)