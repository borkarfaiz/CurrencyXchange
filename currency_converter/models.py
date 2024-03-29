from datetime import date

from django.contrib.postgres.fields import JSONField
from django.db import models

from model_utils.models import TimeStampedModel


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
