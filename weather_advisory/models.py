from django.db import models

class WeatherReport(models.Model):
    location_name = models.CharField(max_length=150, default='Guntur District, AP')
    temperature = models.CharField(max_length=20, default='32°C')
    feels_like = models.CharField(max_length=20, default='36°C')
    condition = models.CharField(max_length=100, default='Partly Cloudy')
    humidity = models.CharField(max_length=20, default='68%')
    wind_speed = models.CharField(max_length=20, default='14 km/h')
    rain_probability = models.CharField(max_length=20, default='20%')
    uv_index = models.CharField(max_length=20, default='High')
    advisory_headline = models.CharField(
        max_length=255,
        default='Agro-Advisory: Moderate Rain expected Sunday & Monday'
    )
    advisory_detail = models.TextField(
        default='Hold pesticide/fertilizer spraying until Tuesday to avoid chemical wash-off. Ensure field drainage channels are clear for standing cotton & chilli crops.'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location_name} - {self.temperature}"

class DailyForecast(models.Model):
    weather_report = models.ForeignKey(WeatherReport, on_delete=models.CASCADE, related_name='forecast_days', null=True, blank=True)
    day = models.CharField(max_length=50)
    temp = models.CharField(max_length=50)
    condition = models.CharField(max_length=100)
    rain = models.CharField(max_length=20)
    icon = models.CharField(max_length=50, default='CloudSun')

    def __str__(self):
        return f"{self.day}: {self.temp} ({self.condition})"
