import random
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .models import FarmerProfile, OTPVerification
from .serializers import (
    FarmerProfileSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    GoogleAuthSerializer
)

logger = logging.getLogger(__name__)

STATIC_DEFAULT_PHONE = "+91 98765 43210"

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email', '').strip().lower()
            phone = serializer.validated_data.get('phone', '').strip() or STATIC_DEFAULT_PHONE
            
            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            
            # Record OTP in database
            OTPVerification.objects.create(
                email=email if email else None,
                phone=phone,
                otp=otp
            )
            
            email_sent = False
            email_error = None

            # If email is provided, send OTP via Django email backend / Gmail SMTP
            if email:
                subject = f"🌱 {otp} is your RaithuSetu Login OTP"
                plain_message = (
                    f"Namaste Farmer,\n\n"
                    f"Your RaithuSetu login verification code is: {otp}\n\n"
                    f"This OTP is valid for 10 minutes. Please do not share this code with anyone.\n\n"
                    f"RaithuSetu - Farmer's Friend • Smart Agri\n"
                    f"https://raithusetu.agri"
                )
                html_message = f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background-color: #f9fafb; border-radius: 16px; border: 1px solid #e5e7eb;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="display: inline-block; background-color: #16a34a; color: white; width: 48px; height: 48px; line-height: 48px; border-radius: 12px; font-size: 24px; font-weight: bold;">🌱</div>
                        <h2 style="color: #111827; margin: 12px 0 4px 0; font-size: 22px;">RaithuSetu Smart Agriculture</h2>
                        <p style="color: #6b7280; font-size: 13px; margin: 0;">Farmer's Friend • రైతు మిత్రుడు • किसान मित्र</p>
                    </div>
                    <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <p style="color: #374151; font-size: 14px; margin-bottom: 12px;">Use the following One-Time Password (OTP) to login to your farmer account:</p>
                        <div style="background: #f0fdf4; border: 2px dashed #16a34a; border-radius: 10px; padding: 14px; margin: 16px 0; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #15803d;">
                            {otp}
                        </div>
                        <p style="color: #9ca3af; font-size: 12px; margin-top: 8px;">Valid for 10 minutes. If you did not request this, please ignore this email.</p>
                    </div>
                    <div style="text-align: center; margin-top: 20px; color: #9ca3af; font-size: 11px;">
                        <p>RaithuSetu • Empowering Indian Agriculture with AI Diagnostics & Real-time Mandi Rates</p>
                    </div>
                </div>
                """
                
                try:
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@raithusetu.com')
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=from_email,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    email_sent = True
                except Exception as e:
                    logger.warning(f"Failed to send email OTP to {email}: {e}")
                    email_error = str(e)

            target_display = email if email else phone
            response_data = {
                "status": "success",
                "message": f"OTP successfully sent to {target_display}",
                "email_sent": email_sent,
                "target": target_display,
                "demo_otp": otp  # Available for development/testing and offline fallback
            }
            if email_error and settings.DEBUG:
                response_data["email_notice"] = "SMTP not yet fully configured or failed. Use demo_otp to test."

            return Response(response_data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email', '').strip().lower()
            phone = serializer.validated_data.get('phone', '').strip() or STATIC_DEFAULT_PHONE
            otp = serializer.validated_data.get('otp', '').strip()

            ten_mins_ago = timezone.now() - timedelta(minutes=15)
            
            # Check OTP matching in database or demo codes
            is_valid = False
            if otp in ["1234", "123456"]:
                is_valid = True
            elif email:
                otp_record = OTPVerification.objects.filter(
                    email__iexact=email,
                    otp=otp,
                    created_at__gte=ten_mins_ago
                ).order_by('-created_at').first()
                if otp_record:
                    is_valid = True
                    otp_record.is_verified = True
                    otp_record.save()
            elif phone:
                otp_record = OTPVerification.objects.filter(
                    phone=phone,
                    otp=otp,
                    created_at__gte=ten_mins_ago
                ).order_by('-created_at').first()
                if otp_record:
                    is_valid = True
                    otp_record.is_verified = True
                    otp_record.save()

            if is_valid:
                # Determine username and display name
                if email:
                    username = email
                    name_part = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
                else:
                    username = f"farmer_{phone.replace(' ', '').replace('+', '')}"
                    name_part = f"Farmer ({phone[-4:]})"

                # 1. Store/Get User in Database
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': name_part
                    }
                )
                if email and user.email != email:
                    user.email = email
                    user.save()

                # 2. Store/Get FarmerProfile in Database
                profile, created = FarmerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'email': email,
                        'phone': phone or STATIC_DEFAULT_PHONE,
                        'name': name_part,
                        'name_native': 'రైతు సేవకుడు',
                        'village': 'Pedakakani',
                        'district': 'Guntur',
                        'state': 'Andhra Pradesh',
                        'total_land': '6.5 Acres',
                        'soil_type': 'Black Clay Loam (నల్లరేగడి నేల)',
                        'irrigation_source': 'Borewell + Canal',
                        'active_crops': ['Paddy', 'Chilli', 'Cotton']
                    }
                )
                if email and not profile.email:
                    profile.email = email
                    profile.save()

                # 3. Create or Get DRF Auth Token
                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    "status": "success",
                    "message": "Authentication successful",
                    "token": token.key,
                    "user": FarmerProfileSerializer(profile).data
                }, status=status.HTTP_200_OK)

            return Response({
                "status": "error",
                "message": "Invalid or expired OTP. Please check the code and try again."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email', '').strip().lower()
            name = serializer.validated_data.get('name', '').strip()
            
            if not email:
                return Response({"detail": "Google email is required."}, status=status.HTTP_400_BAD_REQUEST)

            display_name = name or email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

            # Store/Get User in Database
            user, _ = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': display_name
                }
            )

            # Store/Get FarmerProfile in Database
            profile, created = FarmerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'email': email,
                    'phone': STATIC_DEFAULT_PHONE,
                    'name': display_name,
                    'name_native': 'రైతు సేవకుడు',
                    'village': 'Pedakakani',
                    'district': 'Guntur',
                    'state': 'Andhra Pradesh',
                    'total_land': '6.5 Acres',
                    'soil_type': 'Black Clay Loam (నల్లరేగడి నేల)',
                    'irrigation_source': 'Borewell + Canal',
                    'active_crops': ['Paddy', 'Chilli', 'Cotton']
                }
            )

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "status": "success",
                "message": "Google authentication successful",
                "token": token.key,
                "user": FarmerProfileSerializer(profile).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FarmerProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.query_params.get('email', '').strip().lower()
        phone = request.query_params.get('phone', '').strip()
        profile = None

        if email:
            profile = FarmerProfile.objects.filter(email__iexact=email).first()
        elif phone:
            profile = FarmerProfile.objects.filter(phone__icontains=phone).first()
        elif request.user and request.user.is_authenticated:
            profile = getattr(request.user, 'farmer_profile', None) or getattr(request.user, 'farmerprofile', None)
        else:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Token '):
                key = auth_header.split(' ')[1]
                token_obj = Token.objects.filter(key=key).first()
                if token_obj:
                    profile = getattr(token_obj.user, 'farmer_profile', None) or getattr(token_obj.user, 'farmerprofile', None)

        if profile:
            return Response(FarmerProfileSerializer(profile).data, status=status.HTTP_200_OK)
        return Response({"detail": "No profile found for current user."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()
        profile = None

        if email:
            profile = FarmerProfile.objects.filter(email__iexact=email).first()
        elif phone:
            profile = FarmerProfile.objects.filter(phone__icontains=phone).first()
        elif request.user and request.user.is_authenticated:
            profile = getattr(request.user, 'farmer_profile', None) or getattr(request.user, 'farmerprofile', None)
        else:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Token '):
                key = auth_header.split(' ')[1]
                token_obj = Token.objects.filter(key=key).first()
                if token_obj:
                    profile = getattr(token_obj.user, 'farmer_profile', None) or getattr(token_obj.user, 'farmerprofile', None)

        if not profile:
            return Response({"detail": "Profile not found to update."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FarmerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

