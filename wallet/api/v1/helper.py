from datetime import datetime

from django.db.utils import IntegrityError
from django.db import transaction

from currency_converter.models import Currency

from ...models import Balance, BalanceHistory, Wallet, Order, OrderType, OrderStatus

from .exceptions import InsufficientBalance

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
		raise Wallet.DoesNotExist("wallet for the user is not created.")
	currency = Currency.objects.get(code=currency_code)
	balance, created = Balance.objects.get_or_create(wallet=wallet, currency=currency)
	initiated_order = create_order(
		from_balance=balance, to_balance=balance, from_currency=currency, to_currency=currency,
		system_transfer_amount=amount, actual_transfer_amount=amount, transfer_units=amount,
		type=OrderType.ADD_FUNDS
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
		initiated_order.transaction_status = OrderStatus.FAILED
		initiated_order.save()
		raise transaction.TransactionManagementError("{} Failed".format(OrderType.ADD_FUNDS))


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
		type=OrderType.WITHDRAW_FUNDS
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
		raise InsufficientBalance(str(e))
	except Exception as e:
		transaction.rollback()
		initiated_order.transaction_status = OrderStatus.FAILED
		initiated_order.save()
		raise transaction.TransactionManagementError("{} Failed".format(OrderType.WITHDRAW_FUNDS))


def create_order(
		from_balance, to_balance, from_currency, to_currency,
		system_transfer_amount, actual_transfer_amount,
		transfer_units, type,
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
	:param type: type of the order
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
				type=type, system_transfer_rate=system_transfer_rate,
				actual_transfer_rate=actual_transfer_rate, transaction_datetime=transaction_datetime,
			)
		else:
			order = Order.objects.create(
				from_balance=from_balance, to_balance=to_balance, from_currency=from_currency,
				to_currency=to_currency, system_transfer_amount=system_transfer_amount,
				actual_transfer_amount=actual_transfer_amount, transfer_units=transfer_units,
				type=type, system_transfer_rate=system_transfer_rate,
				actual_transfer_rate=actual_transfer_rate, transaction_datetime=transaction_datetime,
				transaction_id=transaction_id
			)
		return order
