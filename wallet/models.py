from datetime import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models

from currency_converter.models import Currency

from model_utils.models import TimeStampedModel

UserModel = get_user_model()


def default_currency():
	return Currency.objects.get(code="INR")


class Wallet(TimeStampedModel):
	user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
	preferred_currency = models.ForeignKey(
		Currency, default=default_currency, on_delete=models.PROTECT, related_name="wallet_preferred_currency"
	)

	def __str__(self):
		return self.user.username


class Balance(TimeStampedModel):
	wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="balance_wallet")
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="balance_currency")
	balance = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)

	class Meta:
		unique_together = ["wallet", "currency"]

	def __str__(self):
		return "{} {}".format(self.wallet.user.username, self.currency.code)


class OrderType(models.TextChoices):
	FUND_TRANSFER = "FUND_TRANSFER"
	SELF_FUND_TRANSFER = "SELF_FUND_TRANSFER"
	ADD_FUNDS = "ADD_FUNDS"
	WITHDRAW_FUNDS = "WITHDRAW_FUNDS"


class OrderStatus(models.TextChoices):
	FAILED = "FAILED"
	COMPLETED = "COMPLETED"
	INITIATED = "INITIATED"


class Order(TimeStampedModel):
	from_balance = models.ForeignKey(Balance, on_delete=models.PROTECT, related_name="order_from_balance")
	to_balance = models.ForeignKey(Balance, on_delete=models.PROTECT, related_name="order_to_balance")
	from_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="order_from_currency")
	to_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="order_to_currency")
	system_transfer_rate = models.DecimalField(max_digits=20, decimal_places=10, default=1.0)
	actual_transfer_rate = models.DecimalField(max_digits=20, decimal_places=10, default=1.0)
	system_transfer_amount = models.DecimalField(max_digits=30, decimal_places=10)
	actual_transfer_amount = models.DecimalField(max_digits=30, decimal_places=10)
	transfer_units = models.DecimalField(max_digits=30, decimal_places=10)
	type = models.CharField(max_length=50, choices=OrderType.choices, default=OrderType.FUND_TRANSFER)
	transaction_id = models.CharField(max_length=40, default=uuid.uuid4, unique=True, db_index=True)
	transaction_datetime = models.DateTimeField(default=datetime.now)
	status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.INITIATED)


class BalanceHistory(TimeStampedModel):
	wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="balance_history_wallet")
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="balance_history_currency")
	balance = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)
	order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="balance_history_order")
