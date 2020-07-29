from rest_framework import serializers

from currency_converter.models import Currency


def validate_currency_code(value):
	"""
	checks if borrower exist in BPE
	:param value: pan
	:return: raise error or value
	"""
	currency = Currency.objects.filter(code=value).last()
	if not currency:
		raise serializers.ValidationError("Invalid currency")
	if not currency.is_active:
		raise serializers.ValidationError("We don't support the currecncy as of now")
	return value
