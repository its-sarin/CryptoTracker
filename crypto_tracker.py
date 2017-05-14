import sys
import optparse
import GDAX
from getkey import getkey, keys
from blessings import Terminal

key = None

usage = "usage: %prog [options] arg1 arg2 arg3"
parser = optparse.OptionParser(usage=usage)

parser.add_option('-b', '--btc', action="store_true", dest="btc",
    help="Limit crypto tracker to BTC-USD", default=False)

parser.add_option('-e', '--eth', action="store_true", dest="eth",
    help="Limit crypto tracker to ETH-USD", default=False)

parser.add_option('-l', '--ltc', action="store_true", dest="ltc",
    help="Limit crypto tracker to LTC-USD", default=False)

# Parse arguments
(options, args) = parser.parse_args()

# Handle coin options
btc = options.btc
eth = options.eth
ltc = options.ltc
all_coins = (not btc and not eth and not ltc)

coins = ["BTC-USD", "ETH-USD", "LTC-USD"]
prods = []

if (all_coins):
    prods = coins
else:
    if (btc):
        prods.append(coins[0])
    if (eth):
        prods.append(coins[1])
    if (ltc):
        prods.append(coins[2])

# Enter fullscreen mode
term = Terminal()
print term.enter_fullscreen
print term.move_y(0)

# GDAX Websocket Client
class GDAXWebsocketClient(GDAX.WebsocketClient):
    def __init__(self, prods):
        # Initialize class variables
        self._prods = prods
        self._btc = "BTC-USD" in self._prods
        self._eth = "ETH-USD" in self._prods
        self._ltc = "LTC-USD" in self._prods

        self.recvd_data = False
        self.btc_price = 0
        self.eth_price = 0
        self.ltc_price = 0
        self.new_btc_price = 0
        self.new_eth_price = 0
        self.new_ltc_price = 0

        self.btc_change = False
        self.eth_change = False
        self.ltc_change = False
        self.btc_up = False
        self.eth_up = False
        self.ltc_up = False

    def onOpen(self):
        # Subscription values
        self.url = "wss://ws-feed.gdax.com/"
        self.products = self._prods

    def onMessage(self, msg):
        # Reset flags
        self.btc_change = False
        self.eth_change = False
        self.ltc_change = False
        self.btc_up = False
        self.eth_up = False
        self.ltc_up = False

        # If we're showing BTC-USD
        if (self._btc):
            # Bitcoin - Catch messages of Type "done" with Reason "filled" and get the Price data
            if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "BTC-USD"):
                if (msg.has_key("price")):
                    self.recvd_data = True
                    self.new_btc_price = msg["price"]

            # Bitcoin - If the new price is different from old price, update
            if (self.btc_price != self.new_btc_price):
                self.btc_change = True
                if (self.btc_price < self.new_btc_price):
                    self.btc_up = True
                self.btc_price = self.new_btc_price

        # If we're showing ETH-USD
        if (self._eth):
            # Ether - Catch messages of Type "done" with Reason "filled" and get the Price data
            if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "ETH-USD"):
                if (msg.has_key("price")):
                    self.recvd_data = True
                    self.new_eth_price = msg["price"]

            # Ether - If the new price is different from old price, update
            if (self.eth_price != self.new_eth_price):
                self.eth_change = True
                if (self.eth_price < self.new_eth_price):
                    self.eth_up = True
                self.eth_price = self.new_eth_price

        # If we're showing LTC-USD
        if (self._ltc):
            # Litecoin - Catch messages of Type "done" with Reason "filled" and get the Price data
            if (msg["type"] == "done" and msg["reason"] == "filled" and msg["product_id"] == "LTC-USD"):
                if (msg.has_key("price")):
                    self.recvd_data = True
                    self.new_ltc_price = msg["price"]

            # Litecoin - If the new price is different from old price, update
            if (self.ltc_price != self.new_ltc_price):
                self.ltc_change = True
                if (self.ltc_price < self.new_ltc_price):
                    self.ltc_up = True
                self.ltc_price = self.new_ltc_price

        # If we have no date yet or there has been a change in some value,
        # write out the updated values
        if (self.recvd_data == False or self.btc_change or self.eth_change or self.ltc_change):
            sys.stdout.write("\033[K")

            if (self._btc):
                if (self.btc_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("BTC-USD: $%.3f" % float(self.btc_price))

            if (self._btc and self._eth):
                sys.stdout.write("\033[1;36m")
                sys.stdout.write(" | ")

            if (self._eth):
                if (self.eth_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("ETH-USD: $%.3f" % float(self.eth_price))

            if (self._ltc and (self._eth or self._btc)):
                sys.stdout.write("\033[1;36m")
                sys.stdout.write(" | ")

            if (self._ltc):
                if (self.ltc_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("LTC-USD: $%.3f" % float(self.ltc_price))

            sys.stdout.write("\r")
            sys.stdout.flush()

    def onClose(self):
        print("\n\033[0;32m-- Goodbye! --")

# Start the websocket client
ws_client = GDAXWebsocketClient(prods)
ws_client.start()

# Listen for Escape key to quit and close websocket if so
while (key != keys.ESCAPE):
    key = getkey()
    if (key == keys.ESCAPE):
        ws_client.close()
