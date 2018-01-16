import sqlite3
import csv
# Library used for getting data from binance api. #coin values
import json
from urllib.request import urlopen
# Library used for ALEXA
from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
conn = sqlite3.connect('Testdata.db', check_same_thread=False)  # specify database name, if not present it will create on
c = conn.cursor()

url = "https://api.binance.com/api/v1/ticker/allPrices"
# Get all  Price data in json format from binance api
request = urlopen(url)
allPrices = json.loads(request.read())  # it stores in json i.e. Dictionary format in python
btcVal = 0  # used to store current bitcoin value


def init():
    c.execute("DROP TABLE coinsXaction")
    c.execute("CREATE TABLE IF NOT EXISTS coinsXaction(Date TEXT, Market TEXT, Type TEXT, Price REAl, Amount REAL, Total REAL)")
    with open('TradeHistory.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        firstLine = True
        for line in csv_reader:
            if firstLine:  # skips the first line
                firstLine = False
                continue
            c.execute('insert into coinsXaction (Date, Market, Type, Price, Amount, Total) values (?,?,?,?,?,?);', line)

        # Buy and Sell Values are UNSIGNED, following makes them SIGNED.
        c.execute("""
            UPDATE coinsXaction
            SET Price = Price * -1,
            Amount = Amount * -1,
            Total = Total * -1
            WHERE Type = 'SELL'
            """)

        # below for loop gives the curent price of bitcoin in USD
        for dictionary in allPrices:
            if dictionary['symbol'] == 'BTCUSDT':
                global btcVal
                btcVal = dictionary['price']

        conn.commit()

def getCurrPrice(coin):
    coin = coin.upper() + "BTC"
    for dictionary in allPrices:
        if dictionary['symbol'] == coin:
            return dictionary['price']


def topCoins(number):
    data = c.execute("""
        SELECT Market,sum(Amount),sum(Total)
        FROM coinsXaction
        GROUP BY Market
        ORDER BY 3 desc
        LIMIT {};
        """.format(int(number)))

    topCoinStr = ""
    for line in data:
        # print("inside topcoins")
        coinName = line[0].split('BTC')[0]
        # print(getQuantity(coinName))
        # print("inside topcoins")
        holdingPrice = float(getCurrPrice(coinName)) * float(line[1])
        usdHoldPrice = holdingPrice * float(btcVal)
        print(coinName, holdingPrice, usdHoldPrice)
        topCoinStr = topCoinStr + "{} at ${} ,".format(coinName, int(usdHoldPrice))
    return topCoinStr


def positionQuery(coinName):
    coinName = coinName.upper() + "BTC"
    # profit / loss of a coin
    print(coinName)
    data = c.execute("""
        SELECT sum(Total),sum(Amount)
        FROM coinsXaction
        WHERE Market = "{}";
        """.format(coinName))
    for line in data:
        bought_price = float(line[0])
        print("total price bought is {}".format(bought_price))
        coinName = coinName.split('BTC')[0]
        holdingPrice = float(getCurrPrice(coinName)) * float(line[1])
        usdHoldPrice = holdingPrice * float(btcVal)
        usdBoughtPrice = bought_price * float(btcVal)
        usdProfLossPrice = usdHoldPrice - usdBoughtPrice
        print(coinName, holdingPrice, usdHoldPrice, usdBoughtPrice, usdProfLossPrice)
    # available quantity of a coin

        if usdProfLossPrice > 0:
            return (" You are in profit of {:.1f} dollars ".format(usdProfLossPrice))    
        else:
            return ("Sorry, you are in loss of {:.1f}".format(usdProfLossPrice))


def quantity(coinName):  # it gives the available quantity of a coin
    coinName = coinName + "BTC"
    data = c.execute("""
        SELECT sum(Amount)
        FROM coinsXaction
        WHERE Market = "{}"
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
    message = positionQuery(coinName)
    return question(message)


@ask.intent('AskTopCoin')
def topCoinsIntent(number):
    message = topCoins(number)
    return question(message)


@ask.intent('availQuantity')
def getquantity(coinName):
    message = quantity(coinName.upper())
    return question(message)


if __name__ == '__main__':
    app.run(port=6000, debug=True)  # port should be same on ngrok


c.close()  # closing cursors
conn.close()  # closing db connection
