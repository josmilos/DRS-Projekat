import random
import time
from multiprocessing import Process, Queue, current_process
from CryptoExchangeEngine.service.models import Transaction, Currency
from CryptoExchangeEngine.service.creditCard import CARD_NUMBER, CARD_DATE, CARD_CVV
from CryptoExchangeEngine.service import db
from Crypto.Hash import keccak

results = Queue()


def validate_card(card_number, card_date, card_cvv):
    if card_number != CARD_NUMBER:
        return False
    elif card_date != CARD_DATE:
        return False
    elif card_cvv != CARD_CVV:
        return False
    else:
        return True


# Hash function for blockchain transactions
def hash_function(params, results):
    # print("Process that is made new:", current_process().pid)
    data = ""
    for key, value in params.items():
        data += f"{value}"
    data += str(random.randint(1, 1000))
    # print("Data to be hashed: " + data)
    k = keccak.new(digest_bits=256)
    k.update(bytes(data, encoding="ascii"))
    # print("Hashed data: " + k.hexdigest())
    # return k.hexdigest()
    results.put(k.hexdigest())


# Function for processing crypto transaction on blockchain
def process_transaction(app, lock, hashed_id, sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type):
    with app.app_context():
        new_transaction = Transaction(
            hash_id=hashed_id,
            type=tr_type,
            from_amount=from_amount,
            from_currency=from_currency,
            to_amount=to_amount,
            to_currency=to_currency,
            state="PROCESSING",
            sender_email=sender,
            receiver_email=receiver,
        )
        db.session.add(new_transaction)
        db.session.commit()
        print(f"Processing transaction with hashID: {hashed_id} ")
        print(f"Currency: {from_currency} --> {to_currency}")

        # After 5 minutes these actions below will be taken
        time.sleep(30)
        print("Mining finished")
        sender_balance = db.session.query(Currency).filter_by(email=sender, currency=from_currency).first()
        receiver_balance = db.session.query(Currency).filter_by(email=receiver, currency=to_currency).first()

        if sender_balance and sender_balance.amount >= from_amount:
            lock.acquire()
            if receiver_balance:
                receiver_balance.amount += to_amount
                sender_balance.amount -= from_amount
            else:
                new_currency = Currency(
                    email=receiver,
                    currency=to_currency,
                    amount=to_amount
                )
                sender_balance.amount -= from_amount
                db.session.add(new_currency)
            new_transaction.state = "PROCESSED"
            db.session.commit()
            lock.release()
        else:
            lock.acquire()
            new_transaction.state = "DENIED"
            db.session.commit()
            lock.release()
        #db.session.add(new_transaction)

    return f"Transaction with hashID: {hashed_id} has been processed"


# sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type, state
def initiate_transaction(app, lock, sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type):
    lock.acquire()
    params = {"sender": sender, "receiver": receiver, "from_amount": from_amount}
    # print("Process before making new:", current_process().pid)
    p = Process(target=hash_function, args=[params, results])
    p.start()
    p.join()
    hashed_id = results.get()
    lock.release()
    return process_transaction(app, lock, hashed_id, sender, receiver, from_amount, to_amount, from_currency,
                               to_currency, tr_type)
