import os
from flask import Flask, render_template, request, session, redirect, url_for
#from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests


CMC_ENDPOINT = "https://pro-api.coinmarketcap.com"
CMC_PRO_API_KEY = "a05ec627-fb01-4d24-84fb-52034219b16b"

SUPPORTED_ASSETS = ["USD", "BTC", "ETH", "LTC"]

template_dir = os.path.abspath('../UI/templates')

app = Flask(__name__, template_folder=template_dir)
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key="key"


# REAL-TIME CRYPTOCURRENCY PRICE LOADER
# def crypto_price(cryptos):
#     return_price = {}
#     for crypto in cryptos:
#         parameters = {
#             "amount": 1,
#             "symbol": crypto,
#             "convert": "USD",
#             "CMC_PRO_API_KEY": CMC_PRO_API_KEY
#         }
#         response = requests.get(CMC_ENDPOINT + "/v2/tools/price-conversion", params=parameters)
#         price = response.json()["data"][0]["quote"]["USD"]["price"]
#         return_price[crypto] = round(price, 2)
#
#     return return_price

def crypto_price(crypto):
    parameters = {
        "amount": crypto["amount"],
        "symbol": crypto["from"],
        "convert": crypto["to"],
        "CMC_PRO_API_KEY": CMC_PRO_API_KEY
    }
    response = requests.get(CMC_ENDPOINT + "/v2/tools/price-conversion", params=parameters)
    print(response.json())
    return response.json()["data"][0]["quote"][crypto["to"]]["price"]
    #return price

def crypto_prices(cryptos):
    return_price = {}
    for crypto in cryptos:
        # parameters = {
        #     "amount": 1,
        #     "symbol": crypto,
        #     "convert": "USD",
        #     "CMC_PRO_API_KEY": CMC_PRO_API_KEY
        # }
        # response = requests.get(CMC_ENDPOINT + "/v2/tools/price-conversion", params=parameters)
        # price = response.json()["data"][0]["quote"]["USD"]["price"]
        # return_price[crypto] = round(price, 2)
        return_price[crypto] = 100

    return return_price


@app.route('/')
def home():
    cryptos = ["BTC", "ETH", "LTC", "BNB", "DOGE"]
    cryptocurrency_prices = crypto_prices(cryptos)
    # cryptocurrency_prices = {
    #     "BTC": 17000,
    #     "ETH": 1180,
    #     "LTC": 65
    # }
    # print(cryptocurrency_prices)
    return render_template("index.html", crypto=cryptocurrency_prices)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    if "user" in session:
        session.pop("user",None)
    # cryptos = ["BTC", "ETH", "LTC", "BNB", "DOGE"]
    # cryptocurrency_prices = crypto_price(cryptos)
    cryptocurrency_prices = {
        "BTC": 17000,
        "ETH": 1180,
        "LTC": 65
    }
    return render_template("index.html", crypto=cryptocurrency_prices)


@app.route('/profile')
def profile():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()
    return render_template("profile.html", user=user)


@app.route('/credit-card', methods=["GET", "POST"])
def credit_card():
    if "user" in session:
        user = session["user"]
        return render_template("regissterCreditCard.html", user=user)
    return render_template("login.html")


@app.route('/profile/verification', methods=["GET", "POST"])
def verification():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()
        if request.method == "POST":
            owner = str(request.form["cowner"])
            card_number = str(request.form["cnum"])
            card_date = str(request.form["cdate"])
            card_cvv = str(request.form["ccvv"])


            parameters = {
                "email": user_email,
                "cowner": owner,
                "cnum": card_number,
                "cdate": card_date,
                "ccvv": card_cvv
            }

            response = requests.patch("http://127.0.0.1:5000/verify-user", params=parameters)
            try:
                response.raise_for_status()
                data = response.json()
                print(data)
            # user["user"]["verified"]=True
            # session["user"]["verisfied"]=user POTREBNO RAZJASNJENJE ####################################################
            except Exception as e:
                data2 = response.json()
                print(data2)
                return render_template("transactionMessage.html", message=data2["error"]["Error"])

            return render_template("profile.html",user=user)
        return render_template("profile.html", user=user)
    else:
        return render_template("login.html")


@app.route('/profile/deposit', methods=["GET", "POST"])
def deposit():
    user = session["user"]
    email = user["user"]["email"]
    if request.method == "POST":
        owner = str(request.form["cowner"])
        card_number = str(request.form["cnum"])
        card_date = str(request.form["cdate"])
        card_cvv = str(request.form["ccvv"])
        amount = float(request.form["amount"])

        parameters = {
            "email": email,
            "cowner": owner,
            "cnum": card_number,
            "cdate": card_date,
            "ccvv": card_cvv,
            "amount": amount
        }
        response = requests.post("http://127.0.0.1:5000/deposit", params=parameters)
        try:

            response.raise_for_status()
            data = response.json()
            print(data)
        except Exception as e:
            data2 = response.json()
            print(data2)
            return  render_template("transactionMessage.html",message=data2["error"]["Error"])
        parameters2 = {
            "email": email
        }
        user2 = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters2).json()
        return render_template("profile.html", user=user2)
    return render_template("deposit.html", user=user)


