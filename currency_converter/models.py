
from datetime import date, datetime

from django.db import models

from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField

UserModel = get_user_model()


class Currency(TimeStampedModel):
	code = models.CharField(max_length=3, unique=True, db_index=True, primary_key=True)
	name = models.CharField(max_length=60, null=True)
	symbol = models.CharField(max_length=5, null=True)
	is_active = models.BooleanField(default=False)


class ConversionRate(TimeStampedModel):
	base = models.OneToOneField(Currency, on_delete=models.CASCADE)
	rates = JSONField()
	date = models.DateField(default=date.today)

	class Meta:
		unique_together = ["base", "date"]


class ConversionRateHistory(TimeStampedModel):
	base = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="converion_rate_histroy_base")
	rates = JSONField()
	date = models.DateField(default=date.today)

	class Meta:
		unique_together = ["base", "date"]