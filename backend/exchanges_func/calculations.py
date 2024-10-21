import pandas as pd
import json
from exchanges_func.utils import get_bin_price, get_bybit_price
from datetime import datetime

""" Utility Functions """
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD
    raise TypeError(f"Type {type(obj)} not serializable")

def clean_transactions(data):
    """
    Transforms positions into only the significant token.
    Ie: SOLUSDT -> SOL
    """
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)
    
    # Function to extract the significant token
    def extract_significant_token(position):
        # If the position is already BTC or ETH, return it as is
        if position in ['BTC', 'ETH']:
            return position

        quote_currencies = ['BUSD','USDT','USDC', 'USD', 'BTC', 'ETH']
        
        # Remove quote currencies from the end of the position string
        for quote in quote_currencies:
            if position.endswith(quote):
                return position[:-len(quote)]
        
        # If no quote currency is found, return the original position
        return position
    
    # Apply the function to the 'position' column
    df['position'] = df['position'].apply(extract_significant_token)

    # Remove rows where 'position' is an empty string
    df = df[df['position'] != '']
    
    # Convert the DataFrame back to a list of dictionaries
    cleaned_data = df.to_dict('records')
    
    return cleaned_data

""" Calculations Section """
def create_df_pnl(token_name):
    df_pnl = pd.DataFrame(columns=['PnL Type', 'Position', 'Avg Buy (USD)', 'Sold Value (USD)', 'Sold Amount', 'Current Balance','USD Value','PnL'])
    df_pnl.loc[0] = ['Realized', token_name, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    df_pnl.loc[1] = ['Unrealized', token_name, 0.0, 0.0, 0.0, 0.0, 0.0,0.0]

    return df_pnl

def update_df_pnl(df_pnl, avg_buy_price, value_sold, amount_sold, current_balance, current_price):
    df_pnl.loc[df_pnl['PnL Type'] == 'Realized', 'Avg Buy (USD)'] = float(avg_buy_price)
    df_pnl.loc[df_pnl['PnL Type'] == 'Unrealized', 'Avg Buy (USD)'] = float(avg_buy_price)

    # Update Realized PNL
    df_pnl.loc[df_pnl['PnL Type'] == 'Realized', 'Sold Value (USD)'] = float(value_sold)
    df_pnl.loc[df_pnl['PnL Type'] == 'Realized', 'Sold Amount'] = float(amount_sold)
    df_pnl.loc[df_pnl['PnL Type'] == 'Realized', 'PnL'] = float(value_sold - (amount_sold * avg_buy_price))

    # Update Unrealized PNL
    df_pnl.loc[df_pnl['PnL Type'] == 'Unrealized', 'Current Balance'] = float(current_balance) # Got Negative, because no buys just sells
    df_pnl.loc[df_pnl['PnL Type'] == 'Unrealized', 'USD Value'] = float(current_balance*current_price) 
    df_pnl.loc[df_pnl['PnL Type'] == 'Unrealized', 'PnL'] = float((current_balance * current_price) - (current_balance * avg_buy_price))

    return df_pnl

def calculate_pnl(data):
    all_transactions = clean_transactions(data)
    df = pd.DataFrame(all_transactions)

    # Sort the dataframe by date
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    df = df.sort_values('txn_date')

    portfolio_structure = {}
    grouped_by_pic = df.groupby('pic')

    for pic_name, pic_group in grouped_by_pic:
        portfolio_structure['pic'] = portfolio_structure.get('pic', {})
        portfolio_structure['pic'][pic_name] = {
            'exchanges': {},
            'total_pic_pnl': 0
        }
        
        grouped_by_exchange = pic_group.groupby('exchange')
        for exchange_name, exchange_group in grouped_by_exchange:
            portfolio_structure['pic'][pic_name]['exchanges'][exchange_name] = {
                'tokens': {},
                'total_exchange_pnl': 0
            }
            
            grouped_by_token = exchange_group.groupby('position')
            for token_name, token_group in grouped_by_token:
                # Sort token_group by date
                token_group['txn_date'] = token_group['txn_date'].dt.strftime('%Y-%m-%d')

                portfolio_structure['pic'][pic_name]['exchanges'][exchange_name]['tokens'][token_name] = {
                    'transactions': json.loads(token_group.reset_index(drop=True).to_json(orient='records')),
                    'pnl': None,
                    'pnl_verification': None
                }

                df_pnl = create_df_pnl(token_name)

                amount_bought = 0.0
                value_spent = 0.0
                avg_buy_price = 0.0
                amount_sold = 0.0
                value_sold = 0.0

                for txn_type, txn_group in token_group.groupby('txn_type'):
                    if txn_type in ['Buy', 'Deposit', 'Rebate', 'Revenue', 'Commision']:
                        amount_bought += txn_group['token_amt'].sum()
                        value_spent += txn_group['usd_value'].sum()
                    elif txn_type in ['Sell', 'Withdraw', 'Fee']:
                        amount_sold += txn_group['token_amt'].sum()
                        value_sold += txn_group['usd_value'].sum()

                if amount_bought > 0:
                    avg_buy_price = value_spent / amount_bought

                current_balance = amount_bought - amount_sold
                current_price = 0

                if exchange_name == "bybit":
                    current_price = float(get_bybit_price(token_name))
                elif exchange_name == "binance":
                    current_price = float(get_bin_price(token_name))

                df_pnl_updated = update_df_pnl(df_pnl, avg_buy_price, value_sold, amount_sold, current_balance, current_price)

                portfolio_structure['pic'][pic_name]['exchanges'][exchange_name]['tokens'][token_name]['pnl'] = df_pnl_updated.to_dict(orient='records')

                curr_usd_value = current_balance * current_price
                difference = (value_sold + curr_usd_value) - value_spent

                pnl_realized = df_pnl_updated.loc[df_pnl_updated['PnL Type'] == 'Realized', 'PnL'].sum()
                pnl_unrealized = df_pnl_updated.loc[df_pnl_updated['PnL Type'] == 'Unrealized', 'PnL'].sum()
                
                pnl_total = pnl_realized + pnl_unrealized
                df_verifier = pd.DataFrame({
                    'In Amount': [value_spent],
                    'Out Amount': [value_sold],
                    'Bal USD': [curr_usd_value],
                    'Difference': [difference],
                    'Total PNL': [pnl_total]
                })

                portfolio_structure['pic'][pic_name]['exchanges'][exchange_name]['tokens'][token_name]['pnl_verification'] = df_verifier.to_dict(orient='records')

                # Update total exchange PnL
                portfolio_structure['pic'][pic_name]['exchanges'][exchange_name]['total_exchange_pnl'] += pnl_total

            # Update total PIC PnL after processing all tokens for this exchange
            portfolio_structure['pic'][pic_name]['total_pic_pnl'] += portfolio_structure['pic'][pic_name]['exchanges'][exchange_name]['total_exchange_pnl']

    return json.dumps(portfolio_structure, default=json_serial)