@app.route('/profile/transaction-history', methods=["GET"])
def transaction_history():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()

    # parameters = {
    #     "email": email
    # }
    response = requests.get("http://127.0.0.1:5000/user-transactions", params=parameters)
    response.raise_for_status()
    data = response.json()

    print(data)


@app.route('/user-transactions', methods=["GET", "POST"])
def user_transactions():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        response = requests.get("http://127.0.0.1:5000/user-transactions", params=parameters).json()

    return render_template("userTransactions.html",transactions=response)


@app.route('/user-transactions-filter', methods=["GET", "POST"])
def user_transactions_filter():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        filterType = request.form["filterType"]
        filterKey = request.form["filterKey"]
        parameters = {
            "email": user_email
        }
        response = requests.get("http://127.0.0.1:5000/user-transactions", params=parameters).json()

        filterList=[]
        if filterType == "email":
            for item  in response:
                if item["sender_email"] == filterKey or item["receiver_email"] == filterKey:
                    filterList.append(item)

        elif filterType == "curency":
            for item  in response:
                if item["currency"] == filterKey:
                    filterList.append(item)
        elif filterType == "transactionType":
            for item  in response:
                if item["type"] == filterKey:
                    filterList.append(item)

    return render_template("userTransactions.html",transactions=filterList)


@app.route('/profile/wallet', methods=["GET"])
def wallet():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()

    # parameters = {
    #     "email": user["user"]["email"]
    # }
    response = requests.get("http://127.0.0.1:5000/user-cryptocurrencies", params=parameters)
    try:
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        data2 = response.json()
        print(data2)
        return render_template("transactionMessage.html", message=data2["error"]["Error"])

    # Need to implement calculation of total amount in $ held in each asset and show on UI

    return render_template("wallet.html", crypto=data)


@app.route('/withdraw-form', methods=["GET", "POST"])
def withdraw_form():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user_crypto = requests.get("http://127.0.0.1:5000/user-cryptocurrencies", params=parameters).json()
    withdrawing_currency = request.form["currency"]
    balance = user_crypto[withdrawing_currency]
    return render_template("withdraw.html", currency=withdrawing_currency, balance=balance)


@app.route('/withdraw', methods=["POST"])
def withdraw():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()

    sender = user["user"]["email"]
    currency = str(request.form["curr"])
    amount = float(request.form["amount"])
    receiver = str(request.form["receiver"])

    parameters = {
        "sender": sender,
        "receiver": receiver,
        "curr": currency,
        "amount": amount
    }

    response = requests.patch("http://127.0.0.1:5000/transaction", params=parameters)
    try:
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        data2 = response.json()
        print(data2)
        return render_template("transactionMessage.html", message=data2["error"]["Error"])

    if response.status_code == 200:
        return render_template("transactionMessage.html", message=data["response"]["Success"])


@app.route('/buy-form', methods=["GET", "POST"])
def buy():
    currency=request.form["currency"]
    cryptos = [currency]
    price = crypto_prices(cryptos)[currency]
    return render_template("buy.html",currency=currency,price=price)


@app.route('/buy-crypto', methods=["GET", "POST"])
def buy_transaction():
    user = session["user"]

    currency = str(request.form["currency"]).upper()
    price = float(request.form["price"])
    to_amount = float(request.form["toamount"])
    from_amount = to_amount * float(price)
    email = user["user"]["email"]

    parameters = {
        "email": email,
        "curr": currency,
        "from_amount": from_amount,
        "to_amount": to_amount

    }
    message="Successfully bought cryptocurrency"
    data=""

    response = requests.post("http://127.0.0.1:5000/buy-crypto", params=parameters)
    try:
        response.raise_for_status()
        data = response.json()
        return render_template("transactionMessage.html", message=data["response"]["Success"])
    except Exception as e:
        data2 = response.json()
        print(data2)
        return render_template("transactionMessage.html", message=data2["error"]["Error"])





@app.route('/sell-form', methods=["GET", "POST"])
def sell_form():
    currency = request.form["currency"]
    cryptos = [currency]
    price = crypto_prices(cryptos)[currency]
    return render_template("sell.html",currency=currency,price=price)


