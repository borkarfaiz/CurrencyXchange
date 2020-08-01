from datetime import datetime
from decimal import Decimal

from django.db.utils import IntegrityError
from django.db import transaction

from currency_converter.helpers import get_system_conversion_rates, get_live_conversion_rates
from currency_converter.models import Currency

from .exceptions import InsufficientBalance
from .models import Balance, BalanceHistory, Wallet, Order, OrderCategory, OrderStatus
from .utils import send_order_receipt


def create_order(
		from_balance, to_balance, from_currency, to_currency,
		system_transfer_amount, actual_transfer_amount,
		transfer_units, category,
		system_transfer_rate=1, actual_transfer_rate=1,
		transaction_id=None, transaction_datetime=datetime.now(),
):
	"""

	:param from_balance: Balance instance from which balance should be transferred
	:param to_balance: Balance instance to which balance should be transferred
	:param from_currency: Currency instance from currency
	:param to_currency:  Currency instance to currency
	:param system_transfer_amount:  amount transferred to user
	:param actual_transfer_amount: amount deducted from the system
	:param transfer_units: total amount transfer from base currency
	:param category: category of the order
	:param system_transfer_rate: transfer rate for the user
	:param actual_transfer_rate: transfer deducted from the system
	:param transaction_id: transaction_id of order
	:param transaction_datetime: when order was placed
	:return: order if successfully created
	"""
	with transaction.atomic():
		# to handle concurrent request
		balance = Balance.objects.select_for_update().get(id=from_balance.id)
		if transaction_id:
			transaction_exists = Order.objects.filter(transaction_id=transaction_id).exist()
			if transaction_exists:
				raise IntegrityError("Order already exist with {} transaction_id".format(transaction_id))
		if not transaction_id:
			order = Order.objects.create(
				from_balance=from_balance, to_balance=to_balance, from_currency=from_currency,
				to_currency=to_currency, system_transfer_amount=system_transfer_amount,
				actual_transfer_amount=actual_transfer_amount, transfer_units=transfer_units,
				category=category, system_transfer_rate=system_transfer_rate,
				actual_transfer_rate=actual_transfer_rate, transaction_datetime=transaction_datetime,
			)
		else:
			order = Order.objects.create(
				from_balance=from_balance, to_balance=to_balance, from_currency=from_currency,
				to_currency=to_currency, system_transfer_amount=system_transfer_amount,
				actual_transfer_amount=actual_transfer_amount, transfer_units=transfer_units,
				category=category, system_transfer_rate=system_transfer_rate,
				actual_transfer_rate=actual_transfer_rate, transaction_datetime=transaction_datetime,
				transaction_id=transaction_id
			)
		return order


def add_funds_to_account(user, amount, currency_code):
	"""
	add funds to the users wallet(balance)
	if balanced not created already will create balance entry
	:param user: The User for which the balance should be updated
	:param amount: The amount which should be added to users wallet
	:param currency_code: The code of the currency in which amount should be added in wallet
	:return: Balance instance if funds added successfully else None and will raise suited Exception,
	"""
	try:
		wallet = Wallet.objects.get(user=user)
	except Wallet.DoesNotExist:
		raise Wallet.DoesNotExist("wallet for the user {} not created.".format(user.username))
	currency = Currency.objects.get(code=currency_code)
	balance, created = Balance.objects.get_or_create(wallet=wallet, currency=currency)
	initiated_order = create_order(
		from_balance=balance, to_balance=balance, from_currency=currency, to_currency=currency,
		system_transfer_amount=amount, actual_transfer_amount=amount, transfer_units=amount,
		category=OrderCategory.ADD_FUNDS
	)
	try:
		with transaction.atomic():
			balance = Balance.objects.select_for_update().get(id=balance.id)
			balance.balance += amount
			balance.save()
			initiated_order.status = OrderStatus.COMPLETED
			initiated_order.save()
			BalanceHistory.objects.create(
				order=initiated_order, wallet=wallet, balance=balance.balance, currency=currency,
			)
			return balance

	except Exception as e:
		transaction.rollback()
		initiated_order.status = OrderStatus.FAILED
		initiated_order.save()
		raise transaction.TransactionManagementError("{} Failed".format(OrderCategory.ADD_FUNDS))


