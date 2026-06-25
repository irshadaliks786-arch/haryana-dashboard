import os
import sys
import django
import requests

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haryana_dashboard.settings')
django.setup()

from dashboard.models import District, WeatherData

# OpenWeather API key
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather_condition(weather_list):
    if weather_list:
        return weather_list[0].get('description', 'Unknown')
    return 'Unknown'

def fetch_weather():
    districts = District.objects.all()
    print(f"Total districts: {districts.count()}")

    saved = 0
    failed = 0

    for district in districts:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': float(district.latitude),
            'lon': float(district.longitude),
            'appid': API_KEY,
            'units': 'metric'  # Celsius mein
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            main = data.get('main', {})
            wind = data.get('wind', {})
            weather = data.get('weather', [])

            WeatherData.objects.create(
                district=district,
                temperature=main.get('temp'),
                feels_like=main.get('feels_like'),
                humidity=main.get('humidity'),
                wind_speed=wind.get('speed'),
                weather_condition=get_weather_condition(weather),
                source='OpenWeather'
            )

            print(f"✅ {district.district_name} — {main.get('temp')}°C")
            saved += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ {district.district_name} — Error: {e}")
            failed += 1

    print(f"\n✅ Saved: {saved} | ❌ Failed: {failed}")

if __name__ == '__main__':
    fetch_weather()