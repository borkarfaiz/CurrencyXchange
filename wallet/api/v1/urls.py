from django.urls import path
from .views import WalletAPI, BalanceAPI

urlpatterns = [
	#
	path("", WalletAPI.as_view()),
	path("balance", BalanceAPI.as_view()),
	# path("withdraw-funds", withdraw_funds),
	# path("transfer-funds", transfer_funds),
	# path("convert-funds", convert_funds),
	# path("fetch-funds", get_funds)
]