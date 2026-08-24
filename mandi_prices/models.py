from django.db import models

class MandiCommodityPrice(models.Model):
    crop_name = models.CharField(max_length=120)
    crop_name_native = models.CharField(max_length=120, blank=True)
    mandi_name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Andhra Pradesh')
    modal_price = models.IntegerField(help_text="Price in INR per Quintal")
    previous_price = models.IntegerField(help_text="Previous day price")
    price_change_percent = models.CharField(max_length=20, default='+0.0%')
    msp_rate = models.IntegerField(help_text="Minimum Support Price")
    daily_arrival = models.CharField(max_length=100, default='500 Quintals')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop_name} - {self.mandi_name} (₹{self.modal_price})"
