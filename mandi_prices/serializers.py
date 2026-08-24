from rest_framework import serializers
from .models import MandiCommodityPrice

class MandiCommodityPriceSerializer(serializers.ModelSerializer):
    crop = serializers.CharField(source='crop_name')
    mandi = serializers.CharField(source='mandi_name')
    price = serializers.IntegerField(source='modal_price')
    prev = serializers.IntegerField(source='previous_price')
    change = serializers.CharField(source='price_change_percent')
    msp = serializers.IntegerField(source='msp_rate')
    arrival = serializers.CharField(source='daily_arrival')

    class Meta:
        model = MandiCommodityPrice
        fields = [
            'id', 'crop', 'crop_name_native', 'mandi', 'district',
            'state', 'price', 'prev', 'change', 'msp', 'arrival', 'updated_at'
        ]
