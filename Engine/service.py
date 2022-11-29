import os
from flask import Flask, render_template, request
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import DatabaseFunctions

template_dir = os.path.abspath('../UI/templates')

app = Flask(__name__, template_folder=template_dir)
# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
