from django.urls import path

from .views import active_currencies, conversion_rate, live_rates

urlpatterns = [
	path("active-currencies", active_currencies),
	path("conversion-rate", conversion_rate),
	path("live-rates", live_rates)
]