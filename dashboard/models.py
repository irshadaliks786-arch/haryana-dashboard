from django.db import models

class District(models.Model):
    district_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Haryana')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        db_table = 'districts'  # existing table use karega

    def __str__(self):
        return self.district_name


class Earthquake(models.Model):
    earthquake_id = models.CharField(max_length=50, unique=True)
    magnitude = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    place = models.CharField(max_length=255, null=True)
    event_time = models.DateTimeField(null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    depth = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    source = models.CharField(max_length=50, default='USGS')

    class Meta:
        db_table = 'earthquakes'

    def __str__(self):
        return f"{self.place} - {self.magnitude}"


class WeatherData(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    weather_date = models.DateTimeField(auto_now_add=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    feels_like = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    humidity = models.IntegerField(null=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weather_condition = models.CharField(max_length=100, null=True)
    source = models.CharField(max_length=50, default='OpenWeather')

    class Meta:
        db_table = 'weather_data'

    def __str__(self):
        return f"{self.district.district_name} - {self.weather_date}"


class AirQualityData(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    aqi = models.IntegerField(null=True)
    pm25 = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    pm10 = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    no2 = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    co = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    ozone = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    category = models.CharField(max_length=50, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default='OpenWeather')

    class Meta:
        db_table = 'air_quality_data'

    def __str__(self):
        return f"{self.district.district_name} - AQI: {self.aqi}"