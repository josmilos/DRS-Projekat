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
    # cryptocurrency_prices = crypto_price(cryptos)
    # print(cryptocurrency_prices)
    return render_template("index.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    if "user" in session:
        session.pop("user",None)
    return render_template("index.html")

@app.route('/profil')
def profil():
    user = session["user"]
    return render_template("profil.html", user=user)

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

        response = requests.get("http://127.0.0.1:5000/login-user", params=parameters)
        response.raise_for_status()
        data = response.json()

        # if next(iter(data)) == 'response' and response.status_code == 200:
        #     if next(iter(data["response"])) == 'Success':
        #         session["user"] = data

        if response.status_code == 200:
            session["user"] = data
            print(data)
        elif response.status_code == 401:
            print("Wrong Credentials")
        elif response.status_code == 404:
            print("User not found")

        return render_template("login.html")
    else:    
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
