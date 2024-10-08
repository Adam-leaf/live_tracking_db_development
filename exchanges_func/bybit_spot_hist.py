# Base Imports
import hashlib
import hmac
import time
from datetime import timedelta
import urllib.parse
import json
from requests.exceptions import ConnectTimeout, RequestException

# External Imports
from exchanges_func.utils import convert_timestamp_to_date, get_bybit_price, convert_to_unix, assign_time, process_owners
from db_func.funcs import add_txn
import pandas as pd
import requests

"""
    Collects data from Exchange API and saves it into the database
    Exchange: Bybit
        1. Trade History
        2. Deposit History 
        3. Withdrawal History 
"""

# Trade History Section 
def get_bybit_trade_history(bb_api_key, bb_secret_key, category, start_time, end_time, cursor, max_retries=3, delay=5):
    url = "https://api.bybit.com/v5/execution/list"
    parse_cursor = urllib.parse.quote(cursor)

    parameters = {
        "category": category,
        "startTime": start_time,
        "endTime": end_time,
        "cursor": cursor
    }
    
    for attempt in range(max_retries):
        try:
            timestamp = str(int(time.time() * 1000))
            queryString = f"category={category}&startTime={start_time}&endTime={end_time}&cursor={parse_cursor}"
            param_str = f'{timestamp}{bb_api_key}{queryString}'
            signature = hmac.new(bb_secret_key.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()

            headers = {
                "accept": "application/json",
                'X-BAPI-SIGN': signature,
                'X-BAPI-API-KEY': bb_api_key,
                'X-BAPI-TIMESTAMP': timestamp,
            }
            
            response = requests.get(url, headers=headers, params=parameters, timeout=10)
            
            if response.status_code == 200:
                return {
                    "statusCode": 200,
                    "body": response.json()
                }
            elif response.status_code == 429:  # Rate limit exceeded
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Request failed with status code {response.status_code}. Retrying...")
                time.sleep(delay)
        
        except (ConnectTimeout, RequestException) as e:
            if attempt < max_retries - 1:
                print(f"Request failed: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "message": f"Request failed after {max_retries} attempts: {str(e)}"
                    })
                }

    return {
        "statusCode": 500,
        "body": json.dumps({
            "message": f"Request failed after {max_retries} attempts"
        })
    }

def loop_get_bybit_history(bb_api_key, bb_secret_key, category, start_date, end_date):
    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)
    print(f"Bybit: Full unix range {unix_start}, {unix_end}")

    current_start_time = start_date
    trade_history_full = []

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=1), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        print(f"Starting at {unix_start}, ending at {unix_end}") 

        cursor = ""
        trade_history_in_range = []

        while True:
            raw_history = get_bybit_trade_history(bb_api_key, bb_secret_key, category, unix_start, unix_end, cursor)

            if raw_history['statusCode'] != 200:
                print(f"Error fetching data: {raw_history['body']}")
                break

            result = raw_history.get('body', {}).get('result', {})
            cursor = result.get('nextPageCursor')

            history_list = result.get('list', [])
            trade_history_in_range.extend(history_list)

            if not cursor:
                break

        trade_history_full.extend(trade_history_in_range)
        current_start_time = current_end_time 

    return trade_history_full

def parse_bybit_hist(bybit_trade_history, owner):
    
    bybit_orders = []

    for trade in bybit_trade_history:
        
        execValue = trade.get('execPrice') # Reconfirm if execPrice or execValue will give in USD terms
        execQty = trade.get('execQty')
        usd_value = float(execValue) * float(execQty)

        order = {
            'date': convert_timestamp_to_date(trade.get('execTime')),
            'exchange_id': trade.get('execId'),
            'position': trade.get('symbol'),
            'action': trade.get('side'),
            'PIC': owner,
            'exchange': 'bybit',
            'exec_qty': execQty,
            'exec_price': execValue,
            'usd_value': usd_value
        }
    
        bybit_orders.append(order)
    
    df_bybit_orders = pd.DataFrame(bybit_orders)
    return df_bybit_orders

