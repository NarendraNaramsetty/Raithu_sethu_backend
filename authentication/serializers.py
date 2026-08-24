from rest_framework import serializers
from .models import FarmerProfile, OTPVerification

class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = [
            'id', 'email', 'phone', 'name', 'name_native', 'village',
            'district', 'state', 'total_land', 'soil_type',
            'irrigation_source', 'active_crops', 'avatar',
            'created_at', 'updated_at'
        ]

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip()
        phone = attrs.get('phone', '').strip()
        if not email and not phone:
            raise serializers.ValidationError("Either an email address or mobile number is required.")
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email', '').strip()
        phone = attrs.get('phone', '').strip()
        if not email and not phone:
            raise serializers.ValidationError("Either an email address or mobile number is required.")
        return attrs

class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    avatar = serializers.CharField(required=False, allow_blank=True)

