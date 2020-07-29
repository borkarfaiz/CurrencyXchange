from django.urls import path

from .views import active_currencies, conversion_rate

urlpatterns = [
	path("active-currencies", active_currencies),
	path("conversion-rate", conversion_rate),
]