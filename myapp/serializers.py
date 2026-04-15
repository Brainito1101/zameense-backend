from rest_framework import serializers
from .models import Land, Lead, LandImage, SavedProperty, Inquiry


class LandImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandImage
        fields = ['id', 'land', 'image', 'created_at']


class LandSerializer(serializers.ModelSerializer):
    images = LandImageSerializer(many=True, read_only=True)

    class Meta:
        model = Land
        fields = [
            'id', 'title', 'location', 'lat', 'lng',
            'property_type', 'price', 'area',
            'description', 'images',
            'owner_name', 'owner_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SavedPropertySerializer(serializers.ModelSerializer):
    land = LandSerializer(read_only=True)
    land_id = serializers.PrimaryKeyRelatedField(
        queryset=Land.objects.all(), write_only=True
    )

    class Meta:
        model = SavedProperty
        fields = ['id', 'land', 'land_id', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        land = validated_data.pop('land_id')
        return SavedProperty.objects.create(land=land, **validated_data)


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['id', 'land', 'buyer', 'message', 'created_at']
        read_only_fields = ['created_at']


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"