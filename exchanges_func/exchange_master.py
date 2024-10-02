from exchanges_func.binance_spot_hist import save_binance_records
from exchanges_func.calculations import calculate_pnl
from db_func.funcs import get_as_dict, get_all
import pandas as pd

def update_db(mode):
    acc_owners = ['A'] # Development
    #acc_owners = ['J', 'JM2', 'VKEE', 'KS']

    save_binance_records(acc_owners, mode)
    #save_bybit_records(acc_owners, mode)

def start_calculation():
    raw_transactions = get_as_dict(lambda: get_all())

    # Portfolio Data, is a dictionary with dataframes inside it
    portfolio_data = calculate_pnl(raw_transactions)

    # # Convert the entire portfolio_data to JSON
    # def convert_to_json_serializable(obj):
    #     if isinstance(obj, dict):
    #         return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    #     elif isinstance(obj, list):
    #         return [convert_to_json_serializable(v) for v in obj]
    #     elif isinstance(obj, pd.DataFrame):
    #         return obj.to_dict(orient='records')
    #     else:
    #         return obj

    sol_transactions = portfolio_data['Test']['binance']['SOL']['transactions']
    sol_pnl = portfolio_data['Test']['binance']['SOL']['pnl']
    sol_pnl_verification = portfolio_data['Test']['binance']['SOL']['pnl_verification']

    # You can now use these DataFrames as needed in your new file
    print()
    print(sol_transactions)
    print()
    print(sol_pnl)
    print()
    print(sol_pnl_verification)

def display_all():
    pass


# Find a way to avoid duplicates