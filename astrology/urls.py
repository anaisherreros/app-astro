from django.urls import path
from .views import health, chart, chart_form

urlpatterns = [
    path("health/", health, name="astrology-health"),
    path("chart/", chart, name="astrology-chart"),
    path("chart/form/", chart_form, name="astrology-chart-form"),
]