from db_func.funcs import get_as_dict, get_all, initiate
from db_func import app
from exchanges_func.exchange_master import update_db, start_calculation, convert
from flask import render_template
from flask_cors import CORS

# Enable CORS for all routes
CORS(app)

# Frontend Routes
@app.route("/", methods=["GET"])
def home():

    all_transactions = get_as_dict(lambda: get_all())
    return render_template('index.html', transactions=all_transactions)

@app.route("/view_pnl", methods=["GET"])
def view_pnl():
    
    json_portfolio = start_calculation()

    return render_template('view_pnl.html', portfolio=json_portfolio)


# Backend Routes
@app.route("/all_transaction", methods=["GET"])
def all_transaction():

    all_transactions = get_as_dict(lambda: get_all())

    return all_transactions


@app.route("/db_update", methods=["GET"])
def start_update_db():
    acc_owners = ['J', 'VKEE']
    #acc_owners = ['J', 'JM2', 'VKEE', 'KS']

    initiate()
    update_db(acc_owners,"Since2023")

    return "I am updating the database"

@app.route("/calc_pnl", methods=["GET"])
def start_calc_pnl():
    
    json_portfolio = start_calculation()

    return json_portfolio

@app.route("/manual", methods=["GET"])
def manual():
    
    convert()

    return "Updated DB Manually"