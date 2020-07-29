from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from ...models import Currency, ConversionRate

from .serializers import ConversionRateSerializer

@api_view(["GET"])
def active_currencies(request):
	active_currencies = Currency.objects.filter(
		is_active=True
	).values('code', 'symbol')
	return Response(status=HTTP_200_OK, data=active_currencies)


@api_view(["GET"])
def conversion_rate(request):
	data = request.data
	conversion_rate_serializer = ConversionRateSerializer(data=data)
	if conversion_rate_serializer.is_valid():
		base = data.get("base")
		conversion_rate_data = ConversionRate.objects.get(
			base__code=base
		)
		conversion_rate_info = {
			"base": base,
		}
		if data.get("to"):
			to = data.get("to")
			rate = conversion_rate_data.rates.get(to)
			conversion_rate_info.update({
				"to": to,
				"rate": rate,
			})
		else:
			conversion_rate_info.update({"rates": conversion_rate_data.rates})

		return Response(status=HTTP_200_OK, data=conversion_rate_info)
	return Response(status=HTTP_400_BAD_REQUEST, data=conversion_rate_serializer.errors)