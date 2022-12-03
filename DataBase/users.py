from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import DataBase.Errors.errors as err

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# User TABLE Configuration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    # def __init__(self, email, password, name, surname, address, phone, balance=0.0):
    #     self.email = email
    #     self.password = password,
    #     self.name = name,
    #     self.surname = surname,
    #     self.address = address,
    #     self.phone = phone,
    #     self.balance = balance,
    #     self.verified = False


def create_table():
    try:
        db.create_all()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def delete_table():
    try:
        db.drop_all()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def add_new_user(user):
    try:
        db.session.add(user)
    except Exception as e:
        print(e)
        return False
    else:
        db.session.commit()
    finally:
        return True


def get_user_by_email(query_email):
    user = db.session.query(User).filter_by(email=query_email).first()
    if user:
        return user
    else:
        raise err.UserNotFoundByEmail(query_email)


def update_user_by_email(query_email, key, value):
    user = db.session.query(User).filter_by(email=query_email).first()
    if user:
        try:
            if key == "password":
                user.password = value
            elif key == "name":
                user.name = value
            elif key == "surname":
                user.surname = value
            elif key == "address":
                user.address = value
            elif key == "phone":
                user.phone = value
            elif key == "balance":
                user.balance = value
            elif key == "verified":
                user.verified = value
            else:
                return False
        except Exception as e:
            print(e)
            return False
        else:
            db.session.commit()
            return True
    else:
        raise err.UserNotFoundByEmail(query_email)
        return False


def delete_user_by_email(query_email):
    user = db.session.query(User).filter_by(email=query_email).first()
    if user:
        try:
            db.session.delete(user)
        except Exception as e:
            print(e)
            return False
        else:
            db.session.commit()
            return True
    else:
        raise err.UserNotFoundByEmail(query_email)
        return False


def start():
    if __name__ == '__main__':
        app.run()
    # with app.app_context():
        # db.create_all()
