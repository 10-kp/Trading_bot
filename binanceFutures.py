import json  # Importing the JSON library to work with JSON data.
import time  # Importing the time library, though it's not used in this code.
import ccxt  # Importing the CCXT library to interact with cryptocurrency exchanges.
import random  # Importing the random library for generating random strings.
import string  # Importing the string library to access letters and digits.

# Loading configuration settings from a JSON file named 'config.json'
with open('config.json') as config_file:
    config = json.load(config_file)

# Checking if the testnet (sandbox) mode is enabled for Binance Futures.
if config['EXCHANGES']['binance-futures']['TESTNET']:
    
    # Creating an exchange object for Binance Futures in testnet mode
    exchange = ccxt.binance({
        'apiKey': config['EXCHANGES']['binance-futures']['API_KEY'], # API key for Binance.
        'secret': config['EXCHANGES']['binance-futures']['API_SECRET'],# Secret key for Binance.
        'options': {
            'defaultType': 'future', # Setting the default market type to futures.
        },
        'urls': {
            'api': {
                'public': 'https://testnet.binancefuture.com/fapi/v1',
                'private': 'https://testnet.binancefuture.com/fapi/v1',
            }, }
    })
    
    # Enabling sandbox mode to simulate trades without real money.
    exchange.set_sandbox_mode(True) 
else:
    # Creating an exchange object for Binance Futures in live mode.
    exchange = ccxt.binance({
        'apiKey': config['EXCHANGES']['binance-futures']['API_KEY'],# API key for Binance.
        'secret': config['EXCHANGES']['binance-futures']['API_SECRET'],# Secret key for Binance.
        'options': {
            'defaultType': 'future',# Setting the default market type to futures.
        },
        'urls': {
            'api': {
                'public': 'https://fapi.binance.com/fapi/v1',
                'private': 'https://fapi.binance.com/fapi/v1',
            }, }
    })

# Defining a class named 'Bot' that contains methods to automate trading tasks.
class Bot:

    def __int__(self): # Constructor method for the Bot class (nothing here).
        pass

    def create_string(self):
        N = 7# Length of the random string to be generated

         # Generating a random string of 7 uppercase letters and digits
        res = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k=N))
        baseId = 'x-40PTWbMI' # A base string to prepend to the random string
        self.clientId = baseId + str(res)# Creating a unique client order ID.
        return

# Method to close an existing position on Binance Futures.
    def close_position(self, symbol):

        # Fetching the current position for the given symbol.
        position = exchange.fetch_positions(symbol)[0]['info']['positionAmt']
        self.create_string()
        params = {
            "newClientOrderId": self.clientId, # Adding the unique ID to the order parameters.
            'reduceOnly': True  # Setting 'reduceOnly' to true to ensure the position is reduced (not increased).
        }
         # Checking if the position is a long position (greater than 0).
        if float(position) > 0:
            print("Closing Long Position")

            # Creating a market order to sell and close the long position.
            exchange.create_order(symbol, 'Market', 'Sell', float(position), price=None, params=params)
        else:
            print("Closing Short Position")

            # Creating a market order to buy and close the short position.
            exchange.create_order(symbol, 'Market', 'Buy', -float(position), price=None, params=params)

# Method to set risk parameters (stop loss and take profit) for an existing position.
    def set_risk(self, symbol, data, stop_loss, take_profit):

        # Fetching the current position details.
        position = exchange.fetch_positions(symbol)
        print(position)

        # Getting the entry price of the position.
        price = float(position[0]['info']['entryPrice'])

        # Getting the size (quantity) of the position.
        size = abs(float(position[0]['info']['positionAmt']))

        # Fetching the latest market price for the symbol
        markPrice = float(exchange.fetch_ticker(data['symbol'])['last'])

# Setting both stop loss and take profit orders.
        if data['order_mode'] == 'Both':
            if data['side'] == 'Buy':# If the trade is a 'Buy' order.
                self.create_string()# Creating a unique client order ID.

                # Creating a stop market order to sell and stop the loss.
                exchange.create_order(symbol, 'STOP_MARKET', 'Sell', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': stop_loss, # Setting the stop loss price.
                })
                self.create_string()# Creating a new unique client order ID.

                # Creating a take profit order to sell and take profit.
                exchange.create_order(symbol, 'TAKE_PROFIT', 'Sell', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': take_profit,# Setting the take profit price.
                })
            else: # If the trade is a 'Sell' order.
                self.create_string()# Creating a unique client order ID.

                # Creating a stop market order to buy and stop the loss.
                exchange.create_order(symbol, 'STOP_MARKET', 'Buy', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': stop_loss,# Setting the stop loss price
                })
                self.create_string()# Creating a new unique client order ID.

                # Creating a take profit order to buy and take profit.
                exchange.create_order(symbol, 'TAKE_PROFIT', 'Buy', size, take_profit, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': take_profit,# Setting the take profit price.
                })

