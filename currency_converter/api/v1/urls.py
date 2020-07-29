from django.urls import path

from .views import active_currencies

urlpatterns = [
	path("active_currencies", active_currencies),
	# path("", withdraw_funds),
	# path("transfer-funds", transfer_funds),
	# path("convert-funds", convert_funds),
	# path("fetch-funds", get_funds)
]