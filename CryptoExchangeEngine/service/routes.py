from flask import request, jsonify, render_template
from CryptoExchangeEngine.service import app, db
from CryptoExchangeEngine.service.models import User, Transaction, CryptoCurrency
from CryptoExchangeEngine.service.functions import validate_card, hash_function, initiate_transaction


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/search-user-by-email", methods=["GET"])
def get_user_by_email():
    usr_email = request.args.get("email")
    found_user = db.session.query(User).filter_by(email=usr_email).first()
    if found_user:
        return jsonify(user=found_user.to_dict()), 200
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/user-transactions", methods=["GET"])
def user_transactions():
    transactions_list = []
    usr_email = request.args.get("email")
    sender_transactions = db.session.query(Transaction).filter_by(sender_email=usr_email).all()
    receiver_transactions = db.session.query(Transaction).filter_by(receiver_email=usr_email).all()
    for trx in sender_transactions:
        temp = trx.to_dict()
        transactions_list.append(temp)
    for trx in receiver_transactions:
        temp = trx.to_dict()
        transactions_list.append(temp)
    return jsonify(transactions_list), 200



@app.route("/user-cryptocurrency-by-email-name", methods=["GET"])
def user_cryptocurrencies_by_email_name():
    owned_list = []
    usr_email = request.args.get("email")
    currency_name = request.args.get("currency_name")
    user_owned_crypto = db.session.query(CryptoCurrency).filter_by(email=usr_email).all()
    for crypto in user_owned_crypto:
        temp = crypto.to_dict()
        if str(temp["currency"]) == currency_name:
            owned_list.append({"email" : temp["email"],"currency" : temp["currency"], "amount": temp["amount"]})
    print(jsonify(owned_list))
    return jsonify(owned_list), 200


@app.route("/user-cryptocurrencies", methods=["GET"])
def user_cryptocurrencies():
    owned_currency = {}
    usr_email = request.args.get("email")
    user_owned_crypto = db.session.query(CryptoCurrency).filter_by(email=usr_email).all()
    for crypto in user_owned_crypto:
        temp = crypto.to_dict()
        if float(temp["amount"]) > 0:
            owned_currency[temp["currency"]] = temp["amount"]
    return jsonify(owned_currency), 200


@app.route("/login-user", methods=["GET"])
def login_user():
    usr_email = request.args.get('email')
    password = request.args.get('pass')

    found_user = db.session.query(User).filter_by(email=usr_email).first()

    if found_user:
        if found_user.password == password:
            return jsonify(user=found_user.to_dict()), 200
        else:
            return jsonify(
                error={"Wrong Credentials": f"Credentials for user with email {found_user.email} do not match"}), 401
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


# HTTP POST - Create Record
@app.route("/register-user", methods=["POST"])
def add_new_user():
    existing_user = db.session.query(User).filter_by(email=request.args.get('email')).first()
    if existing_user:
        return jsonify(
            error={"Error": f"Can't register because user with email {existing_user.email} already exists!"}), 400

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
        return jsonify(error={"Error": f"User with email {new_user.email} could not be created"}), 500
    else:
        db.session.commit()
    finally:
        return jsonify(user=new_user.to_dict()), 200


