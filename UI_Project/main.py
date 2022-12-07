import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests

 

template_dir = os.path.abspath('../UI/templates')

app = Flask(__name__, template_folder=template_dir)
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key="key"

@app.route('/')
def home():
    return render_template("index.html")





@app.route('/register', methods=["GET", "POST"])
def register():
    if "user" in session:
        user=session["user"]
        return render_template("index.html")
    if request.method == "POST":
        name=request.form["ime"]
        surname=request.form["prezime"]
        adress=request.form["adress"]
        phoneNumber=request.form["brojTelefona"]
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
        
        session["user"]=data
        print(data)
        
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
        session["user"]=data
        print(data)

        return render_template("login.html")
    else:    
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
