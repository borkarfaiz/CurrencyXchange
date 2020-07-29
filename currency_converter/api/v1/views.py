from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from ...models import Currency


@api_view(["GET"])
def active_currencies(request):
	active_currencies = Currency.objects.filter(
		is_active=True
	).values('code', 'symbol')
	return Response(status=HTTP_200_OK, data=active_currencies)