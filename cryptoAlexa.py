# Library used for ALEXA
from flask import Flask
from flask_ask import Ask, statement, question, session
import processUnit as pu

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():  # when alexa opens the app
    pu.init()
    welcome = 'Hi, how can i help?'
    return question(welcome)


@ask.intent('AskCoinPrice')
def getcoin(coinName):
    message = pu.positionQuery(coinName)
    return question(message)


@ask.intent('AskTopCoin')
def topCoinsIntent(number):
    message = pu.topCoins(number)
    return question(message)


@ask.intent('availQuantity')
def getquantity(coinName):
    message = pu.quantity(coinName.upper())
    return question(message)


if __name__ == '__main__':
    app.run(port=6000, debug=True)  # port should be same on ngrok

# pu.c.close()  # closing cursors
# pu.conn.close()  # closing db connection
