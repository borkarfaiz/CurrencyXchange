from django.contrib.auth import get_user_model

from rest_framework import serializers

from currency_converter.models import Currency

UserModel = get_user_model()


def validate_currency_code(currency_code):
	"""
	checks if the provided currency is activate or not
	:param currency_code: currency_code
	:return: raise error or return currency_code
	"""
	currency = Currency.objects.filter(code=currency_code).last()
	if not currency:
		raise serializers.ValidationError("Invalid currency")
	if not currency.is_active:
		raise serializers.ValidationError("We don't support the currecncy as of now")
	return currency_code


def user_exist_check(user_name):
	"""
	check if the user
	:param user_name:
	:return: raise error or return uesr_name
	"""
	try:
		user = UserModel.objects.get(username=user_name)
	except UserModel.DoesNotExist:
		raise serializers.ValidationError("user with {} username is not present in the system.".format(user_name))
	return user_name


class UniqueFieldsValidator:
	message = 'The fields {field_names} must make a unique set.'

	def __init__(self, fields, message=None):
		self.fields = fields
		self.message = message or self.message.format(fields)

	def __call__(self, attrs):
		checked_values = [
			value for field, value in attrs.items() if field in self.fields
		]
		if len(set(checked_values)) == 1:
			raise serializers.ValidationError(self.message)
