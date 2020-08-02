import calendar
import os
from datetime import date

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models.expressions import F, Func, Value as V
from django.db.models.fields import DateField, CharField
from django.db.models.functions import Cast, Concat
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Order
from .utils import send_monthly_statement, send_email_with_attachment

UserModel = get_user_model()


@periodic_task(
	run_every=crontab(day_of_month=1),
	name="send_monthly_statements_to_user",
	ignore_result=True
)
def send_monthly_statement_to_users():
	today = date.today()
	previous_month = today - relativedelta(months=1)
	month_max_date = calendar.monthrange(previous_month.year, previous_month.month)[1]
	from_date = previous_month.replace(day=1)
	to_date = previous_month.replace(day=month_max_date)
	users = UserModel.objects.all()
	for user in users:
		send_monthly_statement(user, from_date, to_date)


@task
def send_order_receipt(order_id, round_of_value=4):
	order = Order.objects.filter(
		id=order_id
	).annotate(
		invoice_number=F("id"),
		invoice_date=Cast(Func(function="Now", ), output_field=DateField()),
		order_time=F("transaction_datetime"),
		from_user_name=F("from_balance__wallet__user__username"),
		from_user_email=F("from_balance__wallet__user__email"),
		to_user_name=F("to_balance__wallet__user__username"),
		to_user_email=F("to_balance__wallet__user__email"),
		description=F("category"),
		rounded_base_amount=Func(
			F("transfer_units"),
			V(round_of_value),
			function="ROUND",
		),
		rounded_quoted_amount=Func(
			F("system_transfer_amount"),
			V(round_of_value),
			function="ROUND",
		),
		base_amount=Concat("from_balance__currency__symbol", "rounded_base_amount", output_field=CharField()),
		rate=Func(
			F("system_transfer_rate"),
			V(round_of_value),
			function="ROUND",
		),
		quoted_amount=Concat("to_balance__currency__symbol", "rounded_quoted_amount", output_field=CharField())
	).last()
	html_string = render_to_string('wallet/order_receipt.html', {"order": order})

	html = HTML(string=html_string)
	target = '/tmp/receipt_{}.pdf'.format(order_id)
	html.write_pdf(target=target)
	subject = "Order Receipt #{} | CurrencyXchange".format(order_id)
	body = "Hi {},\n" \
		   "We have successfully processed your order, Please find the receipt in the attachment".format(
		order.from_user_name.title()
	)
	to_email = [order.from_user_email]

	send_email_with_attachment(
		subject=subject, body=body, to_email_list=to_email,
		file_to_attach_path=target
	)
	try:
		os.remove(target)
	except FileNotFoundError:
		pass
	return None
