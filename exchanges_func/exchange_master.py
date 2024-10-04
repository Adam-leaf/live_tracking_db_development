from exchanges_func.binance_spot_hist import save_binance_records
from exchanges_func.calculations import calculate_pnl
from db_func.funcs import get_as_dict, get_all
import pandas as pd
import json

def update_db(acc_owners, mode):

    save_binance_records(acc_owners, mode)
    #save_bybit_records(acc_owners, mode)

def start_calculation():
    raw_transactions = get_as_dict(lambda: get_all())
    portfolio_data_json = calculate_pnl(raw_transactions)
    portfolio_data = json.loads(portfolio_data_json)

    return portfolio_data

def display_all():
    pass