@app.route('/sell-crypto', methods=["GET", "POST"])
def sell_crypto():
    user = session["user"]

    currency = str(request.form["currency"]).upper()
    price = float(request.form["price"])
    from_amount = float(request.form["fromamount"])
    to_amount = from_amount * float(price)

    email = user["user"]["email"]

    parameters = {
        "email": email,
        "curr": currency,
        "from_amount": from_amount,
        "to_amount": to_amount

    }

    message = "Successfully sold cryptocurrency"
    data = ""

    response = requests.patch("http://127.0.0.1:5000/sell-crypto", params=parameters)
    try:
        response.raise_for_status()
        data = response.json()
        return render_template("transactionMessage.html", message=data["response"]["Success"])
    except Exception as e:
        data2 = response.json()
        print(data2)
        return render_template("transactionMessage.html", message=data2["error"]["Error"])





@app.route('/exchange-form', methods=["GET", "POST"])
def exchange_form():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user_crypto = requests.get("http://127.0.0.1:5000/user-cryptocurrencies", params=parameters).json()
    selling_currency = request.form["currency"]
    selling_balance = user_crypto[selling_currency]
    buying_currency = [crypto for crypto in SUPPORTED_ASSETS if crypto != selling_currency]
    return render_template("exchange.html",sellingCurrency=selling_currency,sellingBalance=selling_balance, buyingCurrency=buying_currency)


@app.route('/exchange', methods=["GET", "POST", "PATCH"])
def exchange():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()
    if request.method == "POST":
        selling_currency = str(request.form["scurr"]).upper()
        selling_amount = float(request.form["samount"])
        buying_currency = str(request.form["bcurr"]).upper()

        crypto = {
            "amount": selling_amount,
            "from": selling_currency,
            "to": buying_currency
        }

        bought_amount = crypto_price(crypto)

        parameters = {
            "email": user_email,
            "scurr": selling_currency,
            "samount": selling_amount,
            "bcurr": buying_currency,
            "bamount": bought_amount
        }

        response = requests.patch("http://127.0.0.1:5000/exchange-crypto", params=parameters)
        try:
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            data2 = response.json()
            print(data2)
            return render_template("transactionMessage.html", message=data2["error"]["Error"])

        if response.status_code == 200:
            return render_template("transactionMessage.html", message=data["response"]["Success"])


@app.route('/edit', methods=["GET", "POST", "PATCH"])
def edit():
    user_email = session["user"]["user"]["email"]
    parameters = {
        "email": user_email
    }
    user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()

    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        adress = request.form["adress"]
        phoneNumber = request.form["phoneNumber"]
        email = user["user"]["email"]
        password = request.form["password"]

        parameters = {
            "email": email,
            "pass": password,
            "name": name,
            "surname": surname,
            "addr": adress,
            "ph": phoneNumber
        }

        response = requests.patch("http://127.0.0.1:5000/update-user-by-email", params=parameters)
        try:
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            data2 = response.json()
            print(data2)
            return render_template("transactionMessage.html", message=data2["error"]["Error"])

        if response.status_code == 200:
            session["user"] = data
            user = session["user"]
            print(data)



        return render_template("profile.html", user=user)
    else:
        return render_template("edit.html", user=user)


@app.route('/register', methods=["GET", "POST"])
def register():
    if "user" in session:
        user=session["user"]
        return render_template("index.html")
    if request.method == "POST":
        name=request.form["name"]
        surname=request.form["surname"]
        adress=request.form["adress"]
        phoneNumber=request.form["phoneNumber"]
        email=request.form["email"]
        password=request.form["password"]

        parameters = {
            "email": email,
            "pass": password,
            "name": name,
            "surname": surname,
            "addr": adress,
            "ph": phoneNumber
        }

        response = requests.post("http://127.0.0.1:5000/register-user", params=parameters)
        try:
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            data2 = response.json()
            print(data2)
            return render_template("transactionMessage.html", message=data2["error"]["Error"])

        if response.status_code == 200:
            session["user"] = data
            print(data)

        return render_template("register.html")
    else:    
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if "user" in session:
        user_email = session["user"]["user"]["email"]
        parameters = {
            "email": user_email
        }
        user = requests.get("http://127.0.0.1:5000/search-user-by-email", params=parameters).json()
        return redirect("/")
    if request.method == "POST":
        
        email=request.form["email"]
        password=request.form["password"]

        parameters = {
            "email": email,
            "pass": password
        }

        response = requests.get("http://127.0.0.1:5000/login-user", params=parameters)
        try:
            response.raise_for_status()
            data = response.json()

            # if next(iter(data)) == 'response' and response.status_code == 200:
            #     if next(iter(data["response"])) == 'Success':
            #         session["user"] = data

            if response.status_code == 200:
                session["user"] = data
            return redirect("/")
        except Exception as e:
            data2 = response.json()
            print(data2)
            return render_template("transactionMessage.html", message=data2["error"]["Error"])

        return render_template("login.html")
    else:    
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
