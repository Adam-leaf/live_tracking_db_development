from db_func.models import Transaction
from db_func import db 
from sqlalchemy.exc import IntegrityError

# creating the DB, if you want to restart the database just delete the site.db file and run this. 
def initiate () : 
    db.create_all()


def add_txn(exchange_id_in, txn_date_in, position_in, txn_type_in, pic_in, exchange_in, token_amt_in, price_in, usd_amt_in):
    
    # Check if a transaction with the same exchange_id and pic already exists
    existing_txn = Transaction.query.filter_by(exchange_id=exchange_id_in, pic=pic_in, exchange = exchange_in).first()
    
    if existing_txn is None:
        new_txn = Transaction(
            exchange_id=exchange_id_in,
            txn_date=txn_date_in,
            position=position_in,
            txn_type=txn_type_in,
            pic=pic_in,
            exchange=exchange_in,
            token_amt=token_amt_in,
            token_price=price_in,
            usd_value=usd_amt_in
        )
        
        try:
            db.session.add(new_txn)
            db.session.commit()
            print(f"Added new transaction: {exchange_id_in} \nPIC: {pic_in}, with exchange: {exchange_in}")
        except IntegrityError:
            db.session.rollback()
            print(f"Duplicate transaction found: {exchange_id_in} \nPIC: {pic_in}, with exchange: {exchange_in}. Skipping.")
    else:
        print("")
        print(f"Transaction already exists: {exchange_id_in}  \nPIC: {pic_in}, with exchange: {exchange_in}. Skipping.")


def get_all():
    return Transaction.query.all() 


def get_byId (txn_id_in) : 
    return Transaction.query.filter_by(txn_id = txn_id_in).first()
    

def get_byPic (pic_in) : 
    return Transaction.query.filter_by(pic = pic_in).all()


# The two functions below are for converting the transaction model to a dictionary 
def query_to_dict(query_results):
    """
    Convert SQLAlchemy query results to a list of dictionaries.
    
    :param query_results: SQLAlchemy query results
    :return: List of dictionaries representing the query results
    """
    result_list = []
    for row in query_results:
        row_dict = {}
        for column in row.__table__.columns:
            row_dict[column.name] = getattr(row, column.name)
        result_list.append(row_dict)
    return result_list


def get_as_dict(query_func):
    """
    Execute a query function and return the results as a list of dictionaries.
    
    :param query_func: Function that returns SQLAlchemy query results
    :return: List of dictionaries representing the query results
    """
    database_contents = query_func()
    return query_to_dict(database_contents)
