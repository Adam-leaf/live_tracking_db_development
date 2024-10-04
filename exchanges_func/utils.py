import json
import math
import os
from datetime import datetime, timedelta
import requests

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def save_dataframe_to_csv(dataframe, file_path):
    try:
        dataframe.to_csv(file_path, index=False)
        print(f"DataFrame successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame to CSV: {e}")

def convert_to_unix(date_input):
    
    if isinstance(date_input, str):
        date_obj = datetime.strptime(date_input, '%Y-%m-%d')
    elif isinstance(date_input, datetime):
        date_obj = date_input
    else:
        raise ValueError("Input should be a date string or a datetime object")
    
    # Convert the datetime object to a Unix timestamp (in seconds) and then to milliseconds
    timestamp_ms = date_obj.timestamp() * 1000
    no_dec_timestamp = math.trunc(timestamp_ms)
    return no_dec_timestamp

def convert_timestamp_to_date(timestamp_ms_str):
    # Convert the string timestamp to an integer
    timestamp_ms = int(timestamp_ms_str)
    
    # Convert the timestamp from milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000
    
    # Convert the timestamp to a datetime object
    date_time = datetime.fromtimestamp(timestamp_sec)
    
    # Format the datetime object to a date-only string
    date_only = date_time.strftime('%Y-%m-%d')
    
    return date_only

def assign_time(mode):
    """
        Has 2 modes:
            1. Full - Start Date is 2 years ago from current time
            2. Weekly - Start Date is 1 week ago from current time

    """
    current_time_exact = datetime.now()

    # Convert the date back to a datetime object at midnight (00:00:00)
    current_date = datetime.combine(current_time_exact, datetime.min.time())

    end_date = current_date 

    # 2 Modes
    if mode == 'Full': 
        print('Getting data from current date to 2 years ago')
        start_date = end_date - timedelta(days=730)  # 2 years = 730 days
        
    elif mode == 'Weekly':
        print('Getting data from current date to 1 week ago')
        start_date = end_date - timedelta(weeks=1)

    elif mode == '2 Months':
        print('Getting data from current date to 8 week ago')
        start_date = end_date - timedelta(weeks=8)

    return start_date, end_date

# Binance
def get_binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    symbols = data.get('symbols')
    all_symbols = []
    valid_endings = ['USDT', 'USDC', 'ETH', 'BTC', 'BNB']

    for item in symbols:
        status = item.get('status')
        symbol = item.get('symbol')

        if status == 'TRADING':
            if any(symbol.endswith(ending) or symbol.startswith(ending) for ending in valid_endings):
                symbol_list = {
                    'symbol': symbol
                }
                all_symbols.append(symbol_list)
    
    return all_symbols

def extract_date(datetime_str):
    # Convert the string to a datetime object
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

    date_only = dt.strftime('%Y-%m-%d')
    # Return only the date part as a string
    return date_only

def get_bin_price(asset):
    # # Check if the price is already in the cache
    # if asset in price_cache:
    #     return price_cache[asset]
    
    # Stablecoins
    if asset in ['USDT', 'USDC', 'BUSD']:
        return 1.0
    
    # If not, fetch the price from the API
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT'
    response = requests.get(url)
    data = response.json() 
    
    # Convert price to float and cache it
    price = float(data.get('price', 0.0))
    # price_cache[asset] = price
    
    return price

# Owner Loop
def process_owners(owner):

    # acc_owners should be a list, ie: acc_owners = ['VKEE', 'J']

    pic = {
        "A": "Test",
        "TEST": "WD",
        "J": "Jansen",
        "VKEE": "Vkee",
        "JM": "Joshua Moh",
        "JM2": "Joshua Moh",
        "KS": "KS",
    }

    print(f'Checking Owner: {owner}')
    
    bb_api_key = os.getenv(f'{owner}_BYBIT_API_KEY', 'none')
    bb_secret_key = os.getenv(f'{owner}_BYBIT_SECRET_KEY', 'none')
    bin_api_key = os.getenv(f'{owner}_BIN_API_KEY', 'none')
    bin_secret_key = os.getenv(f'{owner}_BIN_SECRET_KEY', 'none')

    owner_data = {
        "bb_api_key": bb_api_key,
        "bb_secret_key": bb_secret_key,
        "bin_api_key": bin_api_key,
        "bin_secret_key": bin_secret_key,
        "pic": pic.get(owner),
    }

    return owner_data