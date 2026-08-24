from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import get_weather, parse_weather_payload, POPULAR_AGRI_LOCATIONS
from .models import WeatherReport, DailyForecast
from .serializers import WeatherReportSerializer, DailyForecastSerializer

class CurrentWeatherView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        loc_key = request.query_params.get('city', 'guntur').lower()
        loc_info = POPULAR_AGRI_LOCATIONS.get(loc_key, POPULAR_AGRI_LOCATIONS['guntur'])

        lat = float(request.query_params.get('lat', loc_info['lat']))
        lon = float(request.query_params.get('lon', loc_info['lon']))
        location_name = request.query_params.get('location', loc_info['name'])

        # Fetch live real-time Open-Meteo weather
        raw_weather = get_weather(lat=lat, lon=lon)
        if raw_weather:
            current_weather, _ = parse_weather_payload(raw_weather, location_name=location_name)
            if current_weather:
                return Response(current_weather, status=status.HTTP_200_OK)

        # Fallback to database record if external API is unreachable
        report = WeatherReport.objects.first()
        if report:
            return Response(WeatherReportSerializer(report).data, status=status.HTTP_200_OK)

        return Response({
            "location_name": location_name,
            "temperature": "31°C",
            "feels_like": "35°C",
            "condition": "Partly Cloudy",
            "humidity": "70%",
            "wind_speed": "12 km/h",
            "rain_probability": "25%",
            "uv_index": "High",
            "advisory_headline": "Agro-Advisory: Moderate weather conditions",
            "advisory_detail": "Ideal conditions for foliar sprays and routine farm irrigation."
        }, status=status.HTTP_200_OK)

class WeatherForecastView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        loc_key = request.query_params.get('city', 'guntur').lower()
        loc_info = POPULAR_AGRI_LOCATIONS.get(loc_key, POPULAR_AGRI_LOCATIONS['guntur'])

        lat = float(request.query_params.get('lat', loc_info['lat']))
        lon = float(request.query_params.get('lon', loc_info['lon']))
        location_name = request.query_params.get('location', loc_info['name'])

        # Fetch live real-time Open-Meteo weather
        raw_weather = get_weather(lat=lat, lon=lon)
        if raw_weather:
            _, forecast_days = parse_weather_payload(raw_weather, location_name=location_name)
            if forecast_days:
                return Response(forecast_days, status=status.HTTP_200_OK)

        # Fallback to database
        forecasts = DailyForecast.objects.all()
        return Response(DailyForecastSerializer(forecasts, many=True).data, status=status.HTTP_200_OK)
