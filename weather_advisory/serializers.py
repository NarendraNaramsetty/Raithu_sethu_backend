from rest_framework import serializers
from .models import WeatherReport, DailyForecast

class DailyForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyForecast
        fields = ['id', 'day', 'temp', 'condition', 'rain', 'icon']

class WeatherReportSerializer(serializers.ModelSerializer):
    forecast = DailyForecastSerializer(source='forecast_days', many=True, read_only=True)

    class Meta:
        model = WeatherReport
        fields = [
            'id', 'location_name', 'temperature', 'feels_like',
            'condition', 'humidity', 'wind_speed', 'rain_probability',
            'uv_index', 'advisory_headline', 'advisory_detail',
            'forecast', 'updated_at'
        ]
