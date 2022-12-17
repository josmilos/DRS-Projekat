import os
from flask import Flask, render_template, request, session, redirect, url_for
#from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests


CMC_ENDPOINT = "https://pro-api.coinmarketcap.com"
CMC_PRO_API_KEY = "a05ec627-fb01-4d24-84fb-52034219b16b"

 

template_dir = os.path.abspath('../UI/templates')

app = Flask(__name__, template_folder=template_dir)
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key="key"


def crypto_price(cryptos):
    return_price = {}
    for crypto in cryptos:
        parameters = {
            "amount": 1,
            "symbol": crypto,
            "convert": "USD",
            "CMC_PRO_API_KEY": CMC_PRO_API_KEY
        }
        response = requests.get(CMC_ENDPOINT + "/v2/tools/price-conversion", params=parameters)
        price = response.json()["data"][0]["quote"]["USD"]["price"]
        return_price[crypto] = round(price, 2)

    return return_price


@app.route('/')
def home():
    cryptos = ["BTC", "ETH", "LTC", "BNB", "DOGE"]
    cryptocurrency_prices = crypto_price(cryptos)
    # print(cryptocurrency_prices)
    return render_template("index.html", crypto=cryptocurrency_prices)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    if "user" in session:
        session.pop("user",None)
    cryptos = ["BTC", "ETH", "LTC", "BNB", "DOGE"]
    cryptocurrency_prices = crypto_price(cryptos)
    return render_template("index.html", crypto=cryptocurrency_prices)

@app.route('/profil')
def profil():
    user = session["user"]
    return render_template("profil.html", user=user)


@app.route('/credit-card', methods=["GET", "POST"])
def credit_card():
    if "user" in session:
        user = session["user"]
        return render_template("regissterCreditCard.html", user=user)
    return render_template("login.html")

@app.route('/profile/verification', methods=["GET", "POST"])
def verification():
    if "user" in session:
        user = session["user"]
        email = user["user"]["email"]
        if request.method == "POST":
            owner = str(request.form["cowner"])
            card_number = str(request.form["cnum"])
            card_date = str(request.form["cdate"])
            card_cvv = str(request.form["ccvv"])


            parameters = {
                "email": email,
                "cowner": owner,
                "cnum": card_number,
                "cdate": card_date,
                "ccvv": card_cvv
            }

            response = requests.patch("http://127.0.0.1:5000/verify-user", params=parameters)
            response.raise_for_status()
            data = response.json()
            print(data)
            user["user"]["verified"]=True
            session["user"]["verisfied"]=user


            return render_template("profil.html",user=user)
        return render_template("profil.html", user=user)
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
        response.raise_for_status()
        data = response.json()
        print(data)


@app.route('/profile/transaction-history', methods=["GET"])
def transaction_history():
    user = session["user"]
    email = user["user"]["email"]

    parameters = {
        "email": email
    }
    response = requests.get("http://127.0.0.1:5000/user-transactions", params=parameters)
    response.raise_for_status()
    data = response.json()

    print(data)


@app.route('/profile/wallet', methods=["GET"])
def wallet():
    user = session["user"]
    email = user["user"]["email"]

    parameters = {
        "email": email
    }
    response = requests.get("http://127.0.0.1:5000/user-cryptocurrencies", params=parameters)
    response.raise_for_status()
    data = response.json()

    print(data)

@app.route('/buy', methods=["GET", "POST"])
def buy():
    cryptoName=request.form["curencyName"]
    cryptoValue=request.form["curencyValue"]
    return render_template("buy.html",cryptoName=cryptoName,cryptoValue=cryptoValue)

@app.route('/buy-transaction', methods=["GET", "POST"])
def buy_transaction():
    cryptoName=request.form["curencyName"]
    cryptoValue=request.form["curencyValue"]
    amount=request.form["amount"]
    user=session["user"]
    email=user["user"]["email"]

    parameters = {
        "email": email,
        "curr": cryptoName,
        "price": cryptoValue,
        "amount": amount,

    }
    message="Successfully bought cryptocurrency"
    data=""
    try:
        response = requests.post("http://127.0.0.1:5000/buy-crypto", params=parameters)
        response.raise_for_status()
        data = response.json()
    except:
        if response.status_code == 200:
            return render_template("transactionMessage.html",message=data)
            print(data)
        elif response.status_code == 400:
            #print("User already exists")
            message="Insufficient funds. User does not have enough funds to make this purchase!"
        elif response.status_code == 500:
            #print("User not created due to server error")
            message="Server error"

    return render_template("transactionMessage.html",message=message)




@app.route('/sell-crypto', methods=["GET", "POST", "PATCH"])
def sell_crypto():
    user = session["user"]

    if request.method == "POST":
        currency = str(request.form["currency"])
        price = float(request.form["price"])
        amount = float(request.form["amount"])
        email = user["user"]["email"]

        parameters = {
            "email": email,
            "curr": currency,
            "price": price,
            "amount": amount
        }
        response = requests.patch("http://127.0.0.1:5000/sell-crypto", params=parameters)
        response.raise_for_status()
        data = response.json()

        print(data)


@app.route('/exchange', methods=["GET", "POST", "PATCH"])
def exchange():
    user = session["user"]
    email = user["user"]["email"]
    if request.method == "POST":
        selling_currency = request.form["scurr"]
        selling_price = float(request.form["sprice"])
        selling_amount = float(request.form["samount"])
        buying_currency = request.form["bcurr"]
        buying_price = float(request.form["bprice"])

        parameters = {
            "email": email,
            "scurr": selling_currency,
            "sprice": selling_price,
            "samount": selling_amount,
            "bcurr": buying_currency,
            "bprice": buying_price
        }
        response = requests.patch("http://127.0.0.1:5000/exchange-crypto", params=parameters)
        response.raise_for_status()
        data = response.json()

        print(data)


@app.route('/edit', methods=["GET", "POST", "PATCH"])
def edit():
    user = session["user"]
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
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            session["user"] = data
            user = session["user"]
            print(data)

        elif response.status_code == 500:
            print("User not updated due to server error")

        return render_template("profil.html", user=user)
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
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            session["user"] = data
            print(data)
        elif response.status_code == 400:
            print("User already exists")
        elif response.status_code == 500:
            print("User not created due to server error")
        
        return render_template("register.html")
    else:    
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if "user" in session:
        user=session["user"]
        return render_template("index.html")
    if request.method == "POST":
        
        email=request.form["email"]
        password=request.form["password"]

        parameters = {
            "email": email,
            "pass": password
        }
        try:
            response = requests.get("http://127.0.0.1:5000/login-user", params=parameters)
            response.raise_for_status()
            data = response.json()

            # if next(iter(data)) == 'response' and response.status_code == 200:
            #     if next(iter(data["response"])) == 'Success':
            #         session["user"] = data

            if response.status_code == 200:
                session["user"] = data
                print(data)
        except:
            #elif response.status_code == 401:
             #   print("Wrong Credentials")
            #elif response.status_code == 404:
            message="User not found"
            return  render_template("transactionMessage.html",message=message)


        return render_template("login.html")
    else:    
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
