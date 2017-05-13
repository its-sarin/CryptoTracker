import sys
import GDAX
from getkey import getkey, keys

key = None

class GDAXWebsocketClient(GDAX.WebsocketClient):
    def __init__(self):
        # Initialize class variables
        self.recvd_data = False
        self.btc_price = 0
        self.eth_price = 0
        self.ltc_price = 0
        self.new_btc_price = 0
        self.new_eth_price = 0
        self.new_ltc_price = 0

    def onOpen(self):
        # Subscription values
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["BTC-USD", "ETH-USD", "LTC-USD"]

    def onMessage(self, msg):
        btc_change = False
        eth_change = False
        ltc_change = False
        btc_up = False
        eth_up = False
        ltc_up = False

        # Bitcoin - Catch messages of Type "done" with Reason "filled" and get the Price data
        if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "BTC-USD"):
            if (msg.has_key("price")):
                self.recvd_data = True
                self.new_btc_price = msg["price"]

        # Ether - Catch messages of Type "done" with Reason "filled" and get the Price data
        if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "ETH-USD"):
            if (msg.has_key("price")):
                self.recvd_data = True
                self.new_eth_price = msg["price"]

        # Litecoin - Catch messages of Type "done" with Reason "filled" and get the Price data
        if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "LTC-USD"):
            if (msg.has_key("price")):
                self.recvd_data = True
                self.new_ltc_price = msg["price"]

        # Bitcoin - If the new price is different from old price, update
        if (self.btc_price != self.new_btc_price):
            btc_change = True
            if (self.btc_price < self.new_btc_price):
                btc_up = True
            self.btc_price = self.new_btc_price

        # Ether - If the new price is different from old price, update
        if (self.eth_price != self.new_eth_price):
            eth_change = True
            if (self.eth_price < self.new_eth_price):
                eth_up = True
            self.eth_price = self.new_eth_price

        # Litecoin - If the new price is different from old price, update
        if (self.ltc_price != self.new_ltc_price):
            ltc_change = True
            if (self.ltc_price < self.new_ltc_price):
                ltc_up = True
            self.ltc_price = self.new_ltc_price

        # If we have no date yet or there has been a change in some value,
        # write out the updated values
        if (self.recvd_data == False or btc_change or eth_change or ltc_change):
            sys.stdout.write("\r")

            if (btc_up):
                sys.stdout.write("\033[0;32m")
            else:
                sys.stdout.write("\033[1;31m")

            sys.stdout.write("BTC: %.3f" % float(self.btc_price))
            sys.stdout.write("\033[1;36m")
            sys.stdout.write(" | ")

            if (eth_up):
                sys.stdout.write("\033[0;32m")
            else:
                sys.stdout.write("\033[1;31m")

            sys.stdout.write("ETH: %.3f" % float(self.eth_price))
            sys.stdout.write("\033[1;36m")
            sys.stdout.write(" | ")

            if (ltc_up):
                sys.stdout.write("\033[0;32m")
            else:
                sys.stdout.write("\033[1;31m")

            sys.stdout.write("LTC: %.3f" % float(self.ltc_price))
            sys.stdout.flush()

    def onClose(self):
        print("\n\033[0;32m-- Goodbye! --")

# Start the websocket client
ws_client = GDAXWebsocketClient()
ws_client.start()

# Listen for Escape key to quit and close websocket if so
while (key != keys.ESCAPE):
    key = getkey()
    if (key == keys.ESCAPE):
        ws_client.close()
