from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('earthquakes/', views.earthquakes, name='earthquakes'),
    path('weather/', views.weather_aqi, name='weather_aqi'),
]