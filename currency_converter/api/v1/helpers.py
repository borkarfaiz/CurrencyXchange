from decimal import Decimal
import json
import requests

from django.conf import settings

from ...models import ConversionRate


def get_system_conversion_rates(base, to=None, only_rate=False):
	"""
	fetches the system conversion rate
	if to is not provides it will return all the conversion of currency,
	for eg:-
		{
			"base": "USD",
			"rates": {
				"INR": 74.321321312,
				"AUF": 32.323132132,
				....
			}
		}

	if to provided then will return only the specified currency
	for eg:-
		{
			"base": "USD",
			"to": "INR",
			"rate": 74.321321313
		}
	if to and only_rate bot are provided
	for eg:-
		74.313113132

	:param base: for which the currency is needed
	:param to: to which currency should be converted [it is optional]
	:param only_rate: True if only rate is required as float
	:return: returns the data as described in above example.
	"""
	conversion_rate_data = ConversionRate.objects.get(
		base__code=base
	)
	conversion_rate_info = {"base": base}
	if to:
		rate = Decimal(conversion_rate_data.rates.get(to))
		# if only conversion rate integer value required
		if only_rate:
			return rate
		conversion_rate_info.update({
			"to": to,
			"rate": rate,
		})
	else:
		conversion_rate_info.update({"rates": conversion_rate_data.rates})

	return conversion_rate_info


def get_live_conversion_rates(from_currency, to_currency):
	"""
	fetches the live currency rates from the api
	:param from_currency: which currency needs to be converted
	:param to_currency:  to which currency should be converted
	:return: rate as float value
	"""
	# documentaion link
	# https://www.currencyconverterapi.com/docs
	api_url = settings.CURRCONV_LIVE_RATE_API_URL
	api_key = settings.CURRCONV_LIVE_RATE_API_KEY
	q = "{}_{}".format(from_currency, to_currency)
	compact = "ultra"
	response = requests.get(url=api_url, params={"apiKey": api_key, "compact": compact, "q": q})
	if response.status_code != 200:
		# NOTE should be email triggered or use sentry
		print("conversion not update for currency {}".format(q))
		return None
	response_content = response.content
	json_response = json.loads(response_content.decode("utf-8"))
	rate = Decimal(json_response.get(q))
	return rate
