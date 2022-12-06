from flask import request, jsonify, render_template
from service import app, db
from service.models import User, Transaction


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/get-user-by-email", methods=["GET"])
def get_user_by_email():
    usr_email = request.args.get("email")
    found_user = db.session.query(User).filter_by(email=usr_email).first()
    if found_user:
        return jsonify(user=found_user.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404


# HTTP POST - Create Record
@app.route("/add-new-user/", methods=["POST"])
def add_new_user():
    new_user = db.User(
        email=request.args.get('email'),
        password=request.args.get('pass'),
        name=request.args.get('name'),
        surname=request.args.get('surname'),
        address=request.args.get('addr'),
        phone=request.args.get('ph'),
        balance=float(0),
        verified=False
    )
    if db.add_new_user(new_user):
        return jsonify(response={"Success": f"Successfully created user with email {new_user.email}"}), 200
    else:
        return jsonify(error={"Error": f"User with email {new_user.email} could not be created"}), 400


# HTTP PUT/PATCH - Update Record
@app.route("/update-user-by-email/<string:usr_email>", methods=["PATCH"])
def update_user_by_email(usr_email):
    attribute = request.args.get('attr')
    value = request.args.get('val')
    if attribute != "password" or attribute != "name" or attribute != "surname" or attribute != "address" or attribute != "phone" or attribute != "balance" or attribute != "verified":
        return jsonify(error={"Error": f"Provided attribute '{attribute}' is not valid!"}), 400
    else:
        if db.update_user_by_email(usr_email, attribute, value):
            return jsonify(response={"Success": f"Successfully updated following attributes for user with email {usr_email} : \n {attribute} = {value}"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.route("/delete-user-by-email/<usr_email>", methods=["DELETE"])
def delete_user_by_email(usr_email):
    if db.delete_user_by_email(usr_email):
        return jsonify(response={"Success": f"Successfully deleted user with email {usr_email}"}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404

