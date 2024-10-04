# Base Imports
import hashlib
import hmac
import time
from datetime import timedelta

# External Imports
from exchanges_func.utils import *
from db_func.funcs import add_txn
import pandas as pd
import requests

"""
    Collects data from Exchange API and saves it into the database
    Exchange: Binance 
        1. Trade History
        2. Deposit History 
        3. Withdrawal History 
"""

# Trade History Section 
class WeightLimitExceeded(Exception):
    pass

def get_binance_trade_history(bin_api_key, bin_secret_key, start_time, end_time, symbol):
    base_url = 'https://api.binance.com'
    limit = 1000

    timestamp = int(time.time() * 1000)
    params = f'timestamp={timestamp}&limit={limit}&startTime={start_time}&endTime={end_time}&symbol={symbol}'
    signature = hmac.new(bin_secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'X-MBX-APIKEY': bin_api_key
    }

    url = f"{base_url}/api/v3/myTrades?{params}&signature={signature}"
        
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data if data else []
    elif response.status_code == 429:
        raise WeightLimitExceeded(response.json().get('msg', 'Weight limit exceeded'))
    else:
        print(f"Error: Received status code {response.status_code} for symbol {symbol} with start_time {start_time} and end_time {end_time}")
        print(response.text)
        return []

def loop_get_binance_history(bin_api_key, bin_secret_key, start_date, end_date, binance_symbols, max_retries=5, retry_delay=60):

    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)

    print(f"Binance: Full unix range {unix_start} to {unix_end}")

    current_start_time = start_date
    trade_history_full = []
    weight_used = 0
    weight_limit = 6000
    weight_reset_time = time.time() + 60  # Reset weight after 1 minute

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=1), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        print(f"Starting at {unix_start}, ending at {unix_end}")

        for symbol_item in binance_symbols:
            symbol = symbol_item.get('symbol')
            print(f"Current Symbol: {symbol}")
            
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # Check if we need to reset the weight
                    if time.time() >= weight_reset_time:
                        weight_used = 0
                        weight_reset_time = time.time() + 60

                    # Check if we have enough weight
                    if weight_used + 20 > weight_limit:
                        sleep_time = weight_reset_time - time.time()
                        print(f"Weight limit approaching. Sleeping for {sleep_time:.2f} seconds.")
                        time.sleep(max(sleep_time, 0))
                        weight_used = 0
                        weight_reset_time = time.time() + 60

                    raw_history = get_binance_trade_history(bin_api_key, bin_secret_key, unix_start, unix_end, symbol)
                    trade_history_full.extend(raw_history)
                    weight_used += 20
                    break  # Success, move to next symbol
                except WeightLimitExceeded as e:
                    print(f"Weight limit exceeded: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"Error occurred: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_count += 1

            if retry_count == max_retries:
                print(f"Failed to fetch data for {symbol} after {max_retries} attempts. Skipping...")

        current_start_time = current_end_time 

    return trade_history_full

def parse_binance_hist(binance_trade_history, owner):
    
    binance_orders = []

    for trade in binance_trade_history:
        
        price = trade.get('price') # Reconfirm if execPrice or execValue will give in USD terms
        quantity = trade.get('qty')
        usd_value = float(price) * float(quantity)
        isBuyer = trade.get('isBuyer')
        action = ''

        # Decide buy or sell
        if isBuyer is False:
            action = "Sell"
        elif isBuyer is True:
            action = "Buy"

        order = {
            'date': convert_timestamp_to_date(trade.get('time')),
            'exchange_id': trade.get('id', '0'),
            'position': trade.get('symbol'),
            'action': action, 
            'PIC': owner,
            'exchange': 'binance',
            'exec_qty': quantity,
            'exec_price': price,
            'usd_value': usd_value
        }
    
        binance_orders.append(order)
    
    df_binance_orders = pd.DataFrame(binance_orders)
    return df_binance_orders

def get_bin_history(bin_api_key, bin_secret_key, owner, start_date, end_date):

    binance_symbols = get_binance_symbols()
    raw_result = loop_get_binance_history(bin_api_key, bin_secret_key, start_date, end_date, binance_symbols)
    df_parsed_hist = parse_binance_hist(raw_result, owner)

    return df_parsed_hist      


# Deposit History Section
def get_bin_deposit(bin_api_key, bin_secret_key, start_time, end_time):

    base_url = 'https://api.binance.com'
    timestamp = int(time.time() * 1000)
    params = f'timestamp={timestamp}&startTime={start_time}&endTime={end_time}'
    signature = hmac.new(bin_secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'X-MBX-APIKEY': bin_api_key
    }

    url = f"{base_url}/sapi/v1/capital/deposit/hisrec?{params}&signature={signature}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        return data

def loop_get_bin_deposit(bin_api_key, bin_secret_key, start_date, end_date):
    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)
    print(f"Binance Deposit: Full unix range {unix_start}, {unix_end}")

    # Another Loop to collect more than 90 days data
    current_start_time = start_date # Current start time for the loop
    record_history_full = []

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=30), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        #print(f"Starting at {unix_start}, ending at {unix_end}") # Debug

        raw_record = get_bin_deposit(bin_api_key, bin_secret_key, unix_start, unix_end)
        
        # Save info and update time
        record_history_full.extend(raw_record)
        current_start_time = current_end_time 

    return record_history_full

