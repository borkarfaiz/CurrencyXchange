import json
from datetime import date

import requests
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from .models import ConversionRate


@periodic_task(
	run_every=crontab(minute=0, hour=0),
	name="update_conversion_rate",
	ignore_result=True
)
def update_conversion_rate():
	"""
	updates the ConversionRate for transferring the money
	:return: None
	"""
	conversion_rates_to_update = ConversionRate.objects.filter(
		base__is_active=True
	).select_related(
		'base'
	).order_by('base')
	for conversion_rate_to_update in conversion_rates_to_update:
		api_url = settings.EXCHANGE_RATE
		code = conversion_rate_to_update.base.code
		response = requests.get(url=api_url, params={"base": code})
		if response.status_code != 200:
			# NOTE should be email triggered or use sentry
			print("conversion not update for currency {}".format(code))
			continue
		response_content = response.content
		json_response = json.loads(response_content.decode("utf-8"))
		rates = json_response.get("rates")
		conversion_rate_to_update.rates = rates
		conversion_rate_to_update.date = date.today()
		conversion_rate_to_update.save()