def get_bybit_history(bb_api_key, bb_secret_key, owner, start_date, end_date):
    raw_result = loop_get_bybit_history(bb_api_key, bb_secret_key, 'spot', start_date, end_date)
    df_parsed_hist = parse_bybit_hist(raw_result, owner)

    return df_parsed_hist


# Deposit History Section
def get_bybit_deposit(bb_api_key, bb_secret_key, start_time, end_time, cursor):

    url = "https://api.bybit.com/v5/asset/deposit/query-record"
    parse_cursor = urllib.parse.quote(cursor)

    parameters = {
        "startTime" : start_time,
        "endTime": end_time,
        "cursor": cursor
    }
    
    try:
        timestamp = str(int(time.time() * 1000))
        queryString = f"startTime={start_time}&endTime={end_time}&cursor={parse_cursor}"
        param_str = f'{timestamp}{bb_api_key}{queryString}'
        signature = hmac.new(bb_secret_key.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()

        headers = {
            "accept": "application/json",
            'X-BAPI-SIGN': signature,
            'X-BAPI-API-KEY': bb_api_key,
            'X-BAPI-TIMESTAMP': timestamp,
        }
        
        response = requests.get(url, headers=headers, params=parameters)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "statusCode": 200,
                "body": data
            }
        
    except ConnectTimeout:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Request timed out while fetching Bybit Deposit Records"
            })
        }

def get_loop_bybit_deposit(bb_api_key, bb_secret_key, start_date, end_date, cursor):

    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)
    print(f"Bybit Deposit: Full unix range {unix_start}, {unix_end}")

    # Another Loop to collect more than 7 days data
    current_start_time = start_date # Current start time for the loop
    record_history_full = []

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=30), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        #print(f"Starting at {unix_start}, ending at {unix_end}") # Debug

        # Loop Cursor
        cursor = ""
        record_in_range = []

        while True:
            raw_record = get_bybit_deposit(bb_api_key, bb_secret_key, unix_start, unix_end, cursor)
            # Parsing only to entries
            result = raw_record.get('body').get('result')
            cursor = result.get('nextPageCursor')

            if not cursor:
                break
                
            record_list = result.get('rows')
            record_in_range.extend(record_list)
        
        # Save info and update time
        record_history_full.extend(record_in_range)
        current_start_time = current_end_time 

    return record_history_full

def parse_bybit_deposits(bb_api_key, bb_secret_key, start_date, end_date, owner, cursor=""): 
    bybit_deposits = get_loop_bybit_deposit(bb_api_key, bb_secret_key, start_date, end_date, cursor)
    bybit_orders = []

    for trade in bybit_deposits:
        
        symbol = trade.get('coin') 
        price = float(get_bybit_price(symbol))
        amount = float(trade.get('amount'))

        usd_value = price * amount

        order = {
            'date': convert_timestamp_to_date(trade.get('successAt')),
            'exchange_id': trade.get('txID'),
            'position': symbol, 
            'action': 'Deposit',
            'PIC': owner,
            'exchange': 'bybit',
            'exec_qty': amount,
            'exec_price': price,
            'usd_value': usd_value
        }
    
        bybit_orders.append(order)
    
    df_bybit_orders = pd.DataFrame(bybit_orders)
    return df_bybit_orders


# Withdrawal History Section 
def get_bybit_withdraw(bb_api_key, bb_secret_key, withdraw_type, start_time, end_time, cursor):
    url = "https://api.bybit.com/v5/asset/withdraw/query-record"
    parse_cursor = urllib.parse.quote(cursor)
    withdrawType = withdraw_type # Withdraw type. 0(default): on chain. 1: off chain. 2: all

    parameters = {
        "withdrawType" : withdrawType,
        "startTime" : start_time,
        "endTime": end_time,
        "cursor": cursor
    }
    
    try:
        timestamp = str(int(time.time() * 1000))
        queryString = f"withdrawType={withdrawType}&startTime={start_time}&endTime={end_time}&cursor={parse_cursor}"
        param_str = f'{timestamp}{bb_api_key}{queryString}'
        signature = hmac.new(bb_secret_key.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()

        headers = {
            "accept": "application/json",
            'X-BAPI-SIGN': signature,
            'X-BAPI-API-KEY': bb_api_key,
            'X-BAPI-TIMESTAMP': timestamp,
        }
        
        response = requests.get(url, headers=headers, params=parameters)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "statusCode": 200,
                "body": data
            }
        
    except ConnectTimeout:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Request timed out while fetching Bybit Withdrawal Records"
            })
        }

