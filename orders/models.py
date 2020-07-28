import uuid

from datetime import date, datetime

from django.db import models

from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField

from wallet.models import Balance

UserModel = get_user_model()


class Currency(TimeStampedModel):
	code = models.CharField(max_length=3, unique=True, db_index=True, primary_key=True)
	name = models.CharField(max_length=60, null=True)
	symbol = models.CharField(max_length=5)
	is_active = models.BooleanField(default=False)


class ConversionRate(TimeStampedModel):
	base = models.OneToOneField(Currency, on_delete=models.CASCADE)
	rates = JSONField()
	date = models.DateField(default=date.today)


class ConversionRateHistory(TimeStampedModel):
	base = models.OneToOneField(Currency, on_delete=models.CASCADE)
	rates = JSONField()
	date = models.DateField(default=date.today)


class OrderType(models.TextChoices):
	TRANSFER = "FUND_TRANSFER"
	SELF_TRANSFER = "SELF_TRANSFER"
	ADD_MONEY = "ADD_FUNDS"
	WITHDRAW_MONEY = "WITHDRAW_FUNDS"


class Order(TimeStampedModel):
	from_balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
	to_balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
	from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	system_transfer_rate = models.DecimalField(max_length=20, decimal_places=10)
	actual_transfer_rate = models.DecimalField(max_length=20, decimal_places=10)
	system_transfer_amount = models.DecimalField(max_length=30, decimal_places=10)
	actual_transfer_amount =  models.DecimalField(max_length=30, decimal_places=10)
	transfer_units = models.DecimalField(max_length=30, decimal_places=10)
	type = models.CharField(choices=OrderType.choices, default=OrderType.TRANSFER)
	transaction_id = models.CharField(max_length=40, default=uuid.uuid4)
	transaction_datetime = models.DateTimeField(default=datetime.now)
	transaction_status = models.CharField(max_length=20, default="SUCCESS")