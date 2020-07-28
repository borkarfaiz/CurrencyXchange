from django.db import models

from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model

from orders.models import Currency, Order

UserModel = get_user_model()


def default_currency():
	return Currency.objects.get(code="INR")


class Wallet(TimeStampedModel):
	user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
	preferred_currency = models.OneToOneField(Currency, default=default_currency)


class Balance(TimeStampedModel):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="balance")
	currency = models.OneToOneField(Currency, related_name="currency")
	balance = models.DecimalField(max_length=30, decimal_places=10, default=0.0)


class BalanceHistory(TimeStampedModel):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="balance")
	currency = models.OneToOneField(Currency, related_name="currency")
	balance = models.DecimalField(max_length=30, decimal_places=10, default=0.0)
	order = models.OneToOneField(Order, related_name="balance_history")