def get_loop_bybit_withdraw(bb_api_key, bb_secret_key, withdraw_type, start_date, end_date, cursor):

    unix_start = convert_to_unix(start_date)
    unix_end = convert_to_unix(end_date)
    print(f"Bybit Withdraw: Full unix range {unix_start}, {unix_end}")

    # Another Loop to collect more than 7 days data
    current_start_time = start_date # Current start time for the loop
    record_history_full = []

    while current_start_time < end_date:
        current_end_time = min(current_start_time + timedelta(days=30), end_date)

        unix_start = convert_to_unix(current_start_time)
        unix_end = convert_to_unix(current_end_time)

        #print(f"Starting at {unix_start}, ending at {unix_end}") # Debug

        # Loop Cursor
        cursor = ""
        record_in_range = []

        while True:
            raw_record = get_bybit_withdraw(bb_api_key, bb_secret_key, withdraw_type, unix_start, unix_end, cursor)
            # Parsing only to entries
            result = raw_record.get('body').get('result')
            cursor = result.get('nextPageCursor')

            if not cursor:
                break
                
            record_list = result.get('rows')
            record_in_range.extend(record_list)
        
        # Save info and update time
        record_history_full.extend(record_in_range)
        current_start_time = current_end_time 

    return record_history_full

def parse_bybit_withdrawals(bb_api_key, bb_secret_key, start_date, end_date, owner, cursor= ""): 
    withdraw_type = 2
    bybit_withdrawals= get_loop_bybit_withdraw(bb_api_key, bb_secret_key, withdraw_type, start_date, end_date, cursor)
    bybit_orders = []

    for trade in bybit_withdrawals:
        
        symbol = trade.get('coin') 
        price = float(get_bybit_price(symbol))
        amount = float(trade.get('amount'))

        usd_value = price * amount

        order = {
            'date': convert_timestamp_to_date(trade.get('createTime')),
            'exchange_id': trade.get('txID'),
            'position': symbol, 
            'action': 'Withdraw',
            'PIC': owner,
            'exchange': 'bybit',
            'exec_qty': amount,
            'exec_price': price,
            'usd_value': usd_value
        }
    
        bybit_orders.append(order)
    
    df_bybit_orders = pd.DataFrame(bybit_orders)
    return df_bybit_orders


# Database Section
def fetch_history(owner_data, history_type, start_date, end_date):
    """Fetch history data based on the type."""
    if history_type == 'trades':
        return get_bybit_history(owner_data['bybit_api_key'], owner_data['bybit_secret_key'], owner_data['pic'], start_date, end_date)
    elif history_type == 'deposits':
        return parse_bybit_deposits(owner_data['bybit_api_key'], owner_data['bybit_secret_key'], start_date, end_date, owner_data['pic'])
    elif history_type == 'withdrawals':
        return parse_bybit_withdrawals(owner_data['bybit_api_key'], owner_data['bybit_secret_key'], start_date, end_date, owner_data['pic'])
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
def save_bybit_records(acc_owners, mode):
    """
        Save trading history for a given owner within a specified date range.

        :param acc_owners: a list of owners as seen in the .env file
        :param mode: Either "Weekly" or "Full"
    """

    start_date, end_date = assign_time(mode) # "Weekly" / "Full"
    print(start_date)
    print(end_date)

    for owner in acc_owners:

        owner_data = process_owners(owner)
        # Check if Bybit API key or secret key is "none"
        if owner_data['bybit_api_key'] == 'none' or owner_data['bybit_secret_key'] == 'none':
            print(f"Skipping owner {owner_data['pic']} due to missing Bybit API credentials")
            continue

        history_types = ['trades', 'deposits', 'withdrawals']

        for history_type in history_types:
            df = fetch_history(owner_data, history_type, start_date, end_date)
            save_to_database(df)