import uuid
import csv
from datetime import datetime

# External Imports
from db_func.funcs import add_txn
from exchanges_func.utils import get_bin_hist_price, get_bybit_hist_price, convert_to_unix_v2

def map_user_id_to_pic(user_id):
        
    pic = {
        "18065187": "WD",
        "0": "Jansen",
        "0": "Vkee",
        "0": "Joshua Moh",
        "0": "Joshua Moh",
        "0": "KS",
    }    

    return pic.get(user_id)

def process_manual(csv_file_path, exchange):
    print(f"Starting to process {csv_file_path} for {exchange}")
    
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if row['Account'] == 'Spot' and row['Operation'] != 'Transaction Fee':

                # Convert UTC_Time to the format expected by add_txn
                timestamp = row['UTC_Time']
                timestamp_ms = convert_to_unix_v2(timestamp) # Used for price
                txn_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

                # Set transaction type
                txn_type_mapping = {
                    'Commission Rebate': 'Rebate', # Buy
                    'Commission History': 'Commision', # Buy
                    'Transaction Spend': 'Sell',
                    'Transaction Sold': 'Sell',
                    'Transaction Buy': 'Buy',
                    'Transaction Fee': 'Fee',
                    'Transaction Revenue': 'Revenue', # Buy
                    'Deposit': 'Deposit',
                    'Withdraw': 'Withdraw',
                    'Airdrop Assets': 'Airdrop',
                    'Referrer Commission': 'Commision',
                }
                txn_type = txn_type_mapping.get(row['Operation'], row['Operation']) # Airdrop Assets, Transfer Between Spot Account and UM Futures Account
                
                price = 0.0
                token_amount_in = abs(float(row['Change']))  # Absolute Value so no negatives
                usd_value = 0.0

                if exchange == "bybit":
                    price = get_bybit_hist_price(row['Coin'],timestamp_ms)
                elif exchange == "binance":
                    price = get_bin_hist_price(row['Coin'],timestamp_ms)

                usd_value = price * token_amount_in

                # Generate a unique exchange_id using timestamp and other info
                id_variables = f"{row['User_ID']}_{row['UTC_Time']}_{row['Operation']}_{row['Coin']}_{row['Change']}_{usd_value}"
                exchange_id = uuid.uuid5(uuid.NAMESPACE_OID, id_variables)

                print(f"Processing transaction: {exchange_id}")
                print(f"  Date: {txn_date}")
                print(f"  Coin: {row['Coin']}")
                print(f"  Type: {txn_type}")
                print(f"  Amount: {token_amount_in}")
                print(f"  Price: {price}")
                print(f"  USD Value: {usd_value}")

                add_txn(
                    exchange_id_in=str(exchange_id),
                    txn_date_in=txn_date,
                    position_in=row['Coin'],
                    txn_type_in=txn_type,
                    pic_in=map_user_id_to_pic(row['User_ID']),
                    exchange_in=exchange, 
                    token_amt_in=token_amount_in,
                    price_in=price, 
                    usd_amt_in=usd_value
                )

    print(f"Finished processing {csv_file_path} for {exchange}")
