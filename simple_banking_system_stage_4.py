import random
import sqlite3


def connect_db():
    con = sqlite3.connect('card.s3db')
    return con


def create_db():
    con = sqlite3.connect('card.s3db')
    cur = con.cursor()
    cur.executescript('''
CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY AUTOINCREMENT,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
);
''')
    con.commit()
    con.close()

def select_all(connection):
    cur = connection.cursor()
    cur.execute('SELECT * FROM card;')
    return cur.fetchall()

def select_one(query, connection):
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchone()

def insert_into(card, pin, connection):
    cur = connection.cursor()
    cur.execute('INSERT INTO card(number, pin, balance) VALUES ("{}","{}",{});'.format(card, pin, 0))
    connection.commit()

def update_balance(card, balance, connection):
    cur = connection.cursor()
    past_balance = select_one('SELECT balance FROM card WHERE number = "{}"'.format(card), connection)
    past_balance = int(past_balance[0])
    balance += past_balance
    cur.execute('UPDATE card SET balance={} WHERE number="{}"'.format(balance, card))
    connection.commit()

def delete_acc(card, connection):
    cur = connection.cursor()
    cur.execute('DELETE FROM card WHERE number = "{}"'.format(card))
    connection.commit()


class Users:

    def luhn_algorithm(self, card):
        sum = 0
        iter = 1
        for i in card:
            if iter % 2 == 1:
                i = int(i)*2
            if int(i) > 9:
                i = int(i) - 9
            sum += int(i)
            iter += 1
        checksum = sum % 10
        card += str(10 - checksum)
        return card

    def check_luhn(self, card):
        sum = 0
        iter = 1
        for i in card:
            if iter % 2 == 1:
                i = int(i)*2
            if int(i) > 9:
                i = int(i) - 9
            sum += int(i)
            iter += 1
        if sum % 10 == 0:
            return True
        else: 
            return False
        
    def generate_card_number(self):
        alredy_exist = True
        while alredy_exist:
            tmp_card = "400000"
            for _ in range(9):
                tmp_card = tmp_card + str(random.randint(0, 9))
            tmp_card = self.luhn_algorithm(tmp_card)
            if len(tmp_card) > 16:
                alredy_exist = True
            else:
                self.account = select_all(self.connection)
                alredy_exist = False
                for acc in self.account:
                    if acc[2] == tmp_card:
                        alredy_exist = True
        return tmp_card

    def generate_pin(self):
        tmp_pin = ""
        for _ in range(4):
            tmp_pin += str(random.randint(0, 9))
        return tmp_pin

    def login(self):
        print('Enter your card number:')
        card_number = str(input())
        print('Enter your PIN:')
        pin = str(input())
        if self.check_in_db(card_number, pin):
            print('You have successfully logged in!')
            self.current_user = card_number
            return True
        else:
            print('Wrong card number or PIN!')
            return False

    def check_card(self, number):
        self.account = select_all(self.connection)
        for acc in self.account:
            if acc[1] == str(number) and len(number) == 16:
                return True
        else:
            return False

    def check_in_db(self, card, pin):
        self.account = select_all(self.connection)
        for acc in self.account:
            if acc[1] == str(card):
                if acc[2] == pin:
                    return True
                else:
                    return False
        else:
            return False

    def register(self):
        card = self.generate_card_number()
        pin = self.generate_pin()
        insert_into(card, pin, self.connection)
        print('Your card has been created')
        print('Your card number:')
        print(card)
        print('Your card PIN:')
        print(pin)

    def get_balance(self, number):
        balance = select_one('SELECT balance FROM card WHERE number = "{}"'.format(number), self.connection)
        print('Balance: ', str(balance[0]))

    def add_income(self, number):
        print('Enter income:')
        income = int(input())
        update_balance(number, income, self.connection)
        print('Income was added')

    def transaction(self, number):
        print('Transfer')
        print('Enter card number:')
        target = str(input())
        if self.check_luhn(target):
            if self.check_card(target):
                print('Enter how much money you want to transfer:')
                value = int(input())
                balance_cuser = select_one('SELECT balance FROM card WHERE number = "{}"'.format(number), self.connection)
                balance_cuser = int(balance_cuser[0])
                if value > balance_cuser:
                    print('Not enough money!')
                    return
                else:
                    balance_tuser = select_one('SELECT balance FROM card WHERE number = "{}"'.format(number), self.connection)
                    balance_tuser = int(balance_tuser[0])
                    #balance_tuser = balance_tuser + value
                    #balance_cuser = balance_cuser * -1
                    update_balance(target, value, self.connection)
                    update_balance(self.current_user, value * -1, self.connection)
                    print('Success!')

            else:
                print('Such a card does not exist.')
                return
        else:
            print('Probably you made a mistake in the card number. Please try again!')

    def account_del(self, number):
        delete_acc(number, self.connection)
        print('The account has been closed!')
        return False

    def __init__(self):
        create_db()
        self.connection = connect_db()
        self.account = select_all(self.connection)
        

if __name__ == "__main__":
    random.seed()
    option = 1
    is_logged = False
    user = Users()
    while option != '0':
        if not is_logged:
            print("1. Create an account\n2. Log into account\n0. Exit")
            option = str(input())
            if option == '1':
                user.register()
            elif option == '2':
                is_logged = user.login()
        else:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            option = str(input())
            if option == '1':
                user.get_balance(user.current_user)
            elif option == '2':
                user.add_income(user.current_user)
            elif option == '3':
                user.transaction(user.current_user)
            elif option == '4':
                is_logged = user.account_del(user.current_user)
            elif option == '5':
                print('You have successfully logged out!')
                is_logged = False
    else:
        print('Bye!')
        user.connection.close()

