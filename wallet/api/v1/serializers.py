from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from ...models import Balance, Wallet, Currency

from .validators import validate_currency_code

UserModel = get_user_model()


class CurrencySerializer(serializers.ModelSerializer):
	code = serializers.CharField(validators=[Currency.objects.filter(is_active=True)])

	class Meta:
		model = Currency
		fields = ["code", "symbol"]


class BalanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Balance
		fields = ["currency", "balance"]


class WalletSerializer(serializers.ModelSerializer):
	balances = BalanceSerializer(many=True, source="balance_wallet", required=False)
	preferred_currency = serializers.CharField(
		source="preferred_currency.code", validators=[validate_currency_code],
		required=False,
	)
	user = serializers.IntegerField(
		validators=[UniqueValidator(queryset=Wallet.objects.all(), message="Wallet already exist.")],
		required=False, write_only=True)

	class Meta:
		model = Wallet
		fields = ["preferred_currency", "balances", "user"]

	def create(self, validated_data):
		preferred_currency_code = validated_data.get("preferred_currency")
		if preferred_currency_code:
			preferred_currency = Currency.objects.get(**preferred_currency_code)
		user_id = self.validated_data.get('user')
		if preferred_currency_code:
			# if preferred_currency is provided by the user then create it with
			wallet = Wallet.objects.create(user_id=user_id, preferred_currency=preferred_currency)
		else:
			# set default currency you can see the default field in preferred currency for reference
			wallet = Wallet.objects.create(user_id=user_id)
		balance = Balance.objects.get_or_create(wallet=wallet, currency=wallet.preferred_currency)
		return wallet
