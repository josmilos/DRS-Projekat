from service import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    verified = db.Column(db.Boolean, nullable=False, default=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.name}', '{self.surname}',)"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(10), nullable=False) # type = DEPOSIT || WITHDRAW
    state = db.Column(db.String(15), nullable=False) # state = PROCESSING || DENIED || PROCESSED
    sender_email = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    receiver_email = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"User('{self.hash_id}', '{self.type}', '{self.state}',)"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}