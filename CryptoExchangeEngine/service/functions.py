import random
import time
import multiprocessing as mp
from CryptoExchangeEngine.service import db
from CryptoExchangeEngine.service.models import Transaction, CryptoCurrency
from Crypto.Hash import keccak
from CryptoExchangeEngine.service.creditCard import CARD_NUMBER, CARD_DATE, CARD_CVV


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
def hash_function(params):
    data = ""
    for key, value in params.items():
        data += f"{value}"
    data += str(random.randint(1, 1000))
    print("Data to be hashed: " + data)
    k = keccak.new(digest_bits=256)
    k.update(bytes(data, encoding="ascii"))
    print("Hashed data: " + k.hexdigest())
    return k.hexdigest()


# Function for processing crypto transaction on blockchain
def process_transaction(hashed_id, sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type, state):
    new_transaction = Transaction(
        hash_id=hashed_id,
        type=tr_type,
        from_amount=from_amount,
        from_currency=from_currency,
        to_amount=to_amount,
        to_currency=to_currency,
        state=state,
        sender_email=sender,
        receiver_email=receiver,
    )
    print(f"Processing transaction with hashID: {hashed_id} ")
    print(f"Currency: {from_currency} --> {to_currency}")

    db.session.add(new_transaction)
    db.session.commit()
    # After 5 minutes these actions below will be taken
    time.sleep(3)
    receiver_balance = db.session.query(CryptoCurrency).filter_by(email=receiver, currency=to_currency).first()
    if receiver_balance:
        receiver_balance.amount += to_amount
    else:
        new_currency = CryptoCurrency(
            email=receiver,
            currency=to_currency,
            amount=to_amount
        )
        db.session.add(new_currency)
    new_transaction.state = "PROCESSED"
    db.session.add(new_transaction)
    db.session.commit()

    print(f"Transaction with hashID: {hashed_id} has been processed")


def initiate_transaction(sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type, state):
    hashed_id = hash_function({"sender": sender, "receiver": receiver, "amount": from_amount})
    process_transaction(hashed_id, sender, receiver, from_amount, to_amount, from_currency, to_currency, tr_type, state)
    # p = mp.Process(target=process_transaction, args=[hashed_id, sender, receiver, amount, currency, tr_type, state])
    # p.start()