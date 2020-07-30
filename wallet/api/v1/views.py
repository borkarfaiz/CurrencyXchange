from decimal import Decimal

from django.db.utils import IntegrityError

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from rest_framework.views import APIView

from ...models import Balance, Wallet, OrderCategory

from .helpers import add_funds_to_account, withdraw_funds_from_account, convert_and_transfer_currency
from .serializers import BalanceSerializer, FundsSerializer, WalletSerializer, FundsConversionSerializer


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
		data = request.data
		data.update({'user': user.id})
		wallet_serializer = WalletSerializer(data=data)
		if wallet_serializer.is_valid():
			wallet_serializer.save()
			return Response(status=HTTP_201_CREATED, data=wallet_serializer.data)
		return Response(status=HTTP_400_BAD_REQUEST, data=wallet_serializer.errors)


class BalanceAPI(APIView):
	def get(self, request):
		"""
		fetches the balance of a user
		"""
		user = request.user
		code = request.query_params.get('code')
		if code:
			balances = Balance.objects.filter(wallet__user=user, currency__code=code)
		else:
			balances = Balance.objects.filter(wallet__user=user)
		balance_serializer = BalanceSerializer(balances, many=True)
		return Response(status=HTTP_200_OK, data=balance_serializer.data)

	def post(self, request):
		"""
		create a balance inside a wallet for user to add money
		"""
		user = request.user
		data = request.data
		data.update({"wallet": user.wallet.id})
		balance_serializer = BalanceSerializer(data=data)
		if balance_serializer.is_valid():
			try:
				balance_serializer.save()
				return Response(status=HTTP_201_CREATED, data=balance_serializer.data)
			# couldn't able to handle unique together constraint so handling it here
			except IntegrityError as e:
				return Response(status=HTTP_409_CONFLICT, data={"currency": [str(e)]})
		return Response(status=HTTP_400_BAD_REQUEST, data=balance_serializer.errors)


@api_view(["POST"])
def add_funds(request):
	user = request.user
	data = request.data

	# for validation of currency and amount
	balance_serializer = FundsSerializer(data=data)
	if not balance_serializer.is_valid():
		return Response(status=HTTP_400_BAD_REQUEST, data=balance_serializer.errors)

	amount = request.data.get("amount")
	currency = request.data.get("currency")
	try:
		add_funds_to_account(user=user, amount=amount, currency=currency)
	except Exception as e:
		return Response(status=HTTP_400_BAD_REQUEST, data={"detail": str(e)})

	balance = Balance.objects.only('balance').get(wallet__user=user, currency__code=currency).balance
	return Response(status=HTTP_201_CREATED, data={"balance": balance, "currency": currency})


@api_view(["POST"])
def withdraw_funds(request):
	user = request.user
	request_data = request.data

	# for validation of currency and amount
	balance_serializer = FundsSerializer(data=request_data)
	if not balance_serializer.is_valid():
		return Response(status=HTTP_400_BAD_REQUEST, data=balance_serializer.errors)

	amount = request_data.get("amount")
	currency = request_data.get("currency")
	try:
		withdraw_funds_from_account(user=user, amount=amount, currency=currency)
	except Exception as e:
		return Response(status=HTTP_400_BAD_REQUEST, data={"detail": str(e)})

	balance = Balance.objects.only('balance').get(wallet__user=user, currency__code=currency).balance
	return Response(status=HTTP_201_CREATED, data={"balance": balance, "currency": currency})


@api_view(["POST"])
def convert_currency(request):
	# data
	# from_currency, to_currency, amount
	user = request.user
	request_data = request.data
	conversion_serializer = FundsConversionSerializer(data=request_data)
	if not conversion_serializer.is_valid():
		return Response(status=HTTP_400_BAD_REQUEST, data=conversion_serializer.data)
	from_currency = request_data.get("from_currency")
	to_currency = request_data.get("to_currency")
	amount = Decimal(request_data.get("amount"))
	try:
		convert_and_transfer_currency(
			category=OrderCategory.SELF_FUND_TRANSFER, from_user=user,
			from_currency_code=from_currency, to_currency_code=to_currency, amount=amount,
		)
	except Exception as e:
		return Response(status=HTTP_400_BAD_REQUEST, data={"detail": str(e)})

	balances = Balance.objects.filter(
		currency__code__in=[from_currency, to_currency], wallet__user=user
	).values("currency", "balance")

	return Response(status=HTTP_201_CREATED, data=balances)
