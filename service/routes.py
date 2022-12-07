from flask import request, jsonify, render_template
from service import app, db
from service.models import User, Transaction
from Crypto.Hash import keccak
import random


CARD_NUMBER = "4242424242424242"
CARD_DATE = "02/23"
CARD_CVV = "123"

# Implement function that checks if passed card details match with the above
def validate_card():
    pass


def hash_function(params):
    data = ""
    for key, value in params.items():
        data += f"{value};"
    print("Data to be hashed: " + data)
    k = keccak.new(digest_bits=256)
    k.update(bytes(data, encoding="ascii"))
    print("Hashed data: " + k.hexdigest())
    return k.hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/search-user-by-email", methods=["GET"])
def get_user_by_email():
    usr_email = request.args.get("email")
    found_user = db.session.query(User).filter_by(email=usr_email).first()
    if found_user:
        return jsonify(user=found_user.to_dict())
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/login-user", methods=["GET"])
def login_user():
    usr_email = request.args.get('email')
    password = request.args.get('pass')

    user = db.session.query(User).filter_by(email=usr_email).first()

    if user:
        if user.password == password:
            return jsonify(response={"Success": f"Successfully logged in to account with email {user.email}"}), 200
        else:
            return jsonify(error={"Wrong Credentials": f"Credentials for user with email {user.email} do not match"}), 401
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


# HTTP POST - Create Record
@app.route("/register-user", methods=["POST"])
def add_new_user():
    existing_user = db.session.query(User).filter_by(email=request.args.get('email')).first()
    if existing_user:
        return jsonify(error={"Error": f"Can't register because user with email {existing_user.email} already exists!"}), 400

    new_user = User(
        email=request.args.get('email'),
        password=request.args.get('pass'),
        name=request.args.get('name'),
        surname=request.args.get('surname'),
        address=request.args.get('addr'),
        phone=request.args.get('ph'),
        balance=float(0),
        verified=False
    )
    try:
        db.session.add(new_user)
    except Exception as e:
        print(e)
        return jsonify(error={"Error": f"User with email {new_user.email} could not be created"}), 400
    else:
        db.session.commit()
    finally:
        return jsonify(response={"Success": f"Successfully created user with email {new_user.email}"}), 200


# Add function which checks if CC details are valid and use it down here
@app.route("/deposit", methods=["POST"])
def deposit():
    usr_email = request.args.get("email")



# HTTP PUT/PATCH - Update Record
@app.route("/update-user-by-email", methods=["PATCH"])
def update_user_by_email():
    usr_email = request.args.get('email')
    attribute = str(request.args.get('attr'))
    value = str(request.args.get('val'))
    attributes_list = ["password", "name", "surname", "address", "phone", "balance", "verified"]
    if attribute not in attributes_list:
        return jsonify(error={"Error": f"Provided attribute '{attribute}' is not valid!"}), 400
    else:
        user = db.session.query(User).filter_by(email=usr_email).first()
        if user:
            try:
                if attribute == "password":
                    user.password = value
                elif attribute == "name":
                    user.name = value
                elif attribute == "surname":
                    user.surname = value
                elif attribute == "address":
                    user.address = value
                elif attribute == "phone":
                    user.phone = value
                elif attribute == "balance":
                    user.balance = value
                elif attribute == "verified":
                    user.verified = value
                else:
                    return jsonify(error={"Error": f"Provided attribute '{attribute}' is not valid!"}), 400
            except Exception as e:
                print(e)
                return jsonify(error={"Error": f"Sorry, we encountered error during updating user's attribute "}), 400
            else:
                db.session.commit()
            finally:
                return jsonify(response={
                    "Success": f"Successfully updated following attributes for user with email {usr_email} : '{attribute} = {value}'"}), 200
        else:
            return jsonify(
                error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404


# Add function which checks if CC details are valid and use it down here
@app.route("/verify-user", methods=["PATCH"])
def verify_user():
    usr_email = request.args.get('email')
    c_owner = request.args.get('cowner')
    c_number = request.args.get('cnum')
    c_date = request.args.get('cdate')
    c_cvv = request.args.get('ccvv')

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user.name != c_owner:
        return jsonify(error={"Error": f"Card owner does not match with this user account"}), 400
    else:
        if c_number == CARD_NUMBER and c_date == CARD_DATE and c_cvv == CARD_CVV:
            user.verified = True
            db.session.commit()
            return jsonify(response={"Success": f"Successfully verified user with email {user.email}"}), 200
        else:
            return jsonify(error={"Error": f"One of the card details provided are not valid"}), 400


# HTTP DELETE - Delete Record
@app.route("/delete-user-by-email", methods=["DELETE"])
def delete_user_by_email():
    usr_email = str(request.args.get('email'))
    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        try:
            db.session.delete(user)
        except Exception as e:
            print(e)
            return jsonify(error={"Error": f"Sorry, we encountered error during deletion of user from database"}), 400
        else:
            db.session.commit()
        finally:
            return jsonify(response={"Success": f"Successfully deleted user with email {usr_email}"}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404


# Testing purposes
# para = {
#     "sender": "petar@mail.com",
#     "receiver": "ivan@gmail.com",
#     "amount": "10",
#     "rndmint": f"{str(random.randint(0, 99))}"
# }
# #hash_function("petar@mail.com", "ivan@gmail.com", 10, random.randint(0, 99))
# hash_function(para)