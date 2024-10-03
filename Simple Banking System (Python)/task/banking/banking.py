import random
import sqlite3

def create_db():
    with sqlite3.connect('card.s3db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY,
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0)''')

def luhn_algorithm(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def card_num():
    while True:
        card_number = "400000" + str(random.randint(0, 999999999)).zfill(9)
        checksum = sum(int(d) if i % 2 == 0 else sum(divmod(int(d) * 2, 10)) for i, d in enumerate(card_number[::-1]))
        check_digit = (10 - (checksum % 10)) % 10
        card_number += str(check_digit)
        if luhn_algorithm(card_number):
            return card_number

def new_pin():
    return str(random.randint(0, 9999)).zfill(4)

def create_account():
    card_number = card_num()
    pin = new_pin()
    with sqlite3.connect('card.s3db') as conn:
        conn.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, pin))
    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)

def add_income(card_number):
    income = int(input("Enter income:\n>"))
    with sqlite3.connect('card.s3db') as conn:
        conn.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (income, card_number))
    print("Income was added!")

def do_transfer(card_number):
    print("Transfer")
    target_card = input("Enter card number:\n>")
    if target_card == card_number:
        print("You can't transfer money to the same account!")
        return
    if not luhn_algorithm(target_card):
        print("Probably you made a mistake in the card number. Please try again!")
        return
    with sqlite3.connect('card.s3db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT balance FROM card WHERE number = ?', (target_card,))
        target_account = cur.fetchone()
        if not target_account:
            print("Such a card does not exist.")
            return
        amount = int(input("Enter how much money you want to transfer:\n>"))
        cur.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
        current_balance = cur.fetchone()[0]
        if amount > current_balance:
            print("Not enough money!")
        else:
            cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?', (amount, card_number))
            cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, target_card))
            conn.commit()
            print("Success!")

def close_account(card_number):
    with sqlite3.connect('card.s3db') as conn:
        conn.execute('DELETE FROM card WHERE number = ?', (card_number,))
    print("The account has been closed!")

def login():
    card_number = input("Enter your card number:\n>")
    pin = input("Enter your PIN:\n>")
    with sqlite3.connect('card.s3db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT balance FROM card WHERE number = ? AND pin = ?', (card_number, pin))
        account = cur.fetchone()
    if account:
        print("You have successfully logged in!")
        while True:
            print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
            choice = input(">")
            if choice == "1":
                print(f"Balance: {account[0]}")
            elif choice == "2":
                add_income(card_number)
            elif choice == "3":
                do_transfer(card_number)
            elif choice == "4":
                close_account(card_number)
                break
            elif choice == "5":
                print("You have successfully logged out!")
                break
            elif choice == "0":
                print("Bye!")
                exit()
    else:
        print("Wrong card number or PIN!")

def main():
    create_db()
    while True:
        print("1. Create an account\n2. Log into account\n0. Exit")
        choice = input(">")
        if choice == "1":
            create_account()
        elif choice == "2":
            login()
        elif choice == "0":
            print("Bye!")
            break

main()