def parse_bin_deposits(bin_api_key, bin_secret_key, owner, start_date, end_date):
    bin_raw_deposits = loop_get_bin_deposit(bin_api_key, bin_secret_key, start_date, end_date)
    binance_orders = []

    for trade in bin_raw_deposits:
        
        # Filter only completed transactions
        status = trade.get('status')
        if status != 1: 
            continue

        symbol = trade.get('coin') 
        price = float(get_bin_price(symbol))
        amount = float(trade.get('amount'))

        usd_value = price * amount

        date = convert_timestamp_to_date(trade.get('insertTime'))

        order = {
            
            'date': date,
            'exchange_id': trade.get('id'),
            'position': symbol, 
            'action': 'Deposit',
            'PIC': owner,
            'exchange': 'binance',
            'exec_qty': amount,
            'exec_price': price,
            'usd_value': usd_value
        }
    
        binance_orders.append(order)
    
    df_bybit_orders = pd.DataFrame(binance_orders)
    return df_bybit_orders


# Withdrawal History Section 
def get_bin_withdraw(bin_api_key, bin_secret_key, start_time, end_time):

    base_url = 'https://api.binance.com'
    timestamp = int(time.time() * 1000)
    params = f'timestamp={timestamp}&startTime={start_time}&endTime={end_time}'
    signature = hmac.new(bin_secret_key.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'X-MBX-APIKEY': bin_api_key
    }

    url = f"{base_url}/sapi/v1/capital/withdraw/history?{params}&signature={signature}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        return data

def loop_get_bin_withdraw(bin_api_key, bin_secret_key, start_date, end_date):
    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)
    print(f"Binance Withdrawal: Full unix range {unix_start}, {unix_end}")

    # Another Loop to collect more than 90 days data
    current_start_time = start_date # Current start time for the loop
    record_history_full = []

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=30), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        #print(f"Starting at {unix_start}, ending at {unix_end}") # Debug

        raw_record = get_bin_withdraw(bin_api_key, bin_secret_key, unix_start, unix_end)
        
        # Save info and update time
        record_history_full.extend(raw_record)
        current_start_time = current_end_time 

    return record_history_full

def parse_bin_withdrawals(bin_api_key, bin_secret_key, owner, start_date, end_date):

    bin_raw_withdrawals = loop_get_bin_withdraw(bin_api_key, bin_secret_key, start_date, end_date)

    binance_orders = []

    for trade in bin_raw_withdrawals:
        
        # Filter only completed transactions
        status = trade.get('status')
        if status != 6:
            continue

        symbol = trade.get('coin') 
        price = float(get_bin_price(symbol))
        amount = float(trade.get('amount'))

        usd_value = price * amount

        date = extract_date(trade.get('completeTime'))

        order = {
            'date': date,
            'exchange_id': trade.get('id'),
            'position': symbol, 
            'action': 'Withdraw',
            'PIC': owner,
            'exchange': 'binance',
            'exec_qty': amount,
            'exec_price': price,
            'usd_value': usd_value
        }
    
        binance_orders.append(order)
    
    df_bybit_orders = pd.DataFrame(binance_orders)
    return df_bybit_orders


# Database Section
def fetch_history(owner_data, history_type, start_date, end_date):
    """Fetch history data based on the type."""
    if history_type == 'trades':
        return get_bin_history(owner_data['bin_api_key'], owner_data['bin_secret_key'], owner_data['pic'], start_date, end_date)
    elif history_type == 'deposits':
        return parse_bin_deposits(owner_data['bin_api_key'], owner_data['bin_secret_key'], owner_data['pic'], start_date, end_date)
    elif history_type == 'withdrawals':
        return parse_bin_withdrawals(owner_data['bin_api_key'], owner_data['bin_secret_key'], owner_data['pic'], start_date, end_date)
    else:
        raise ValueError(f"Invalid history type: {history_type}")

def save_to_database(df):
    """Save the DataFrame to the database based on the history type."""
    json_hist = df.to_dict(orient='records')

    for hist in json_hist:

        add_txn(
            exchange_id_in=hist.get('exchange_id'),
            txn_date_in=hist.get('date'),
            position_in=hist.get('position'),
            txn_type_in=hist.get('action'),
            pic_in=hist.get('PIC'),
            exchange_in=hist.get('exchange'),
            token_amt_in=hist.get('exec_qty'),
            price_in=hist.get('exec_price'),
            usd_amt_in=hist.get('usd_value')
        )

# Master
def save_binance_records(acc_owners, mode):
    """
        Save trading history for a given owner within a specified date range.

        :param acc_owners: a list of owners as seen in the .env file
        :param mode: Either "Weekly" or "Full"
    """

    start_date, end_date = assign_time(mode) # "Weekly" / "Full"

    for owner in acc_owners:

        owner_data = process_owners(owner)
        history_types = ['trades', 'deposits', 'withdrawals']

        for history_type in history_types:
            df = fetch_history(owner_data, history_type, start_date, end_date)
            save_to_database(df)


# Facts
# 1. There will be a function that will collect and store 2 years data
# 2. There will be a function that will add data up to the current date.
#   - For this to work we will need to compare latest data entry to latest existing data entry. (Should have 6 types of trx)
#   - Need a query.filter for exchange and date 