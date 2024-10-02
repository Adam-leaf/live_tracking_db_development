from db_func import db 

class Transaction (db.Model) :
    txn_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exchange_id = db.Column(db.String, unique=True, nullable=False)
    txn_date = db.Column(db.String, nullable=False)
    exchange = db.Column(db.String, nullable=False)
    pic = db.Column(db.String, nullable=False)
    position = db.Column(db.String, nullable=False) # buy / sell 
    txn_type = db.Column(db.String, nullable=False)
    token_amt = db.Column(db.Integer, nullable=False)
    token_price = db.Column(db.Integer, nullable=False)
    usd_value = db.Column(db.Integer, nullable=False)

    # what do you want to show when you print the Transaction instance
    def __repr__(self) -> str:
        return f"Transaction ID : {self.txn_id}, Exchange ID : {self.txn_id} txn_date : {self.txn_date}, exchange : {self.exchange}, pic : {self.pic}, position : {self.position}, txn_type : {self.txn_type}, token_amt : {self.token_amt}, token_price : {self.token_price}, usd_amt : {self.usd_value}"
