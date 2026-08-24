import requests
from datetime import datetime

WMO_WEATHER_CODES = {
    0: ("Clear Sky", "Sun"),
    1: ("Mainly Clear", "Sun"),
    2: ("Partly Cloudy", "CloudSun"),
    3: ("Overcast", "CloudSun"),
    45: ("Foggy / Mist", "CloudSun"),
    48: ("Depositing Rime Fog", "CloudSun"),
    51: ("Light Drizzle", "CloudRain"),
    53: ("Moderate Drizzle", "CloudRain"),
    55: ("Dense Drizzle", "CloudRain"),
    61: ("Slight Rain", "CloudRain"),
    63: ("Moderate Rain", "CloudRain"),
    65: ("Heavy Rain", "CloudRain"),
    80: ("Scattered Showers", "CloudRain"),
    81: ("Moderate Showers", "CloudRain"),
    82: ("Violent Showers", "CloudRain"),
    95: ("Thunderstorm", "CloudRain"),
    96: ("Thunderstorm with Slight Hail", "CloudRain"),
    99: ("Thunderstorm with Heavy Hail", "CloudRain"),
}

POPULAR_AGRI_LOCATIONS = {
    "guntur": {"name": "Guntur District, AP", "lat": 16.3067, "lon": 80.4365},
    "warangal": {"name": "Warangal, Telangana", "lat": 17.9689, "lon": 79.5941},
    "kurnool": {"name": "Kurnool, AP", "lat": 15.8281, "lon": 78.0373},
    "vijayawada": {"name": "Vijayawada, AP", "lat": 16.5062, "lon": 80.6480},
    "hyderabad": {"name": "Hyderabad, Telangana", "lat": 17.3850, "lon": 78.4867},
    "khammam": {"name": "Khammam, Telangana", "lat": 17.2473, "lon": 80.1514},
    "anantapur": {"name": "Anantapur, AP", "lat": 14.6819, "lon": 77.6006},
    "karimnagar": {"name": "Karimnagar, Telangana", "lat": 18.4386, "lon": 79.1288},
}

def get_weather(lat=16.3067, lon=80.4365):
    """
    Fetches real-time hyperlocal weather and 7-day forecast from Open-Meteo API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code,wind_speed_10m_max,uv_index_max",
        "timezone": "Asia/Kolkata"
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Open-Meteo weather: {e}")
        return None

def generate_agro_advisory(current_data, daily_data):
    """
    Generates intelligent, scientifically backed farmer spray & irrigation advisory
    based on real-time Open-Meteo meteorological conditions.
    """
    if not current_data or not daily_data:
        return (
            "Agro-Advisory: Weather parameters normal.",
            "Maintain regular crop scouting and scheduled irrigation."
        )

    humidity = current_data.get('relative_humidity_2m', 60)
    wind_speed = current_data.get('wind_speed_10m', 10)
    
    # Check max precipitation probability in next 48h
    rain_probs = daily_data.get('precipitation_probability_max', [0, 0])
    rain_prob_today = rain_probs[0] if len(rain_probs) > 0 else 0
    rain_prob_tomorrow = rain_probs[1] if len(rain_probs) > 1 else 0
    max_rain_prob = max(rain_prob_today, rain_prob_tomorrow)

    rain_sums = daily_data.get('precipitation_sum', [0, 0])
    total_rain = sum(rain_sums[:2]) if len(rain_sums) >= 2 else 0

    if max_rain_prob >= 50 or total_rain >= 5.0:
        headline = f"Rain Alert ({max_rain_prob}% probability in next 24-48h)"
        detail = "Hold pesticide and fertilizer spraying until skies clear to prevent chemical wash-off. Ensure field drainage channels are clear to prevent waterlogging in cotton, chilli, and pulses."
    elif wind_speed >= 20.0:
        headline = f"High Wind Alert ({wind_speed} km/h)"
        detail = "Avoid tractor-mounted and drone pesticide spraying during strong winds to prevent chemical drift. Secure nursery shade nets and banana propping."
    elif humidity >= 80:
        headline = f"High Humidity Alert ({humidity}%)"
        detail = "Extended high moisture increases risk of fungal diseases (Leaf Blast in Paddy, Blight in Tomato). Inspect lower canopy and apply preventive bio-fungicides if needed."
    else:
        headline = "Favorable Weather for Farm Operations"
        detail = "Weather conditions are optimal for foliar nutrient sprays, weeding, and timely drip/furrow irrigation."

    return headline, detail

def parse_weather_payload(data, location_name="Guntur District, AP"):
    if not data:
        return None, []

    current = data.get('current', {})
    daily = data.get('daily', {})

    current_code = current.get('weather_code', 0)
    condition_text, _ = WMO_WEATHER_CODES.get(current_code, ("Partly Cloudy", "CloudSun"))

    uv_index_max = daily.get('uv_index_max', [6])[0] if daily.get('uv_index_max') else 6
    uv_text = "Very High" if uv_index_max >= 8 else "High" if uv_index_max >= 6 else "Moderate"

    advisory_headline, advisory_detail = generate_agro_advisory(current, daily)

    # 1. Current Weather
    rain_probs = daily.get('precipitation_probability_max', [0])
    current_weather = {
        "location_name": location_name,
        "temperature": f"{round(current.get('temperature_2m', 30))}°C",
        "feels_like": f"{round(current.get('apparent_temperature', 33))}°C",
        "condition": condition_text,
        "humidity": f"{current.get('relative_humidity_2m', 65)}%",
        "wind_speed": f"{round(current.get('wind_speed_10m', 12))} km/h",
        "rain_probability": f"{rain_probs[0] if rain_probs else 0}%",
        "uv_index": uv_text,
        "advisory_headline": advisory_headline,
        "advisory_detail": advisory_detail,
        "updated_at": current.get('time', '')
    }

    # 2. 7-Day Forecast
    forecast_days = []
    times = daily.get('time', [])
    t_max = daily.get('temperature_2m_max', [])
    t_min = daily.get('temperature_2m_min', [])
    codes = daily.get('weather_code', [])
    rain_p = daily.get('precipitation_probability_max', [])

    for i in range(min(7, len(times))):
        date_str = times[i]
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = "Today" if i == 0 else dt.strftime("%a")
        except Exception:
            day_name = f"Day {i+1}"

        w_code = codes[i] if i < len(codes) else 0
        cond, icon_name = WMO_WEATHER_CODES.get(w_code, ("Partly Cloudy", "CloudSun"))
        max_t = round(t_max[i]) if i < len(t_max) else 32
        min_t = round(t_min[i]) if i < len(t_min) else 24
        r_prob = rain_p[i] if i < len(rain_p) else 10

        forecast_days.append({
            "id": i + 1,
            "day": day_name,
            "date": date_str,
            "temp": f"{max_t}°C / {min_t}°C",
            "condition": cond,
            "rain": f"{r_prob}%",
            "icon": icon_name
        })

    return current_weather, forecast_days
