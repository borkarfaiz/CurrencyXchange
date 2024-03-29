from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from currency_converter.helpers import get_system_conversion_rates, get_live_conversion_rates
from .serializers import ConversionRateSerializer
from ...models import Currency


@api_view(["GET"])
def active_currencies(request):
	active_currencies_info = Currency.objects.filter(
		is_active=True
	).values('code', 'symbol')
	return Response(status=HTTP_200_OK, data=active_currencies_info)


@api_view(["GET"])
@cache_page(60*10)
def conversion_rate(request):
	data = request.query_params
	conversion_rate_serializer = ConversionRateSerializer(data=data)
	if conversion_rate_serializer.is_valid():
		base = data.get("base")
		to = data.get("to")
		conversion_rate_info = get_system_conversion_rates(base=base, to=to)
		return Response(status=HTTP_200_OK, data=conversion_rate_info)
	return Response(status=HTTP_400_BAD_REQUEST, data=conversion_rate_serializer.errors)


@api_view(["GET"])
def live_rates(request):
	data = request.query_params
	conversion_rate_serializer = ConversionRateSerializer(data=data)
	if conversion_rate_serializer.is_valid():
		base = data.get("base")
		to = data.get("to")
		conversion_rate_info = get_live_conversion_rates(from_currency=base, to_currency=to)
		return Response(status=HTTP_200_OK, data=conversion_rate_info)
	return Response(status=HTTP_400_BAD_REQUEST, data=conversion_rate_serializer.errors)
