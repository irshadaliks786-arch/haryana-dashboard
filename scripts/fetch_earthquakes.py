import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haryana_dashboard.settings')
django.setup()

from dashboard.models import Earthquake

def fetch_earthquakes():
    # Last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    params = {
        'format': 'geojson',
        'starttime': start_date.strftime('%Y-%m-%d'),
        'endtime': end_date.strftime('%Y-%m-%d'),
        'minlatitude': 23.0,   # India + surrounding area
        'maxlatitude': 37.0,
        'minlongitude': 68.0,
        'maxlongitude': 97.0,
        'minmagnitude': 2.0,   # 2.0+ magnitude
        'orderby': 'time'
    }

    print("USGS API se data fetch ho raha hai...")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        earthquakes = data.get('features', [])
        print(f"Total earthquakes mila: {len(earthquakes)}")

        saved = 0
        skipped = 0

        for eq in earthquakes:
            props = eq.get('properties', {})
            geo = eq.get('geometry', {})
            coords = geo.get('coordinates', [])

            earthquake_id = eq.get('id', '')

            # Duplicate check
            if Earthquake.objects.filter(earthquake_id=earthquake_id).exists():
                skipped += 1
                continue

            # Time convert karo
            time_ms = props.get('time')
            event_time = None
            if time_ms:
                event_time = datetime.utcfromtimestamp(time_ms / 1000)

            Earthquake.objects.create(
                earthquake_id=earthquake_id,
                magnitude=props.get('mag'),
                place=props.get('place'),
                event_time=event_time,
                longitude=coords[0] if len(coords) > 0 else None,
                latitude=coords[1] if len(coords) > 1 else None,
                depth=coords[2] if len(coords) > 2 else None,
                source='USGS'
            )
            saved += 1

        print(f"✅ Saved: {saved} | Skipped (duplicate): {skipped}")

    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fetch_earthquakes()