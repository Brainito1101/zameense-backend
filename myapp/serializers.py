from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Land, Lead, LandImage, SavedProperty, Inquiry
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    



class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("username").lower()
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")

        if not user.is_active:
            raise serializers.ValidationError("User inactive")

        return super().validate({
            "username": user.username,
            "password": password
        })


class LandImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandImage
        fields = ['id', 'image', 'created_at']


class LandSerializer(serializers.ModelSerializer):
    images = LandImageSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Land
        fields = ['id', 'title', 'location', 'lat', 'lng', 'property_type', 'price', 'area', 
                  'description', 'images', 'owner_name', 'owner_phone', 
                  'user_id', 'username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user_id', 'username']


class SavedPropertySerializer(serializers.ModelSerializer):
    land = LandSerializer(read_only=True)
    land_id = serializers.PrimaryKeyRelatedField(queryset=Land.objects.all(), write_only=True)

    class Meta:
        model = SavedProperty
        fields = ['id', 'land', 'land_id', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        land = validated_data.pop('land_id')
        return SavedProperty.objects.create(land=land, **validated_data)


class InquirySerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    land_title = serializers.CharField(source='land.title', read_only=True)

    class Meta:
        model = Inquiry
        fields = ['id', 'land', 'land_title', 'buyer', 'buyer_name', 'message', 'created_at']
        read_only_fields = ['created_at']



class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"