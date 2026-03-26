from rest_framework import serializers
from .models import InventoryItem, Category, StockLog, Profile
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # EVERY new user starts as a 'user' (read-only)
        Profile.objects.create(user=user, role='user') 
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class StockLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = StockLog
        fields = ['id', 'item', 'user', 'change_amount', 'reason', 'notes', 'timestamp']

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
        # This adds the role from the Profile model to the login response
        data['role'] = self.user.profile.role
        return data

