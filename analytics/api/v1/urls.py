from django.urls import path
from .views import financial_summarization, average_currency_transfer_on_weekdays

urlpatterns = [
	path("financial-summarization", financial_summarization),
	path("average-currency-transfer-on-weekdays", average_currency_transfer_on_weekdays)
]