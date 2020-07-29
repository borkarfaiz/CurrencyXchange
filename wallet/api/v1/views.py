from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from rest_framework.views import APIView

from ...models import Wallet

from .serializers import WalletSerializer

@api_view(["POST"])
def add_funds(request):
	# amount, currency, transaction_id
	# validate the data
	# create the order
	# add funds if the wallet not created then create wallet and balance
	# if balance not created then create balance
	user = request.user
	wallet = Wallet.objects.get(user=user)
	amount = request.data.get('amount')
	currency = request.data.get('currency')
	transaction_id = request.data.get('transaction_id')


class WalletAPI(APIView):
	def get(self, request):
		"""
		fetches the wallet and balances
		"""
		user = request.user
		wallet = Wallet.objects.filter(user=user).last()
		serializer = WalletSerializer(instance=wallet)
		return Response(status=HTTP_200_OK, data=serializer.data)

	def post(self, request):
		"""
		creates the wallet and add balance as 0 in default currency
		if not created
		"""
		user = request.user
		wallet = Wallet.objects.filter(user=user).exists()
		if wallet:
			return Response(status=HTTP_409_CONFLICT, data={"detail": "wallet already created"})
		