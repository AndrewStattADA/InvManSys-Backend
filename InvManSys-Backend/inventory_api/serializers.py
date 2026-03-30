from rest_framework import serializers
from .models import InventoryItem, Category, StockLog, UserActionLog, Profile
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_email(self, value):
        """Check if the email is already in use."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        Profile.objects.create(user=user, role='user') 
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class StockLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    item = serializers.StringRelatedField(read_only=True) 
    
    class Meta:
        model = StockLog
        fields = ['id', 'user', 'item', 'item_name', 'action', 'details', 'timestamp']

class InventoryItemSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(write_only=True, required=False)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'sku', 'category', 'category_name', 'quantity'] 

    def create(self, validated_data):
        cat_name = validated_data.pop('category_name', None)
        
        if cat_name:
            category_obj, created = Category.objects.get_or_create(name=cat_name)
            validated_data['category'] = category_obj
            
        return super().create(validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # get the role or default to 'user' if profile is missing
        data['role'] = getattr(self.user.profile, 'role', 'user')
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update User fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update Profile role
        if profile_data and 'role' in profile_data:
            instance.profile.role = profile_data['role']
            instance.profile.save()
            
        return instance

class UserActionLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)
    target_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserActionLog
        fields = ['id', 'actor', 'target_user', 'action_details', 'timestamp']