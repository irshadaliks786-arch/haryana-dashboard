import os
import sys
import django
import requests

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haryana_dashboard.settings')
django.setup()

from dashboard.models import District, AirQualityData

# OpenWeather API key
API_KEY = os.getenv('OPENWEATHER_API_KEY')

# AQI index to category
def get_aqi_category(aqi_index):
    categories = {
        1: 'Good',
        2: 'Fair',
        3: 'Moderate',
        4: 'Poor',
        5: 'Very Poor'
    }
    return categories.get(aqi_index, 'Unknown')

def fetch_aqi():
    districts = District.objects.all()
    print(f"Total districts: {districts.count()}")

    saved = 0
    failed = 0

    for district in districts:
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': float(district.latitude),
            'lon': float(district.longitude),
            'appid': API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            list_data = data.get('list', [])
            if not list_data:
                print(f"⚠️ {district.district_name} — No data")
                continue

            item = list_data[0]
            main = item.get('main', {})
            components = item.get('components', {})
            aqi_index = main.get('aqi')

            AirQualityData.objects.create(
                district=district,
                aqi=aqi_index,
                pm25=components.get('pm2_5'),
                pm10=components.get('pm10'),
                no2=components.get('no2'),
                co=components.get('co'),
                ozone=components.get('o3'),
                category=get_aqi_category(aqi_index),
                source='OpenWeather'
            )

            print(f"✅ {district.district_name} — AQI: {aqi_index} ({get_aqi_category(aqi_index)})")
            saved += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ {district.district_name} — Error: {e}")
            failed += 1

    print(f"\n✅ Saved: {saved} | ❌ Failed: {failed}")

if __name__ == '__main__':
    fetch_aqi()