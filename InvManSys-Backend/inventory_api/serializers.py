from rest_framework import serializers
from .models import InventoryItem, Category, StockLog, UserActionLog, Profile
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# --- REGISTER SERIALIZER ---
# Handles new user account creation and password security
class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True ensures the password can be sent to the server but never read back
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_email(self, value):
        """Check if the email is already in use."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Ensures that two users cannot register with the same email address
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Creates the User instance using the manager to ensure password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Automatically creates a linked Profile with a default 'user' role
        Profile.objects.create(user=user, role='user') 
        return user

# --- CATEGORY SERIALIZER ---
# Basic serializer for classifying inventory items
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

# --- STOCK LOG SERIALIZER ---
# Converts log entries into readable strings for auditing
class StockLogSerializer(serializers.ModelSerializer):
    # StringRelatedField returns the __str__ value of the related object instead of its ID
    user = serializers.StringRelatedField(read_only=True)
    item = serializers.StringRelatedField(read_only=True) 
    
    class Meta:
        model = StockLog
        fields = ['id', 'user', 'item', 'item_name', 'action', 'details', 'timestamp']

# --- INVENTORY ITEM SERIALIZER ---
# Handles the creation and representation of inventory products
class InventoryItemSerializer(serializers.ModelSerializer):

    # Field used only for input to allow creating/assigning a category by name string
    category_name = serializers.CharField(write_only=True, required=False)
    # Field used only for output to show the category name string in the API response
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'sku', 'category', 'category_name', 'quantity'] 

    def create(self, validated_data):
        # Extract the category_name if provided
        cat_name = validated_data.pop('category_name', None)
        
        if cat_name:
            # Finds existing category or creates a new one on the fly
            category_obj, created = Category.objects.get_or_create(name=cat_name)
            validated_data['category'] = category_obj
            
        return super().create(validated_data)

# --- CUSTOM JWT SERIALIZER ---
# Customizes the JWT login response to include user roles
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the standard token data (access/refresh tokens)
        data = super().validate(attrs)
        
        # Inject the user's role into the login response body
        if hasattr(self.user, 'profile'):
            data['role'] = getattr(self.user.profile, 'role', 'user')
        else:
            # Fallback logic for superusers or users without a profile profile
            data['role'] = 'admin' if self.user.is_superuser else 'user'
            
        return data

# --- USER PROFILE SERIALIZER ---
# Used for managing user accounts and roles via a single endpoint
class UserProfileSerializer(serializers.ModelSerializer):
    # Uses dot notation to pull the 'role' field from the related Profile model
    role = serializers.CharField(source='profile.role')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

    def update(self, instance, validated_data):
        # Extract profile data from the nested structure
        profile_data = validated_data.pop('profile', None)
        
        # Manually update the core User model fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Manually update the linked Profile model's role
        if profile_data and 'role' in profile_data:
            instance.profile.role = profile_data['role']
            instance.profile.save()
            
        return instance

# --- USER ACTION LOG SERIALIZER ---
# Serializes logs for administrative changes made to users
class UserActionLogSerializer(serializers.ModelSerializer):
    # Provides human-readable names for the actor and target instead of IDs
    actor = serializers.StringRelatedField(read_only=True)
    target_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserActionLog
        fields = ['id', 'actor', 'target_user', 'action_details', 'timestamp']