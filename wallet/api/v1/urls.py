from django.urls import path
from .views import add_funds, WalletAPI

urlpatterns = [
	#
	path("add-funds", add_funds),
	path("", WalletAPI.as_view())
	# path("withdraw-funds", withdraw_funds),
	# path("transfer-funds", transfer_funds),
	# path("convert-funds", convert_funds),
	# path("fetch-funds", get_funds)
]