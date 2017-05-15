import sys
import datetime
import optparse
import GDAX
from getkey import getkey, keys
from blessings import Terminal

# Command line options
usage = "usage: %prog [options] arg1 arg2 arg3"
parser = optparse.OptionParser(usage=usage)

parser.add_option('-b', '--btc', action="store_true", dest="btc",
    help="Limit crypto tracker to BTC-USD", default=False)

parser.add_option('-e', '--eth', action="store_true", dest="eth",
    help="Limit crypto tracker to ETH-USD", default=False)

parser.add_option('-l', '--ltc', action="store_true", dest="ltc",
    help="Limit crypto tracker to LTC-USD", default=False)

parser.add_option('--nodiff', action="store_true", dest="nodiff",
    help="Suppress display of price difference since day's opening price",
    default=False)

# Parse arguments
(options, args) = parser.parse_args()

# Websocket url
url = "wss://ws-feed.gdax.com/"

# Set initial list of possible coins
coins = ["BTC-USD", "ETH-USD", "LTC-USD"]
prods = []

# Key variable for listening for quit key
key = None

# Handle coin options
btc = options.btc
eth = options.eth
ltc = options.ltc
nodiff = options.nodiff
all_coins = (not btc and not eth and not ltc)

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
class GDAXMessageFeed(GDAX.WebsocketClient):
    def __init__(self, url, products, nodiff):
        # Initialize class variables
        self.products = products
        self.url = url
        self._btc = "BTC-USD" in self.products
        self._eth = "ETH-USD" in self.products
        self._ltc = "LTC-USD" in self.products
        self._nodiff = nodiff

        self.btc_price = 0
        self.eth_price = 0
        self.ltc_price = 0
        self.new_btc_price = 0
        self.new_eth_price = 0
        self.new_ltc_price = 0

        self.btc_open = 0
        self.eth_open = 0
        self.ltc_open = 0

        self.btc_change = False
        self.eth_change = False
        self.ltc_change = False
        self.btc_up = False
        self.eth_up = False
        self.ltc_up = False

        self.btc_amt_change = 0
        self.eth_amt_change = 0
        self.ltc_amt_change = 0

        self.today = None

    def onOpen(self):
        self._set_open()
        self._print_message()

    def onMessage(self, msg):
        if (datetime.datetime.today().day != self.today):
            self._set_open()

        # If we're showing BTC-USD
        if (self._btc):
            # Bitcoin - Catch messages of Type "done" with Reason "filled"
            # and get the Price data
            if (msg["type"] == "done" and
                msg["reason"] == "filled" and
                msg["product_id"] == "BTC-USD"):
                if (msg.has_key("price")):
                    self.new_btc_price = float(msg["price"])

            # Bitcoin - If the new price is different from old price, update
            if (self.btc_price != self.new_btc_price):
                self.btc_change = True
                self.btc_amt_change = self.new_btc_price - self.btc_open

                if (self.new_btc_price > self.btc_open):
                    self.btc_up = True
                else:
                    self.btc_up = False

                self.btc_price = self.new_btc_price
            else:
                self.btc_change = False

        # If we're showing ETH-USD
        if (self._eth):
            # Ether - Catch messages of Type "done" with Reason "filled"
            # and get the Price data
            if (msg["type"] == "done" and
                msg["reason"] == "filled" and
                msg["product_id"] == "ETH-USD"):
                if (msg.has_key("price")):
                    self.new_eth_price = float(msg["price"])

            # Ether - If the new price is different from old price, update
            if (self.eth_price != self.new_eth_price):
                self.eth_change = True
                self.eth_amt_change = self.new_eth_price - self.eth_open

                if (self.new_eth_price > self.eth_open):
                    self.eth_up = True
                else:
                    self.eth_up = False

                self.eth_price = self.new_eth_price
            else:
                self.eth_change = False

        # If we're showing LTC-USD
        if (self._ltc):
            # Litecoin - Catch messages of Type "done" with Reason "filled"
            # and get the Price data
            if (msg["type"] == "done" and
                msg["reason"] == "filled" and
                msg["product_id"] == "LTC-USD"):
                if (msg.has_key("price")):
                    self.new_ltc_price = float(msg["price"])

            # Litecoin - If the new price is different from old price, update
            if (self.ltc_price != self.new_ltc_price):
                self.ltc_change = True
                self.ltc_amt_change = self.new_ltc_price - self.ltc_open

                if (self.new_ltc_price > self.ltc_open):
                    self.ltc_up = True
                else:
                    self.ltc_up = False

                self.ltc_price = self.new_ltc_price
            else:
                self.ltc_change = False

        # If we have no date yet or there has been a change in some value,
        # write out the updated values
        if (self.btc_change or self.eth_change or self.ltc_change):
            self._print_message()

    def onClose(self):
        # Say goodbye
        print("\n\033[0;32m-- Goodbye! --\033[0;0m")

    def _set_open(self):
        # Set today's date
        self.today = datetime.datetime.today().day
        # Get the day's opening price for each currency
        self.btc_open = float(GDAX.PublicClient(product_id="BTC-USD").getProduct24HrStats()["open"])
        self.eth_open = float(GDAX.PublicClient(product_id="ETH-USD").getProduct24HrStats()["open"])
        self.ltc_open = float(GDAX.PublicClient(product_id="LTC-USD").getProduct24HrStats()["open"])

    def _print_message(self):
        print(term.clear)
        with term.location(0, 0):
            sys.stdout.write("\033[K")

            if (self._btc):
                if (self.btc_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("BTC-USD: $%.2f" % self.btc_price)
                if not nodiff:
                    sys.stdout.write(" (%.2f)" % self.btc_amt_change)

            if (self._btc and self._eth):
                sys.stdout.write("\033[1;36m")
                sys.stdout.write(" | ")

            if (self._eth):
                if (self.eth_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("ETH-USD: $%.2f" % self.eth_price)
                if not nodiff:
                    sys.stdout.write(" (%.2f)" % self.eth_amt_change)

            if (self._ltc and (self._eth or self._btc)):
                sys.stdout.write("\033[1;36m")
                sys.stdout.write(" | ")

            if (self._ltc):
                if (self.ltc_up):
                    sys.stdout.write("\033[0;32m")
                else:
                    sys.stdout.write("\033[1;31m")

                sys.stdout.write("LTC-USD: $%.2f" % self.ltc_price)
                if not nodiff:
                    sys.stdout.write(" (%.2f)" % self.ltc_amt_change)

            sys.stdout.write("\r")
            sys.stdout.flush()


# Start the websocket client
ws_client = GDAXMessageFeed(url, prods, nodiff)
ws_client.start()

# Listen for Escape key to quit and close websocket if so
while (key != keys.ESCAPE):
    key = getkey()
    if (key == keys.ESCAPE):
        ws_client.close()
