import json
import math
import os
from datetime import datetime, timedelta
import requests
import uuid

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

def convert_to_unix_v2(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
    timestamp_ms = int(utc_time.timestamp() * 1000)
    
    return timestamp_ms

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
    Has 4 modes:
        1. Full - Start Date is 2 years ago from current time
        2. Weekly - Start Date is 1 week ago from current time
        3. Monthly - Start Date is 4 weeks ago from current time
        4. Since2023 - Start Date is January 1, 2023
    """
    current_time_exact = datetime.now()

    # Convert the date back to a datetime object at midnight (00:00:00)
    current_date = datetime.combine(current_time_exact, datetime.min.time())

    end_date = current_date 

    # 4 Modes
    if mode == 'Full': 
        print('Getting data from current date to 2 years ago')
        start_date = end_date - timedelta(days=730)  # 2 years = 730 days
        
    elif mode == 'Weekly':
        print('Getting data from current date to 1 week ago')
        start_date = end_date - timedelta(weeks=1)

    elif mode == 'Monthly':
        print('Getting data from current date to 4 weeks ago')
        start_date = end_date - timedelta(weeks=4)

    elif mode == 'Since2023':
        print('Getting data from current date to January 1, 2023')
        start_date = datetime(2023, 1, 1)

    else:
        raise ValueError("Invalid mode. Choose 'Full', 'Weekly', 'Monthly', or 'Since2023'.")

    return start_date, end_date

def generate_custom_uuid(all_unique=False, *args):

    # Combine all arguments into a single string
    combined = '_'.join(str(arg) for arg in args)
    
    # If all_unique is True, add current timestamp to ensure uniqueness
    if all_unique:
        combined += datetime.now().isoformat()
    
    # Use the combined string to create a UUID
    return str(uuid.uuid5(uuid.NAMESPACE_OID, combined))


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

    renamed = {'MATIC': 'POL'}
    # Check if the asset needs to be renamed
    asset = renamed.get(asset, asset)
    
    # Stablecoins
    if asset in ['USDT', 'USDC', 'BUSD']:
        return 1.0
    
    # If not, fetch the price from the API
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT'
    response = requests.get(url)
    data = response.json() 

    # Convert price to float and cache it
    result = data.get('result', {})
    list_data = result.get('list', [])

    if list_data:
        lastPrice = list_data[0].get('lastPrice')
        if lastPrice is not None:
            return float(lastPrice)
    
    # Convert price to float and cache it
    price = float(data.get('price', 0.0))
    # price_cache[asset] = price
    
    return price

def get_bin_hist_price(asset, timestamp):
    # Stablecoins
    if asset in ['USDT', 'USDC', 'BUSD']:
        return 1.0

    query = f"symbol={asset}USDT&interval=1s&startTime={timestamp}&endTime={timestamp}"  # 1s interval
    url = f"https://api.binance.com/api/v3/klines?{query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data:  # If data exists
            return float(data[0][4])  # Return closing price
        else:  # If data is empty (doesn't exist for the timestamp)
            print(f"No data exists for {asset} at timestamp {timestamp}")
            return 0
    except requests.RequestException as e:
        print(f"Error fetching data for {asset} at timestamp {timestamp}: {e}")
        return 0
    except (ValueError, IndexError) as e:
        print(f"Error processing data for {asset} at timestamp {timestamp}: {e}")
        return 0


# Bybit
def get_bybit_price(asset):

    renamed = {'MATIC': 'POL'}
    
    # Check if the asset needs to be renamed
    asset = renamed.get(asset, asset)

    # Stablecoins
    if asset in ['USDT', 'USDC', 'BUSD']:
        return 1.0
    
    # If not, fetch the price from the API
    url = f'https://api.bybit.com/v5/market/tickers?category=spot&symbol={asset}USDT'
    response = requests.get(url)
    data = response.json()

    # Convert price to float and cache it
    result = data.get('result', {})
    list_data = result.get('list', [])

    if list_data:
        lastPrice = list_data[0].get('lastPrice')
        if lastPrice is not None:
            return float(lastPrice)

    # If price cannot be found
    print(f"Price for {asset} could not be found.")
    return 0
    

def get_bybit_hist_price(asset, timestamp):
    category = 'spot'

    # Stablecoins
    if asset in ['USDT', 'USDC', 'BUSD']:
        return 1.0

    query = f"symbol={asset}USDT&interval=1&category={category}&start={timestamp}&end={timestamp}"  # 1m interval
    url = f"https://api.bybit.com/v5/market/kline?{query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(data)
        
        if data.get("result", {}).get("list"):  # Check if data exists
            closing_price = float(data["result"]["list"][0][4])
            return closing_price
        else:  # If data is empty or doesn't exist for the timestamp
            print(f"No data exists for {asset} at timestamp {timestamp}")
            return 0
    except requests.RequestException as e:
        print(f"Error fetching data for {asset} at timestamp {timestamp}: {e}")
        return 0
    except (ValueError, IndexError, KeyError) as e:
        print(f"Error processing data for {asset} at timestamp {timestamp}: {e}")
        return 0

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
        "bybit_api_key": bb_api_key,
        "bybit_secret_key": bb_secret_key,
        "bin_api_key": bin_api_key,
        "bin_secret_key": bin_secret_key,
        "pic": pic.get(owner),
    }

    return owner_data