from CryptoExchangeEngine.service import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    # balance = db.Column(db.Float, nullable=False, default=0)
    verified = db.Column(db.Boolean, nullable=False, default=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    crypto_currencies = db.relationship('CryptoCurrency', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.name}', '{self.surname}',)"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class CryptoCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    currency = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"CryptoCurrency('{self.email}', '{self.currency}', '{self.amount}',)"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(500), nullable=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    type = db.Column(db.String(10), nullable=False) # type =  DEPOSIT || WITHDRAW || VERIFY || BUY || SELL || EXCHANGE
    from_amount = db.Column(db.Float, nullable=False)
    from_currency = db.Column(db.String(30), nullable=False)
    to_amount = db.Column(db.Float, nullable=True)
    to_currency = db.Column(db.String(30), nullable=True)
    state = db.Column(db.String(15), nullable=False) # state = PROCESSING || DENIED || PROCESSED
    sender_email = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    receiver_email = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f"Transaction('{self.hash_id}', '{self.type}', '{self.state}',)"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}