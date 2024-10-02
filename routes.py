from db_func.funcs import get_as_dict, get_all, initiate
from db_func import app
from exchanges_func.exchange_master import update_db, start_calculation
from flask import render_template

# Frontend Routes
@app.route("/", methods=["GET"])
def home():

    all_transactions = get_as_dict(lambda: get_all())
    return render_template('index.html', transactions=all_transactions)

# Backend Routes
@app.route("/db_update", methods=["GET"])
def start_update_db():

    initiate()
    update_db("Weekly")

    return "I am updating the database"

@app.route("/calc_pnl", methods=["GET"])
def start_calc_pnl():
    
    start_calculation()

    return "You can see me calculating PNL in the console.log"