from rest_framework import serializers

from ...models import Balance, Wallet, Currency


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
	balances = BalanceSerializer(many=True, source="balance_wallet")
	preferred_currency = CurrencySerializer()

	class Meta:
		model = Wallet
		fields = ["preferred_currency", "balances"]

	def create(self, validated_data):
		pass