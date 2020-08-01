import os
from datetime import date

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML


def send_email_with_attachment(
		subject, body, to_email_list, file_to_attach_path, from_email="noreply@currencyxchange.com"
):
	email = EmailMessage(
		subject,
		body,
		from_email,
		to_email_list,
	)
	email.attach_file(file_to_attach_path)
	email.send()


def send_order_receipt(order):
	context = {
		"invoice_number": order.id,
		"invoice_date": date.today(),
		"order_time": order.transaction_datetime,
		"from_user": {
			"name": order.from_balance.wallet.user.username,
			"email": order.from_balance.wallet.user.email,
		},
		"to_user": {
			"name": order.to_balance.wallet.user.username,
			"email": order.from_balance.wallet.user.email,
		},
		"order": {
			"description": order.category,
			"base_currency": "{}{}".format(order.from_balance.currency.symbol, round(order.transfer_units, 10)),
			"rate": round(order.system_transfer_rate, 10),
			"quoted_currency": "{}{}".format(order.to_balance.currency.symbol, round(order.system_transfer_amount, 10))
		}
	}
	html_string = render_to_string('wallet/order_receipt.html', context)

	html = HTML(string=html_string)
	target = '/tmp/receipt_{}.pdf'.format(order.id)
	html.write_pdf(target=target)
	subject = "Order Receipt #{} | CurrencyXchange".format(context.get("invoice_number"))
	body = "Hi {},\n" \
		   "We have successfully processed your order, Please find the receipt in the attachment".format(
		context.get("from_user").get("name").title()
	)
	to_email = [context.get("from_user").get("email")]

	send_email_with_attachment(
		subject=subject, body=body, to_email_list=to_email,
		file_to_attach_path=target
	)
	try:
		os.remove(target)
	except FileNotFoundError:
		pass
	return None
