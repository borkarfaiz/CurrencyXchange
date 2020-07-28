from datetime import date

from .models import ConversionRate
from django.conf import settings

import requests_async as requests
import requests


def update_coversion_rate_history():
	"""
	creates ConversionRateHistory
	:return:
	"""



def update_conversion_rate():
	"""
	updates the ConversionRate for transferring the money
	:return: None
	"""
	conversion_rates_to_update = ConversionRate.objects.filter(
		base__is_active=True
	).select_related('base')
	for conversion_rate_to_update in conversion_rates_to_update:
		api_url = settings.EXCHANGE_RATE
		response = requests.get(url=api_url, params={"base": conversion_rate_to_update.code})
		if response.status_code != 200:
			# NOTE should be email triggered or use sentry
			continue
		response_content = response.content
		conversion_rate_to_update.rate = response_content
		conversion_rate_to_update.date = date.today()
		conversion_rate_to_update.save()