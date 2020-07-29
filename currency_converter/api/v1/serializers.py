from rest_framework import serializers

from wallet.api.v1.validators import validate_currency_code

from ...models import ConversionRate


class ConversionRateSerializer(serializers.ModelSerializer):
	base = serializers.CharField(validators=[validate_currency_code])
	to = serializers.CharField(validators=[validate_currency_code], required=False)

	class Meta:
		model = ConversionRate
		fields = ["base", "to"]
