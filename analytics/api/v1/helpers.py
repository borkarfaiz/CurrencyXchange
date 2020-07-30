from datetime import date
from decimal import Decimal

from django.contrib.postgres.fields import JSONField
from django.db.models.aggregates import Avg, Count, Sum
from django.db.models.expressions import F, Case, When, Value as V
from django.db.models.fields import CharField
from django.db.models.query_utils import Q

from wallet.models import OrderCategory, OrderStatus, Order


def get_financial_summarization(start_date=None):
	"""
	summarize the financial loss and profit for the currency transfered
	:param start_date: from the date you need the summary
	:return: currency, type, total_amount, number_of_transactions, avg
	"""
	if not start_date:
		start_date = date.today()
	financial_summarization = Order.objects.filter(
		status=str(OrderStatus.COMPLETED), transaction_datetime__date__gte=start_date
	).exclude(
		category__in=[OrderCategory.WITHDRAW_FUNDS, OrderCategory.ADD_FUNDS]
	).annotate(
		amount=Case(
			When(
				Q(actual_transfer_amount__lt=F("system_transfer_amount")),
				then=F("system_transfer_amount") - F("actual_transfer_amount")),
			When(
				Q(actual_transfer_amount__gt=F("system_transfer_amount")),
				then=F("actual_transfer_amount") - F("system_transfer_amount")
			),
			default=Decimal(0)
		),
		type=Case(
			When(
				Q(actual_transfer_rate__gt=F("system_transfer_rate")),
				then=V("profit")
			),
			When(
				Q(actual_transfer_rate__lt=F("system_transfer_rate")),
				then=V("loss")
			),
			default=V("neutral"),
			output_field=CharField(),
		),
		currency=F("to_currency")
	).values(
		"currency", "type"
	).annotate(
		total_amount=Sum("amount"),
		number_of_transaction=Count("type"),
		avg_amount=Avg("amount"),
	).values(
		"currency", "type", "total_amount", "number_of_transaction", "avg_amount"
	)
	financial_data = {"loss": [], "profit": []}
	for financial_summary in financial_summarization:
		type = financial_summary.get('type')
		to_update = financial_data.get(type)
		financial_summary.pop("type")
		to_update.append(financial_summary)
	return financial_data


def get_average_currency_transfer_on_weekdays():
	"""
	summarrize the average transfer currencies on weekdays
	:return: week_day, currency, system_transfer_average, cost_to_organization_transfer_average
	"""
	average_currency_transfer_on_weekdays = Order.objects.filter(
		status=str(OrderStatus.COMPLETED), transaction_datetime__week_day__range=(2, 6)
	).exclude(
		category__in=[OrderCategory.WITHDRAW_FUNDS, OrderCategory.ADD_FUNDS]
	).annotate(
		week_day=Case(
			When(
				Q(transaction_datetime__week_day=2),
				then=V("Monday")
			), When(
				Q(transaction_datetime__week_day=3),
				then=V("Tuesday")
			), When(
				Q(transaction_datetime__week_day=4),
				then=V("Wednesday")
			), When(
				Q(transaction_datetime__week_day=5),
				then=V("Thursday")
			), When(
				Q(transaction_datetime__week_day=6),
				then=V("Friday")
			),
			output_field=CharField()
		),
		currency=F("from_currency"),
	).values(
		"week_day", "currency"
	).annotate(
		system_transfer_average=Avg("system_transfer_amount"),
		cost_to_organization_transfer_average=Avg("actual_transfer_amount"),
	).values(
		"week_day", "currency", "system_transfer_average", "cost_to_organization_transfer_average"
	)
	weekdays = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
	for average_currency_transfer_on_weekday in average_currency_transfer_on_weekdays:
		week_day = average_currency_transfer_on_weekday.get("week_day")
		to_update = weekdays.get(week_day)
		average_currency_transfer_on_weekday.pop("week_day")
		to_update.append(average_currency_transfer_on_weekday)
	return weekdays
