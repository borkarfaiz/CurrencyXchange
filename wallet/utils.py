import os

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


def send_monthly_statement(user, from_date, to_date):
	from .helpers import get_statement_data
	statement_data = get_statement_data(user, from_date, to_date)
	if not statement_data:
		return None
	html_string = render_to_string(
		'wallet/monthly_statement.html',
		{"statement_data": statement_data, "last_month": from_date, "user": user}
	)
	html = HTML(string=html_string)
	target = '/tmp/{}_monthly_statment.pdf'.format(user.username)
	html.write_pdf(target=target)
	month_year_str = from_date.strftime("%b-%Y")
	subject = "{}-Monthly Statement | CurrencyXchange".format(month_year_str)
	body = "Hi {}," \
		   "Please find in the attachment the Monthly statemnt for {}".format(
		user.username.title(), month_year_str
	)
	to_email = [user.email]
	send_email_with_attachment(
		subject=subject, body=body, to_email_list=to_email,
		file_to_attach_path=target
	)
	try:
		os.remove(target)
	except FileNotFoundError:
		pass
	return None