def withdraw_funds_from_account(user, amount, currency_code):
	"""
	withdraw funds to the users wallet(balance)
	if balanced not created already will create balance entry
	:param user: The User for which the balance should be updated
	:param amount: The amount which should be added to users wallet
	:param currency_code: The code of the currency in which amount should be added in wallet
	:return: Balance instance if funds added successfully else None and will raise suited Exception,
	"""
	try:
		wallet = Wallet.objects.get(user=user)
	except Wallet.DoesNotExist:
		raise Wallet.DoesNotExist("wallet for the user is not created.")
	currency = Currency.objects.get(code=currency_code)
	try:
		balance = Balance.objects.get(wallet=wallet, currency=currency)
	except Balance.DoesNotExist:
		raise Wallet.DoesNotExist("There is no funds for the provided currency")
	initiated_order = create_order(
		from_balance=balance, to_balance=balance, from_currency=currency, to_currency=currency,
		system_transfer_amount=amount, actual_transfer_amount=amount, transfer_units=amount,
		category=OrderCategory.WITHDRAW_FUNDS
	)
	try:
		with transaction.atomic():
			balance = Balance.objects.select_for_update().get(id=balance.id)
			balance.balance -= amount
			if balance.balance < 0:
				raise InsufficientBalance("Insufficient Funds")
			balance.save()
			initiated_order.status = OrderStatus.COMPLETED
			initiated_order.save()
			BalanceHistory.objects.create(
				order=initiated_order, wallet=wallet, balance=balance.balance, currency=currency,
			)
			return balance
	except InsufficientBalance as e:
		initiated_order.status = OrderStatus.FAILED
		initiated_order.save()
		raise InsufficientBalance(str(e))
	except Exception as e:
		transaction.rollback()
		initiated_order.status = OrderStatus.FAILED
		initiated_order.save()
		raise transaction.TransactionManagementError("{} Failed".format(OrderCategory.WITHDRAW_FUNDS))


def get_system_transfer_amount_and_rate(from_currency_code, to_currency_code, transfer_units):
	"""
	fetches the system rates and calculates the cost to user amount
	:param from_currency_code: base currency
	:param to_currency_code: destination currency
	:param transfer_units: amount to transfer in base currency
	:return: system_transfer_rate, system_transfer_rate
	"""
	system_transfer_rate = get_system_conversion_rates(base=from_currency_code, to=to_currency_code, only_rate=True)
	system_transfer_amount = transfer_units * system_transfer_rate
	return system_transfer_amount, system_transfer_rate


def get_live_transfer_amount_and_rate(from_currency_code, to_currency_code, transfer_units):
	"""
	fetches the live rates and calculates the cost to organization
	:param from_currency_code: base currency
	:param to_currency_code: destination currency
	:param transfer_units: amount to transfer in base currency
	:return:
	"""
	live_transfer_rate = get_live_conversion_rates(from_currency=from_currency_code, to_currency=to_currency_code)
	live_transfer_amount = transfer_units * live_transfer_rate
	return live_transfer_amount, live_transfer_rate


def convert_and_transfer_currency(
		category, from_user, from_currency_code, to_currency_code, amount,
		to_user=None,
):
	if category == OrderCategory.SELF_FUND_TRANSFER and to_user is None:
		to_user = from_user
	try:
		from_wallet = Wallet.objects.get(user=from_user)
	except Wallet.DoesNotExist:
		raise Wallet.DoesNotExist("Wallet for user {} not created".format(from_user.username))
	try:
		to_wallet = Wallet.objects.get(user=to_user)
	except Wallet.DoesNotExist:
		raise Wallet.DoesNotExist("Wallet for user {} not created".format(to_user.username))
	from_currency = Currency.objects.get(code=from_currency_code)
	to_currency = Currency.objects.get(code=to_currency_code)

	from_balance, created = Balance.objects.get_or_create(wallet=from_wallet, currency=from_currency)
	to_balance, created = Balance.objects.get_or_create(wallet=to_wallet, currency=to_currency)

	if from_currency != to_currency:
		system_transfer_amount, system_transfer_rate = get_system_transfer_amount_and_rate(
			from_currency_code, to_currency_code, amount
		)
		actual_transfer_amount, actual_transfer_rate = get_live_transfer_amount_and_rate(
			from_currency_code, to_currency_code, amount
		)
	# if sending and receiving currency is same we don't need to convert the currency
	else:
		system_transfer_rate = actual_transfer_rate = Decimal(1)
		system_transfer_amount = actual_transfer_amount = amount

	initiated_order = create_order(
		from_balance=from_balance, to_balance=to_balance, from_currency=from_currency, to_currency=to_currency,
		system_transfer_amount=system_transfer_amount, system_transfer_rate=system_transfer_rate,
		actual_transfer_amount=actual_transfer_amount, actual_transfer_rate=actual_transfer_rate,
		transfer_units=amount, category=category
	)
	try:
		with transaction.atomic():
			from_balance = Balance.objects.select_for_update().get(id=from_balance.id)
			to_balance = Balance.objects.select_for_update().get(id=to_balance.id)
			from_balance.balance -= amount
			if from_balance.balance < 0:
				raise InsufficientBalance("Insufficient funds")
			to_balance.balance += system_transfer_amount
			from_balance.save()
			to_balance.save()
			initiated_order.status = OrderStatus.COMPLETED
			initiated_order.save()
			BalanceHistory.objects.create(
				order=initiated_order, wallet=from_wallet, balance=from_balance.balance, currency=from_currency,
			)
			BalanceHistory.objects.create(
				order=initiated_order, wallet=to_wallet, balance=to_balance.balance, currency=to_currency,
			)
			send_order_receipt(initiated_order)
			return initiated_order
	except InsufficientBalance as e:
		initiated_order.status = OrderStatus.FAILED
		initiated_order.save()
		raise InsufficientBalance(str(e))
	except Exception as e:
		transaction.rollback()
		initiated_order.status = OrderStatus.FAILED
		initiated_order.save()
		raise transaction.TransactionManagementError("{} Failed".format(OrderCategory.WITHDRAW_FUNDS))
