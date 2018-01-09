import sqlite3
import csv

from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
conn = sqlite3.connect('Testdata.db', check_same_thread=False)  # specify database name, if not present it will create on
c = conn.cursor()


def init():  # Create a table, Reads the csv and insert all data to the table.
    c.execute("DROP TABLE coinsXaction")
    c.execute("CREATE TABLE coinsXaction(UserName TEXT, Date TEXT, Coins TEXT, BuySell TEXT, Qty REAL, Value REAL, Total REAL)")
    with open('coinsXaction.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)  # reads the csv
        firstLine = True
        for line in csv_reader:
            if firstLine:  # skips the first line as it contains header
                firstLine = False
                continue
            c.execute('insert into coinsXaction (UserName, Date, Coins, BuySell, Qty, Value, Total) values (?,?,?,?,?,?,?);', line)
        conn.commit()


def positionQuery(coinName):  # it accepts the coin name, and give the position of a coin
    data = c.execute("""
        SELECT sum(Total)
        FROM coinsXaction
        WHERE Coins = "{}"
        """.format(coinName))
    for line in data:
        total = int(line[0])
        if total > 0:
            return ("Sorry, you are in loss of {} for {} coin".format(total, coinName))
        else:
            return (" You are in profit of {} for {} coin".format(total, coinName))


def quantity(coinName):  # it gives the available quantity of a coin
    data = c.execute("""
        SELECT sum(QTY)
        FROM coinsXaction
        WHERE Coins = "{}"
        """.format(coinName))
    for line in data:
        qty = int(line[0])
        if qty == 0:
            return ("you sold all your {} coin".format(coinName))
        else:
            return (" You've got {} {} coin".format(qty, coinName))
        break


@ask.launch
def start_skill():  # when alexa opens the app
    init()
    welcome = 'Hi mukesh, how can i help?'
    return question(welcome)


@ask.intent('AskCoinPrice')
def getcoin(coinName):
    message = positionQuery(coinName.upper())
    return question(message)


@ask.intent('availQuantity')
def getquantity(coinName):
    message = quantity(coinName.upper())
    return question(message)


if __name__ == '__main__':
    app.run(port=6000, debug=True)  # port should be same on ngrok


c.close()  # closing cursors
conn.close()  # closing db connection
