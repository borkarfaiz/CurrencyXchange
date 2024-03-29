from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from currency_converter.models import Currency

from ...models import Balance, Wallet

from .validators import user_exist_check, UniqueFieldsValidator, validate_currency_code

UserModel = get_user_model()


class BalanceSerializer(serializers.ModelSerializer):
	currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	balance = serializers.DecimalField(
		max_digits=30, decimal_places=10,
		required=False
	)
	wallet = serializers.IntegerField(
		write_only=True,
	)

	class Meta:
		model = Balance
		fields = ["currency", "balance", "wallet"]

	def create(self, validated_data):
		currency_code = validated_data.get("currency")
		currency = Currency.objects.get(**currency_code)
		wallet = self.validated_data.get('wallet')
		try:
			balance = Balance.objects.create(currency=currency, wallet_id=wallet)
		except IntegrityError:
			raise IntegrityError("balance with currency {} already exist".format(currency.code))
		return balance


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


class FundsSerializer(serializers.ModelSerializer):
	currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	amount = serializers.DecimalField(
		max_digits=30, decimal_places=10,
	)

	class Meta:
		model = Balance
		fields = ["currency", "amount"]


class FundsConversionSerializer(serializers.ModelSerializer):
	from_currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	to_currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	amount = serializers.DecimalField(
		max_digits=30, decimal_places=10,
	)

	class Meta:
		model = Balance
		fields = ["from_currency", "to_currency", "amount"]


class FundsTransferSerializer(serializers.ModelSerializer):
	from_currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	to_currency = serializers.CharField(
		source="currency.code", validators=[validate_currency_code],
	)
	from_username = serializers.CharField()
	to_username = serializers.CharField(validators=[user_exist_check])
	amount = serializers.DecimalField(
		max_digits=30, decimal_places=10,
	)

	class Meta:
		model = Balance
		fields = ["from_currency", "to_currency", "amount", "from_username", "to_username"]
		validators = [
			UniqueFieldsValidator(
				fields=['from_username', 'to_username'],
				message="to_username should be different then current user"
			)
		]