import os
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import InventoryItem, Category, StockLog, UserActionLog
from .serializers import InventoryItemSerializer, CategorySerializer, StockLogSerializer, RegisterSerializer, MyTokenObtainPairSerializer, UserProfileSerializer, UserActionLogSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        user_role = getattr(user.profile, 'role', 'user')

        if user_role in ['user', 'staff'] and not user.is_superuser:
            raise PermissionDenied("Only Managers and Admins can delete items.")

        item_name = instance.name
        
        if instance.sku:
            details_str = f"Deleted: {item_name} (SKU: {instance.sku})"
        else:
            details_str = f"Deleted: {item_name}"

        StockLog.objects.create(
            user=user,
            item=None, 
            item_name=item_name, 
            action="Item Deleted",
            details=details_str
        )

        instance.delete()

    def perform_update(self, serializer):
        user = self.request.user
        user_role = getattr(user.profile, 'role', 'user')
        item = self.get_object()
        old_quantity = item.quantity

        if user_role == 'user' and not user.is_superuser:
            raise PermissionDenied("You do not have permission to edit items.")

        if user_role == 'staff' and not user.is_superuser:
            sent_fields = self.request.data.keys()
            forbidden_fields = ['name', 'category', 'category_name', 'price', 'sku']
            if any(field in sent_fields for field in forbidden_fields):
                raise PermissionDenied("Staff can only update Quantity.")

        updated_item = serializer.save()

        new_quantity = updated_item.quantity
        if old_quantity != new_quantity:
            StockLog.objects.create(
                user=user,
                item=updated_item,
                item_name=updated_item.name,
                action="Quantity Updated",
                details=f"Changed from {old_quantity} to {new_quantity}"
            )

    def perform_create(self, serializer):
        item = serializer.save(owner=self.request.user)
        StockLog.objects.create(
            user=self.request.user,
            item=item,
            item_name=item.name, 
            action="Item Created",
            details=f"Initial quantity: {item.quantity}"
        )

class StockLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user.profile, 'role', 'user')
        # Only Staff, Managers, and Admins can see the logs
        if user_role in ['manager', 'staff'] or user.is_superuser:
            return StockLog.objects.all().order_by('-timestamp')
        return StockLog.objects.none()

class UserActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActionLog.objects.all().order_by('-timestamp')
    serializer_class = UserActionLogSerializer  
    permission_classes = [permissions.IsAuthenticated]

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
        
        old_role = getattr(target_user.profile, 'role', 'user')
        new_role = self.request.data.get('role', old_role)
        
        if requesting_user.is_superuser:
            serializer.save()

            if old_role != new_role:
                UserActionLog.objects.create(
                    actor=requesting_user,
                    target_user=target_user,
                    action_details=f"Admin changed role from {old_role} to {new_role}"
                )
            return

        requesting_role = getattr(requesting_user.profile, 'role', 'user')
        target_role = getattr(target_user.profile, 'role', 'user')

        if requesting_role == 'manager':
            if target_role == 'manager' or target_user.is_superuser:
                raise PermissionDenied("Managers cannot modify Manager or Admin accounts.")
            if new_role == 'manager':
                raise PermissionDenied("Managers are not allowed to grant the Manager role.")

        serializer.save()

        if old_role != new_role:
            UserActionLog.objects.create(
                actor=requesting_user,
                target_user=target_user,
                action_details=f"Manager changed role from {old_role} to {new_role}"
            )   

# builtin framework create a tempory token that lasts xyz thats usable to reset the password 
# --- Password Reset Request ---
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    user = User.objects.filter(email=email).first()
    
    if user:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Get values from settings.py or environment
        frontend_url = os.environ.get('FRONTEND_URL', "https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev")
        reset_link = f"{frontend_url}/reset-password/{uid}/{token}"
        
        message = Mail(
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'mydogisollie@gmail.com'),
            to_emails=email,
            subject='Password Reset Request - Inventory System',
            html_content=f'''
                <h3>Reset Your Password</h3>
                <p>Click the link below to set a new password:</p>
                <a href="{reset_link}">{reset_link}</a>
            '''
        )
        try:
            # Get API key from settings or environment
            api_key = getattr(settings, 'SENDGRID_API_KEY', os.environ.get('SENDGRID_API_KEY'))
            sg = SendGridAPIClient(api_key)
            sg.send(message)
        except Exception as e:
            print(f"SendGrid Error: {str(e)}") 
            return Response({"error": f"Failed to send email: {str(e)}"}, status=500)
            
    return Response({"message": "If an account exists with this email, a reset link has been sent."})

#  Password Reset Confirmation 
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Invalid user identification."}, status=400)

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset successfully. You can now login."})
    else:
        return Response({"error": "Invalid or expired token."}, status=400)