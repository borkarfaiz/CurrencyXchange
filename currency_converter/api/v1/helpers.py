from ...models import ConversionRate


def get_conversion_rate(base, to=None):
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

	:param base: for which the currency is needed
	:param to: to which currency should be converted [it is optional]
	:return: returns the data as described in above example.
	"""
	conversion_rate_data = ConversionRate.objects.get(
		base__code=base
	)
	conversion_rate_info = {"base": base}
	if to:
		rate = conversion_rate_data.rates.get(to)
		conversion_rate_info.update({
			"to": to,
			"rate": rate,
		})
	else:
		conversion_rate_info.update({"rates": conversion_rate_data.rates})

	return conversion_rate_info
