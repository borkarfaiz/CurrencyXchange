from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from analytics.helpers import get_financial_summarization, get_average_currency_transfer_on_weekdays
from .serializers import DateSerializer


@api_view(["GET"])
@cache_page(60 * 10)
def financial_summarization(request):
	request_data = request.query_params
	date_serializer = DateSerializer(data=request_data)
	if not date_serializer.is_valid():
		return Response(status=HTTP_400_BAD_REQUEST, data=date_serializer.errors)
	start_date = request_data.get("start_date")
	financial_summarization = get_financial_summarization(start_date=start_date)
	return Response(status=HTTP_200_OK, data=financial_summarization)


@api_view(["GET"])
@cache_page(60 * 5)
def average_currency_transfer_on_weekdays(request):
	average_currency_transfer_on_weekdays = get_average_currency_transfer_on_weekdays()
	return Response(status=HTTP_200_OK, data=average_currency_transfer_on_weekdays)
