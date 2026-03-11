from django.test import TestCase

from .location.place import (
    resolve_birth_context,
    resolve_birth_place,
    search_city_suggestions,
)


class LocationResolutionTests(TestCase):
    def test_resolve_city_with_country_hint(self):
        result = resolve_birth_place("barcelona, VE")
        self.assertEqual(result["country_code"], "VE")

    def test_resolve_city_without_country_hint_prefers_population(self):
        result = resolve_birth_place("barcelona")
        self.assertEqual(result["country_code"], "ES")

    def test_suggestions_include_multiple_valencia_options(self):
        suggestions = search_city_suggestions("valencia", limit=30)
        countries = {item["country_code"] for item in suggestions}
        self.assertIn("ES", countries)
        self.assertIn("VE", countries)

    def test_suggestions_short_query_returns_empty(self):
        suggestions = search_city_suggestions("v", limit=20)
        self.assertEqual(suggestions, [])

    def test_unknown_city_raises_error(self):
        with self.assertRaises(ValueError):
            resolve_birth_place("ciudad-inventada-xyz")


class TimezoneConversionTests(TestCase):
    def test_madrid_timezone_is_europe_madrid(self):
        context = resolve_birth_context("2024-01-15", "12:00", "madrid")
        self.assertEqual(context["timezone"], "Europe/Madrid")

    def test_lima_timezone_is_america_lima(self):
        context = resolve_birth_context("2024-07-15", "12:00", "lima")
        self.assertEqual(context["timezone"], "America/Lima")
