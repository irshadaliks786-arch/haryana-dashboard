from django.shortcuts import render
from django.db.models import Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from .models import Earthquake, District, WeatherData, AirQualityData
import json

def earthquakes(request):
    # Base queryset - last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    queryset = Earthquake.objects.filter(event_time__gte=thirty_days_ago)

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_mag = request.GET.get('min_mag')
    max_mag = request.GET.get('max_mag')
    search = request.GET.get('search')

    if start_date:
        queryset = queryset.filter(event_time__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(event_time__date__lte=end_date)
    if min_mag:
        queryset = queryset.filter(magnitude__gte=float(min_mag))
    if max_mag:
        queryset = queryset.filter(magnitude__lte=float(max_mag))
    if search:
        queryset = queryset.filter(place__icontains=search)

    # Strongest 5 earthquakes
    strongest = Earthquake.objects.filter(
        event_time__gte=thirty_days_ago
    ).order_by('-magnitude')[:5]

    # Daily chart data
    daily_data = {}
    all_eq = Earthquake.objects.filter(event_time__gte=thirty_days_ago)
    for eq in all_eq:
        if eq.event_time:
            date_str = eq.event_time.strftime('%Y-%m-%d')
            daily_data[date_str] = daily_data.get(date_str, 0) + 1

    daily_data = dict(sorted(daily_data.items()))
    chart_labels = list(daily_data.keys())
    chart_values = list(daily_data.values())

    # Map data
    map_data = []
    for eq in all_eq:
        if eq.latitude and eq.longitude:
            map_data.append({
                'lat': float(eq.latitude),
                'lng': float(eq.longitude),
                'magnitude': float(eq.magnitude) if eq.magnitude else 0,
                'place': eq.place or 'Unknown',
                'time': eq.event_time.strftime('%Y-%m-%d %H:%M') if eq.event_time else '',
                'depth': float(eq.depth) if eq.depth else 0,
            })

    context = {
        'earthquakes': queryset.order_by('-event_time'),
        'strongest': strongest,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'map_data': json.dumps(map_data),
        'total_count': queryset.count(),
        'filters': {
            'start_date': start_date or '',
            'end_date': end_date or '',
            'min_mag': min_mag or '',
            'max_mag': max_mag or '',
            'search': search or '',
        }
    }

    return render(request, 'dashboard/earthquakes.html', context)
def dashboard(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # ── Earthquake Stats ──
    total_earthquakes = Earthquake.objects.filter(
        event_time__gte=thirty_days_ago
    ).count()

    highest_mag = Earthquake.objects.filter(
        event_time__gte=thirty_days_ago
    ).order_by('-magnitude').first()

    latest_eq = Earthquake.objects.filter(
        event_time__gte=thirty_days_ago
    ).order_by('-event_time').first()

    # Active alerts (magnitude >= 4.0)
    alerts = Earthquake.objects.filter(
        event_time__gte=thirty_days_ago,
        magnitude__gte=4.0
    ).order_by('-magnitude')[:5]

    # ── Weather Stats ──
    districts = District.objects.all()
    weather_list = []
    aqi_list = []

    for district in districts:
        weather = WeatherData.objects.filter(
            district=district
        ).order_by('-weather_date').first()

        aqi = AirQualityData.objects.filter(
            district=district
        ).order_by('-recorded_at').first()

        if weather and weather.temperature:
            weather_list.append({
                'district': district.district_name,
                'temperature': float(weather.temperature),
                'condition': weather.weather_condition,
            })

        if aqi and aqi.aqi:
            aqi_list.append({
                'district': district.district_name,
                'aqi': aqi.aqi,
                'category': aqi.category,
            })

    hottest = max(weather_list, key=lambda x: x['temperature']) if weather_list else None
    coldest = min(weather_list, key=lambda x: x['temperature']) if weather_list else None
    most_polluted = max(aqi_list, key=lambda x: x['aqi']) if aqi_list else None
    cleanest = min(aqi_list, key=lambda x: x['aqi']) if aqi_list else None

    # ── Daily Earthquake Chart ──
    daily_data = {}
    all_eq = Earthquake.objects.filter(event_time__gte=thirty_days_ago)
    for eq in all_eq:
        if eq.event_time:
            date_str = eq.event_time.strftime('%Y-%m-%d')
            daily_data[date_str] = daily_data.get(date_str, 0) + 1

    daily_data = dict(sorted(daily_data.items()))
    chart_labels = list(daily_data.keys())
    chart_values = list(daily_data.values())

    # ── AQI Distribution Chart ──
    aqi_counts = {'Good': 0, 'Fair': 0, 'Moderate': 0, 'Poor': 0, 'Very Poor': 0}
    for item in aqi_list:
        cat = item['category']
        if cat in aqi_counts:
            aqi_counts[cat] += 1

    context = {
        # Earthquake
        'total_earthquakes': total_earthquakes,
        'highest_mag': highest_mag,
        'latest_eq': latest_eq,
        'alerts': alerts,

        # Weather
        'hottest': hottest,
        'coldest': coldest,
        'most_polluted': most_polluted,
        'cleanest': cleanest,

        # Charts
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'aqi_labels': json.dumps(list(aqi_counts.keys())),
        'aqi_counts': json.dumps(list(aqi_counts.values())),
    }

    return render(request, 'dashboard/index.html', context)



def weather_aqi(request):
    # Har district ki latest weather
    districts = District.objects.all()

    combined_data = []

    for district in districts:
        # Latest weather
        weather = WeatherData.objects.filter(
            district=district
        ).order_by('-weather_date').first()

        # Latest AQI
        aqi = AirQualityData.objects.filter(
            district=district
        ).order_by('-recorded_at').first()

        combined_data.append({
            'district': district.district_name,
            'temperature': float(weather.temperature) if weather and weather.temperature else None,
            'feels_like': float(weather.feels_like) if weather and weather.feels_like else None,
            'humidity': weather.humidity if weather else None,
            'wind_speed': float(weather.wind_speed) if weather and weather.wind_speed else None,
            'condition': weather.weather_condition if weather else None,
            'aqi': aqi.aqi if aqi else None,
            'pm25': float(aqi.pm25) if aqi and aqi.pm25 else None,
            'pm10': float(aqi.pm10) if aqi and aqi.pm10 else None,
            'no2': float(aqi.no2) if aqi and aqi.no2 else None,
            'co': float(aqi.co) if aqi and aqi.co else None,
            'ozone': float(aqi.ozone) if aqi and aqi.ozone else None,
            'category': aqi.category if aqi else None,
        })

    # Summary cards data
    data_with_temp = [d for d in combined_data if d['temperature'] is not None]
    data_with_aqi = [d for d in combined_data if d['aqi'] is not None]

    hottest = max(data_with_temp, key=lambda x: x['temperature']) if data_with_temp else None
    coldest = min(data_with_temp, key=lambda x: x['temperature']) if data_with_temp else None
    most_polluted = max(data_with_aqi, key=lambda x: x['aqi']) if data_with_aqi else None
    cleanest = min(data_with_aqi, key=lambda x: x['aqi']) if data_with_aqi else None

    # Chart data
    chart_districts = [d['district'] for d in combined_data]
    chart_temps = [d['temperature'] or 0 for d in combined_data]
    chart_aqi = [d['aqi'] or 0 for d in combined_data]
    chart_humidity = [d['humidity'] or 0 for d in combined_data]

    context = {
        'combined_data': combined_data,
        'hottest': hottest,
        'coldest': coldest,
        'most_polluted': most_polluted,
        'cleanest': cleanest,
        'chart_districts': json.dumps(chart_districts),
        'chart_temps': json.dumps(chart_temps),
        'chart_aqi': json.dumps(chart_aqi),
        'chart_humidity': json.dumps(chart_humidity),
    }

    return render(request, 'dashboard/weather_aqi.html', context)