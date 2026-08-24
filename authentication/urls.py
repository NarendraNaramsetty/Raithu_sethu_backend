from django.urls import path
from .views import SendOTPView, VerifyOTPView, FarmerProfileView, GoogleAuthView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
    path('profile/', FarmerProfileView.as_view(), name='farmer-profile'),
]