@app.route("/buy-crypto", methods=["POST", "PATCH"])
def buy_crypto():
    usr_email = str(request.args.get("email"))
    to_currency = str(request.args.get('curr')).upper()
    crypto_price = float(request.args.get('price'))
    from_amount = float(request.args.get('from_amount'))
    to_amount = float(request.args.get('to_amount'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        if user.verified:
            total_price = crypto_price * to_amount
            if total_price > user.balance:
                return jsonify(error={"Error": "Insufficient funds. User does not have enough funds to make this purchase!"}), 400
            else:
                user.balance -= total_price

                new_transaction = Transaction(
                    type="BUY",
                    state="PROCESSED",
                    from_currency="USD",
                    to_currency=to_currency.upper(),
                    sender_email=usr_email,
                    amount=to_amount
                )
                db.session.add(new_transaction)
                user_balance = db.session.query(CryptoCurrency).filter_by(email=usr_email,
                                                                            currency=to_currency.upper()).first()
                if user_balance:
                    user_balance.amount += to_amount
                else:
                    new_currency = CryptoCurrency(
                        email=usr_email,
                        currency=to_currency.upper(),
                        amount=to_amount
                    )

                    db.session.add(new_currency)
            db.session.commit()
            return jsonify(response={"Success": f"Successfully bought cryptocurrency {to_currency}, amount {to_amount} at price {crypto_price}"})
        else:
            return jsonify(
                error={"Error": f"This user is not verified. Crypto trades could not be made before verification!"}), 400
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/sell-crypto", methods=["POST", "PATCH"])
def sell_crypto():
    usr_email = str(request.args.get("email"))
    crypto_currency = str(request.args.get('curr')).upper()
    crypto_price = float(request.args.get('price'))
    crypto_amount = float(request.args.get('amount'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        if user.verified:
            user_balance = db.session.query(CryptoCurrency).filter_by(email=usr_email,
                                                                      currency=crypto_currency.upper()).first()
            if user_balance:
                if user_balance.amount >= crypto_amount:
                    total_price = crypto_price * crypto_amount
                    user.balance += total_price

                    new_transaction = Transaction(
                        type="SELL",
                        state="PROCESSED",
                        from_currency=crypto_currency.upper(),
                        to_currency="USD",
                        sender_email=usr_email,
                        amount=crypto_amount
                    )
                    db.session.add(new_transaction)

                    user_balance.amount -= crypto_amount
                    db.session.commit()

                    return jsonify(response={"Success": f"Successfully sold cryptocurrency {crypto_currency}, amount {crypto_amount} at price {crypto_price}"}), 200
                else:
                    return jsonify(error={
                        "Error": "Insufficient funds. User does not have enough crypto to sell!"}), 400
            else:
                return jsonify(
                    error={"Error": f"Cryptocurrency not owned. User does not own cryptocurrency {crypto_currency}!"}), 400
        else:
            return jsonify(
                error={"Error": f"This user is not verified. Crypto trades could not be made before verification!"}), 400
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/exchange-crypto", methods=["POST", "PATCH"])
def exchange_crypto():
    usr_email = str(request.args.get("email"))

    selling_crypto_currency = str(request.args.get('scurr')).upper()
    # selling_crypto_price = float(request.args.get('sprice'))
    selling_crypto_amount = float(request.args.get('samount'))

    buying_crypto_currency = str(request.args.get('bcurr')).upper()
    # buying_crypto_price = float(request.args.get('bprice'))
    buying_crypto_amount = float(request.args.get('bamount'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        if user.verified:
            selling_currency_balance = db.session.query(CryptoCurrency).filter_by(email=usr_email,
                                                                      currency=selling_crypto_currency.upper()).first()
            buying_currency_balance = db.session.query(CryptoCurrency).filter_by(email=usr_email,
                                                                                currency=buying_crypto_currency.upper()).first()
            if not selling_currency_balance:
                return jsonify(
                    error={"Error": f"Cryptocurrency not owned. User does not own cryptocurrency {selling_crypto_currency}!"}), 400
            else:
                if selling_crypto_amount > selling_currency_balance.amount:
                    return jsonify(error={
                        "Error": f"Insufficient funds. User does not have enough crypto {selling_crypto_currency}!"}), 400
                else:
                    # cash = selling_crypto_amount * selling_crypto_price
                    # exchanged_crypto = cash / buying_crypto_price
                    selling_currency_balance.amount -= selling_crypto_amount

                    # if buying_currency_balance:
                    #     buying_currency_balance.amount += buying_crypto_amount
                    # else:
                    #     new_crypto = CryptoCurrency(
                    #         email=usr_email,
                    #         currency=buying_crypto_currency.upper(),
                    #         amount=buying_crypto_amount
                    #     )
                    #     db.session.add(new_crypto)


                    # new_transaction_from = Transaction(
                    #     type="EXCHANGE",
                    #     state="PROCESSED",
                    #     currency=selling_crypto_currency,
                    #     sender_email=usr_email,
                    #     amount=selling_crypto_amount
                    # )
                    # db.session.add(new_transaction_from)
                    #
                    # new_transaction_to = Transaction(
                    #     type="EXCHANGETO",
                    #     state="PROCESSED",
                    #     currency=buying_crypto_currency,
                    #     sender_email=usr_email,
                    #     amount=exchanged_crypto
                    # )
                    # db.session.add(new_transaction_to)
                    db.session.commit()
                    initiate_transaction(usr_email, usr_email, amount, crypto_currency, tr_type="WITHDRAW",
                                         state="PROCESSING")

                    return jsonify(response={
                        "Success": f"Successfully traded cryptocurrency {selling_crypto_currency}, amount {selling_crypto_amount} for cryptocurrency {buying_crypto_currency}"}), 200
        else:
            return jsonify(
                error={"Error": f"This user is not verified. Crypto trades could not be made before verification!"}), 400
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


# HTTP PUT/PATCH - Update Record
@app.route("/update-user-by-email", methods=["PATCH"])
def update_user_by_email():
    usr_email = str(request.args.get('email'))
    usr_password = str(request.args.get('pass'))
    usr_name = str(request.args.get('name'))
    usr_surname = str(request.args.get('surname'))
    usr_address = str(request.args.get('addr'))
    usr_phone = str(request.args.get('ph'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        user_phone = db.session.query(User).filter_by(phone=usr_phone).first()
        if user_phone:
            if user_phone.email != user.email:
                return jsonify(error={"Error": "This phone is already registered. You can't use that number!"}), 400
            else:
                user.phone = usr_phone
        else:
            user.phone = usr_phone

        user.password = usr_password
        user.address = usr_address
        user.name = usr_name
        user.surname = usr_surname

        db.session.commit()
        return jsonify(user=user.to_dict()), 200
    else:
        return jsonify(
            error={"Not Found": "Sorry, user with that email address was not found in the database"}), 404


@app.route("/verify-user", methods=["POST", "PATCH"])
def verify_user():
    usr_email = str(request.args.get('email'))
    c_owner = str(request.args.get('cowner'))
    c_number = str(request.args.get('cnum'))
    c_date = str(request.args.get('cdate'))
    c_cvv = str(request.args.get('ccvv'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        if f"{user.name} {user.surname}" != c_owner:
            return jsonify(error={"Error": f"Card owner does not match with this user account"}), 400
        else:
            if validate_card(c_number, c_date, c_cvv):
                # Here should be implemented adding to the transaction database
                user.verified = True
                new_transaction = Transaction(
                    type="VERIFY",
                    state="PROCESSED",
                    currency="USD",
                    sender_email=user.email,
                    amount=1
                )
                db.session.add(new_transaction)
                db.session.commit()
                return jsonify(response={"Success": f"Successfully verified user with email {user.email}"}), 200
            else:
                return jsonify(error={"Error": f"One or more of the card details provided are not valid"}), 400
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/deposit", methods=["POST", "PATCH"])
def deposit():
    usr_email = str(request.args.get("email"))
    c_owner = str(request.args.get('cowner'))
    c_number = str(request.args.get('cnum'))
    c_date = str(request.args.get('cdate'))
    c_cvv = str(request.args.get('ccvv'))
    amount = float(request.args.get('amount'))

    user = db.session.query(User).filter_by(email=usr_email).first()
    if user:
        if user.verified:
            if f"{user.name} {user.surname}" != c_owner:
                return jsonify(error={"Error": f"Card owner does not match with this user account"}), 400
            else:
                if validate_card(c_number, c_date, c_cvv):
                    user.balance += amount
                    new_transaction = Transaction(
                        type="DEPOSIT",
                        state="PROCESSED",
                        currency="USD",
                        sender_email=user.email,
                        amount=amount
                    )
                    db.session.add(new_transaction)
                    db.session.commit()
                    return jsonify(response={"Success": f"Successfully deposited ${amount} into user account"}), 200
                else:
                    return jsonify(error={"Error": f"One or more of the card details provided are not valid"}), 400
        else:
            return jsonify(
                error={"Error": f"This user is not verified. Deposit could not be made before verification!"}), 400
    else:
        return jsonify(error={"Not Found": f"Sorry, user with email {usr_email} was not found in the database"}), 404


@app.route("/transaction", methods=["POST", "PATCH"])
def transaction():
    sender = str(request.args.get('sender'))
    receiver = str(request.args.get('receiver'))
    crypto_currency = str(request.args.get('curr')).upper()
    amount = float(request.args.get('amount'))

    user_sender = db.session.query(User).filter_by(email=sender).first()
    user_receiver = db.session.query(User).filter_by(email=receiver).first()
    if not user_sender and not user_receiver:
        return jsonify(error={"Error": "Invalid request, user(s) does not exist!"}), 400
    if user_sender.verified and user_receiver.verified:
        if sender == receiver:
            return jsonify(error={"Error": "You can not send crypto transaction to yourself!"}), 400
        elif crypto_currency != "USD":
            sender_balance = db.session.query(CryptoCurrency).filter_by(email=sender, currency=crypto_currency).first()
            if sender_balance:
                new_balance = float(sender_balance.amount) - amount
                if new_balance < 0:
                    return jsonify(error={"Error": f"Sender has insufficient balance to perform requested transaction. Requested: {amount}  Available: {sender_balance.amount}"}), 400
                else:
                    # hashed_id = hash_function({"sender": sender, "receiver": receiver, "amount": amount})
                    sender_balance.amount = new_balance
                    db.session.commit()
                    initiate_transaction(sender, receiver, amount, crypto_currency, tr_type="WITHDRAW", state="PROCESSING")
                    return jsonify(response={"Success": f"Transaction has been successfully initiated"}), 200
            else:
                return jsonify(
                    error={
                        "Error": f"Cryptocurrency not owned. User does not own cryptocurrency {crypto_currency}!"}), 400
        else:
            new_balance = float(user_sender.balance) - amount
            if new_balance < 0:
                return jsonify(error={
                    "Error": f"Sender has insufficient balance to perform requested transaction. Requested: {amount}  Available: {user_sender.balance}"}), 400
            else:
                user_sender.balance = new_balance
                new_transaction = Transaction(
                    type="WITHDRAW",
                    state="PROCESSED",
                    currency="USD",
                    sender_email=user_sender.email,
                    receiver_email=user_receiver.email,
                    amount=amount
                )
                db.session.add(new_transaction)
                user_receiver.balance += amount
                db.session.commit()
                return jsonify(
                    response={"Success": f"Transaction has been successfully processed"}), 200
    elif not user_sender.verified:
        return jsonify(error={"Error": "Sender is not verified, unverified users can not make transactions!"}), 403
    elif not user_receiver.verified:
        return jsonify(error={"Error": "Receiver is not verified, unverified users can not receive transactions!"}), 403


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

