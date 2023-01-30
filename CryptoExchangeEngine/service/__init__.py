from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

from CryptoExchangeEngine.service import routes

# tasks = Queue()
# results = Queue()
#
# while True:
#     if not tasks.empty():
#         p = Process(target=hash_function, args=[tasks.get(), results])
#         p.start()
#     time.sleep(0.5)

