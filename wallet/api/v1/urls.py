from django.urls import path
from .views import add_funds, BalanceAPI, WalletAPI, withdraw_funds

urlpatterns = [
	#
	path("", WalletAPI.as_view()),
	path("balance", BalanceAPI.as_view()),
	path("add-funds", add_funds),
	path("withdraw-funds", withdraw_funds),
	# path("withdraw-funds", withdraw_funds),
	# path("transfer-funds", transfer_funds),
	# path("convert-funds", convert_funds),
]