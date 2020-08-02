# CurrencyXchange

CurrencyXchange is a platform where you can exchange and transfer currencies all over the world.
 It includes an analytical system for the organization to analyze different things like profit and losses total sales during weekdays, etc.


## Assumptions
### User SignUp
- We don't need any kind of validation or verification of the user such as KYC.
- We don't need any information other than the username of the User.

### Balance / Wallet
- User can have only one wallet and user should have a wallet before doing any currency related operations.
- A single wallet can have multiple balance with different currencies.
    - User can't have multiple balances entries with same currency.
- If user wants to update the balance of the wallet can update it through add-funds or withdraw-funds, user directly can't update the balance.
- Tracking add-funds and withdraw funds in Order so we can include them in the statement.
- Tracking Failed Order as well.
    - for eg:- If user wants to withdraw funds and user doesn't have suffiecient funds then a Order will be created with Failed status.


### Currency
- Currency Rates in the system will be updated only once in the system at 00:00.
- The currency rates which are stored in the system will be applicable to user while transferring or converting the currencies.
- Organization will pay the cost in accordance with live currency rate.
- The Profit and Loss of the organization will be calculated based on live rates and system rates.


**[ER-Diagram link](https://viewer.diagrams.net/?page-id=R2lEEEUBdFMjLlhIrx00&highlight=0000ff&edit=_blank&layers=1&nav=1&hide-pages=1#G1VYm80M0hQ24dXnktkEFnQ5aQuTpRXsxZ)**

## Project Setup On Linux
### Python Setup
- Install Python 3.8.
```bash
sudo apt install python3.8
```

### Postgres Setup
- Install Postgresql.
```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql

```
- run psql.
```bash
sudo -u postgres psql postgres
```
- alter the password for database
    - **NOTE** "faiz@currency" is the database password which is used in django settings file.
```bash
ALTER USER postgres WITH PASSWORD 'faiz@currency';
```
- Create database.
```bash
create database currencyxchange;
```
### Pull Code
- go to the directory where you want to fetch the code.
    - **NOTE** user won't be able to fetch this repository as it is private.
```bash
git clone https://github.com/borkarfaiz/CurrencyXchange
```

### VirtaulEnv Creation and Dependencies Installation

- Install VirtualEnv.
```bash
sudo pip3 install virtualenvwrapper
```
- Add lines to .bashrc or .bashprofile
```bash
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.8
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
```
- run bash command.
- create virtualenv.
```bash
mkvirtualenv --python=/usr/bin/python3.8 currency_xchange
```
- activate virtualenv.
```bash
workon currency_xchange
```
- install depencies
```bash
pip install -r requirements.txt
```
### Celery and Redis Setup
- Redis iinstallation
```bash
wget http://download.redis.io/releases/redis-6.0.6.tar.gz
tar xzf redis-6.0.6.tar.gz
cd redis-6.0.6
make
```
- Run Redis and celery 
```bash
# run each command in different terminal tabs

# path where you have installed redis, will start redis server.
/home/faiz/Downloads/redis-6.0.6/src/redis-server

# run celery beat
celery -A CurrencyXchange beat -l info

# run celery worker
celery -A CurrencyXchange worker -l info
```
### Database Set Generation
- Download the [currencies.csv](https://drive.google.com/file/d/1XVbYBjhMPL0qA8UizyX-RrUzSa31Jb5r/view?usp=sharing)
- Run migrations command.
```bash
python manage.py migrate
```
- open shell for python.
```bash
python manage.py shell_plus --ipython
```
- generate data set.
```python
import pandas as pd

df = pd.read_csv("~/Downloads/currencies.csv")

from currency_converter.models import Currency, ConversionRate

# Creates the Currency related data in the database
bulk_create_list = [Currency(name=row["name"], code=row["code"], symbol=row["symbol"]) for idx, row in df.iterrows()]
Currency.objects.bulk_create(bulk_create_list)

# activate 33 Currency for which API is available
active_currencies = ['AUD', 'BRL', 'GBP', 'BGN', 'CAD', 'CNY', 'HRK', 'CZK', 'DKK', 'EUR', 'HKD', 'HUF','ISK', 'INR', 'IDR', 'ILS', 'JPY', 'MYR', 'MXN', 'NZD','NOK','PHP', 'PLN','RON', 'RUB','SGD', 'ZAR', 'KRW', 'SEK', 'CHF', 'THB', 'TRY', 'USD']
Currency.objects.filter(code__in=active_currencies).update(is_active=True)

# creates the conversion rates entries
currencies = [ConversionRate(base=currency, rates={}) for currency in Currency.objects.filter(is_active=True)]
ConversionRate.objects.bulk_create(currencies)

# use update_conversion_rate to update conversion rates
from currency_converter.tasks import update_conversion_rate
update_conversion_rate()
```
### Email Settings
- add EMAIL_ID and EMAIL_PASSWORD in environmental variables.
### Testing
- Running Pytest
    - pytest will give you detailed result in well formatted way.
```bash
pytest
```
- Running test from manage.py
```bash
python manage.py test
```


## Note:
**The services are only available for the currencies as listed below.**  
- **AUD, BRL, GBP, BGN, CAD, CNY, RK, CZK, DKK, EUR, HKD, HUF, ISK, INR, IDR, ILS, JPY, MYR, MXN, NZD, NOK, PHP, PLN, RON, RUB, SGD, ZAR, KRW, SEK, CHF, THB, TRY, USD.**
