from exchanges_func.binance_spot_hist import save_binance_records
from exchanges_func.bybit_spot_hist import save_bybit_records
from exchanges_func.calculations import calculate_pnl
from exchanges_func.manual_convert import process_manual 
from db_func.funcs import get_as_dict, get_all
import json

def update_db(acc_owners, mode):
    all_unique = False
    save_bybit_records(acc_owners, mode, all_unique)
    save_binance_records(acc_owners, mode, all_unique)

def start_calculation():
    raw_transactions = get_as_dict(lambda: get_all())
    portfolio_data_json = calculate_pnl(raw_transactions)
    portfolio_data = json.loads(portfolio_data_json)

    return portfolio_data

def convert():
    process_manual("./static/2021.csv", "binance")
    process_manual("./static/2022.csv", "binance")

def display_all():
    pass
