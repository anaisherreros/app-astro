from django.urls import path

from .views import chart, chart_form, city_suggestions, health, interpretation

urlpatterns = [
    path("health/", health, name="astrology-health"),
    path("chart/", chart, name="astrology-chart"),
    path("chart/form/", chart_form, name="astrology-chart-form"),
    path("interpretation/", interpretation, name="astrology-interpretation"),
    path("cities/suggest/", city_suggestions, name="astrology-city-suggestions"),
]