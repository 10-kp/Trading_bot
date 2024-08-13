# Imports the JSON library to handle JSON data
import json

# Imports essential functions and classes from the Flask library for creating web applications.
from flask import Flask, render_template, request, jsonify 

# Imports the HTTP class from the pybit library to interact with the Bybit exchange API.
from pybit import HTTP

# Imports the time library (not used in this code but typically used for time-related operations).
import time

#  Imports the ccxt library for connecting to various cryptocurrency exchanges, including Binance
import ccxt

#  Imports a custom class Bot from a module named binanceFutures (used for Binance Futures trading)
from binanceFutures import Bot


def validate_bybit_api_key(session):#function to check if the Bybit API key is valid
    try: #Starts a try block to attempt operations that might fail.
        result = session.get_api_key_info() #Calls the Bybit API to get API key information. If successful, it indicates the key is valid.
        return True #he function returns True, meaning the key is valid if no errors.
    except Exception as e: #Catches any errors that occur during the API call.
        print("Bybit API key validation failed:", str(e))
        return False

def validate_binance_api_key(exchange):#function to check if the Bybit API key is valid
    try:
        result = exchange.fetch_balance() #Fetches account balance from Binance
        return True
    except Exception as e: # Catches errors during the API call.
        print("Binance API key validation failed", str(e))
        return False

#Create a new Flask web application. __name__ helps Flask locate resources and templates.
app = Flask(__name__)

# load config.json
with open('config.json') as config_file: # Opens the config.json file, which contains configuration settings
    config = json.load(config_file) #Reads the JSON data from the file and loads it into a Python dictionary called config


###############################################################################
# Exchange Validation 

use_bybit = False
if 'BYBIT' in config ['EXCHANGES']:# Checks if settings are present in the configuration
    if config['EXCHANGES']['BYBIT']['ENABLED']:#Checks if Bybit is enabled
        print('Bybit is enabled')
        use_bybit = True

#Creates a new Bybit API session using the provided endpoint and API credentials.
    session = HTTP( 
        endpoint='https://api.bybit.com',
        api_key=config['EXCHANGES']['BYBIT']['API_KEY'],
        api_secret=config['EXCHANGES']['BYBIT']['API_SECRET']
    )#

use_binance_futures = False #Initializes a flag for Binance Futures
if 'BINANCE-FUTURES' in config['EXCHANGES']: #Checks if Binance Futures settings are in the configuration.
    if config['EXCHANGES']['BINANCE-FUTURES']['ENABLED']:
        print("Binance is enabled!")
        use_binance_futures = True

# Creates a new Binance Futures API session using the provided credentials and settings
        exchange = ccxt.binance({
        'apiKey': config['EXCHANGES']['BINANCE-FUTURES']['API_KEY'],
        'secret': config['EXCHANGES']['BINANCE-FUTURES']['API_SECRET'],
        'options': {
            'defaultType': 'future',
            },
        'urls': {
            'api': {
                'public': 'https://testnet.binancefuture.com/fapi/v1',
                'private': 'https://testnet.binancefuture.com/fapi/v1',
            }, }
        })
        exchange.set_sandbox_mode(True)

# Validate Bybit API key
if use_bybit:
    if not validate_bybit_api_key(session):
        print("Invalid Bybit API key.")
        use_bybit = False

# Validate Binance Futures API key
if use_binance_futures:
    if not validate_binance_api_key(exchange):
        print("Invalid Binance Futures API key.")
        use_binance_futures = False

@app.route('/') #Defines the root URL (/) for the web application
#function that handles requests to the root URL
def index():
    #JSON response indicating the server is running.
    return {'message': 'Server is running!'}

#Defines the /webhook URL for handling POST requests.
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Hook Received!")
    data = json.loads(request.data) #Parses the JSON data from the request body
    print(data)

#Checks if the provided key matches the expected key in the configuration
    if int(data['key']) != config['KEY']:
        print("Invalid Key, Please Try Again!")
        return {
            "status": "error",
            "message": "Invalid Key, Please Try Again!"
        }

    ##############################################################################
    #             Bybit

#Checks if the data specifies Bybit as the exchange.
    if data['exchange'] == 'bybit':
        if use_bybit:
            if data['close_position'] == 'True': #close current position in the market
                print("Closing Position")
                session.close_position(symbol=data['symbol']) #Closes the position on Bybit for the specified symbol.
            else: #checks if there's a request to cancel orders
                if 'cancel_orders' in data:
                    print("Cancelling Order")
                    session.cancel_all_active_orders(symbol=data['symbol'])
                if 'type' in data:#if there's a type specified in the data
                    print("Placing Order")#an order should be placed
                    if 'price' in data:
                        price = data['price']
                    else:
                        price = 0

##Handling Different Order Modes
# set both a take profit and a stop loss.
                    if data['order_mode'] == 'Both':
                        take_profit_percent = float(data['take_profit_percent'])/100
                        stop_loss_percent = float(data['stop_loss_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                            stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                        elif data['side'] == 'Sell':
                            take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)
                            stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                        print("Take Profit Price: " + str(take_profit_price))
                        print("Stop Loss Price: " + str(stop_loss_price))

                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, take_profit=take_profit_price, stop_loss=stop_loss_price)

# Take Profit Only
                    elif data['order_mode'] == 'Profit':
                        take_profit_percent = float(data['take_profit_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                        elif data['side'] == 'Sell':
                            take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)

                        print("Take Profit Price: " + str(take_profit_price))
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, take_profit=take_profit_price)

# Take PStop Loss Only
                    elif data['order_mode'] == 'Stop':
                        stop_loss_percent = float(data['stop_loss_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                        elif data['side'] == 'Sell':
                            stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                        print("Stop Loss Price: " + str(stop_loss_price))
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, stop_loss=stop_loss_price)

#No Specific Order Mode
                    else:
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price)

#Return Success Message for Bybit
        return {
            "status": "success",
            "message": "Bybit Webhook Received!"
        }
    

    ##############################################################################
    #             Binance Futures#

    
        if data['exchange'] == 'binance-futures':
            if use_binance_futures:
                bot  = Bot() #creates an instance of a Bot
                bot.run(data)
                return {
                    "status": "success",
                    "message": "Binance Futures Webhook Received!"
                }

        else:
            print("Invalid Exchange, Please Try Again!")
            return {
                "status": "error",
                "message": "Invalid Exchange, Please Try Again!"
            }

if __name__ == '__main__':
    app.run(debug=False)


