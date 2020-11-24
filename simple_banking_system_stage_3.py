import random
import sqlite3



random.seed()
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
                self.account = self.cur.execute("SELECT * FROM card;")
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

    def check_in_db(self, card, pin):
        self.account = self.cur.execute('SELECT * FROM card;')
        for acc in self.account:
            if acc[1] == str(card):
                if acc[2] == pin:
                    self.lastuser = acc[0]
                    return True
                else:
                    return False
        else:
            return False

    def register(self):
        card = self.generate_card_number()
        pin = self.generate_pin()
        self.cur.execute('INSERT INTO card(number, pin, balance) VALUES ("{}","{}",{});'.format(card, pin, 0))
        self.con.commit()
        self.lastuser += 1
        print('Your card has been created')
        print('Your card number:')
        print(card)
        print('Your card PIN:')
        print(pin)

    def get_balance(self, number):
        self.cur.execute('SELECT balance FROM card WHERE number = "{}"'.format(number))
        balance = self.cur.fetchone()
        print(str(balance[0]))

    def __init__(self):
        self.con = sqlite3.connect('card.s3db')
        self.cur = self.con.cursor()
        self.cur.executescript('''
CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY AUTOINCREMENT,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
);
''')
        self.cur.execute('SELECT * FROM card')
        self.account = self.cur.fetchall()
        self.lastuser = self.cur.lastrowid




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
        print('1. Balance\n2. Log out\n0. Exit')
        option = str(input())
        if option == '1':
            user.get_balance(user.current_user)
        elif option == '2':
            print('You have successfully logged out!')
            is_logged = False
else:
    print('Bye!')
    user.cur.close()

