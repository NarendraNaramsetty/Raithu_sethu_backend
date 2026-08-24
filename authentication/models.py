from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile', null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='+91 98765 43210')
    name = models.CharField(max_length=100, default='Ramesh Patel')
    name_native = models.CharField(max_length=100, default='రమేష్ పటేల్', blank=True)
    village = models.CharField(max_length=150, default='Pedakakani')
    district = models.CharField(max_length=100, default='Guntur')
    state = models.CharField(max_length=100, default='Andhra Pradesh')
    total_land = models.CharField(max_length=50, default='6.5 Acres')
    soil_type = models.CharField(max_length=100, default='Black Clay Loam (నల్లరేగడి నేల)')
    irrigation_source = models.CharField(max_length=100, default='Borewell + Canal')
    active_crops = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='farmer_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        ident = self.email or self.phone or self.name
        return f"{self.name} ({ident})"

class OTPVerification(models.Model):
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.email or self.phone
        return f"OTP for {target}: {self.otp}"