# Setting only a take profit order.
        elif data['order_mode'] == 'Profit':
            if data['side'] == 'Buy':# If the trade is a 'Buy' order.
                self.create_string()# Creating a unique client order ID

                # Creating a take profit order to sell and take profit.
                exchange.create_order(symbol, 'TAKE_PROFIT', 'Sell', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': take_profit,# Setting the take profit price.
                })
            else:# If the trade is a 'Sell' order.
                self.create_string()# Creating a unique client order ID.

                # Creating a take profit order to buy and take profit.
                exchange.create_order(symbol, 'TAKE_PROFIT', 'Buy', size, take_profit, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': take_profit,# Setting the take profit price.
                })

        # Setting only a stop loss order.
        elif data['order_mode'] == 'Stop':
            if data['side'] == 'Buy':# If the trade is a 'Buy' order.
                self.create_string()# Creating a unique client order ID.

                # Creating a stop market order to sell and stop the loss.
                exchange.create_order(symbol, 'STOP_MARKET', 'Sell', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': stop_loss,# Setting the stop loss price.
                })
            else:# If the trade is a 'Sell' order.
                self.create_string()# If the trade is a 'Sell' order.

                # Creating a stop market order to buy and stop the loss.
                exchange.create_order(symbol, 'STOP_MARKET', 'Buy', size, params={
                    "newClientOrderId": self.clientId,
                    'reduceOnly': True,
                    'stopPrice': stop_loss,# Setting the stop loss price.
                })



# Method to run the bot based on the data provided.
    def run(self, data):
        print(data['close_position'])# Printing the close position status for debugging.
        if data['close_position'] == 'True':
            print("Closing Position")# Informing that the position is being closed.
            self.close_position(symbol=data['symbol']) # Closing the position.
        else:
            if 'cancel_orders' in data:
                print("Cancelling Order") # Informing that orders are being canceled
                exchange.cancel_all_orders(symbol=data['symbol']) # Canceling all existing orders.
            if 'type' in data:
                print("Placing Order") # Informing that a new order is being placed.
                if 'price' in data:
                    price = data['price']# Setting the price if provided in the data
                else:
                    price = 0 # Default price to 0 if not provided.

                if data['order_mode'] == 'Both':
                    take_profit_percent = float(data['take_profit_percent']) / 100
                    stop_loss_percent = float(data['stop_loss_percent']) / 100
                    current_price = exchange.fetch_ticker(data['symbol'])['last']
                    if data['side'] == 'Buy':
                        take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent),
                                                  2)
                        stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                    elif data['side'] == 'Sell':
                        take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent),
                                                  2)
                        stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                    print("Take Profit Price: " + str(take_profit_price))
                    print("Stop Loss Price: " + str(stop_loss_price))

                    self.create_string()
                    params = {
                        "newClientOrderId": self.clientId,
                        'reduceOnly': False
                    }
                    if data['type'] == 'Limit':
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              price=float(price), params=params)
                    else:
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              params=params)

                    self.set_risk(data['symbol'], data, stop_loss_price, take_profit_price)


                elif data['order_mode'] == 'Profit':
                    take_profit_percent = float(data['take_profit_percent']) / 100
                    current_price = exchange.fetch_ticker(data['symbol'])['last']

                    if data['side'] == 'Buy':
                        take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent),
                                                  2)
                    elif data['side'] == 'Sell':
                        take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent),
                                                  2)

                    print("Take Profit Price: " + str(take_profit_price))

                    self.create_string()
                    params = {
                        "newClientOrderId": self.clientId,
                        'reduceOnly': False
                    }

                    if data['type'] == 'Limit':
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              price=float(price), params=params)
                    else:
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              params=params)

                    self.set_risk(data['symbol'], data, 0, take_profit_price)


                elif data['order_mode'] == 'Stop':
                    stop_loss_percent = float(data['stop_loss_percent']) / 100
                    current_price = exchange.fetch_ticker(data['symbol'])['last']

                    if data['side'] == 'Buy':
                        stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                    elif data['side'] == 'Sell':
                        stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                    print("Stop Loss Price: " + str(stop_loss_price))

                    self.create_string()
                    params = {
                        "newClientOrderId": self.clientId,
                        'reduceOnly': False
                    }

                    if data['type'] == 'Limit':
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              price=float(price), params=params)
                    else:
                        exchange.create_order(data['symbol'], data['type'], data['side'], float(data['qty']),
                                              params=params)

                    self.set_risk(data['symbol'], data, stop_loss_price, 0)

                else:
                    return {
                        'status': 'error'
                    }
