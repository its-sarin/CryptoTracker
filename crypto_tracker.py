import sys
from os import name as os_name
from datetime import datetime
from time import time, localtime, strftime
import optparse
import GDAX
from getkey import getkey, keys
from blessings import Terminal

# Hide the cursor (for now only works on Mac and Linux)
if os_name == "posix":
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

# Command line options
usage = "usage: %prog [options] arg1 arg2 arg3"
parser = optparse.OptionParser(usage=usage)

parser.add_option('-b', '--btc', action="store_true", dest="btc",
    help="Limit crypto tracker to BTC-USD", default=False)

parser.add_option('-e', '--eth', action="store_true", dest="eth",
    help="Limit crypto tracker to ETH-USD", default=False)

parser.add_option('-l', '--ltc', action="store_true", dest="ltc",
    help="Limit crypto tracker to LTC-USD", default=False)

parser.add_option('-p', '--pdiff', action="store_true", dest="diff",
    help="Display percent difference since day's opening price",
    default=False)

parser.add_option('-t', '--time', action="store_true", dest="show_time",
    help="Display time of last update at bottom of terminal",
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
diff = options.diff
show_time = options.show_time
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

# Store new Blessings terminal object
term = Terminal()

# Enter fullscreen mode
print term.enter_fullscreen

# GDAX Websocket Client
class GDAXMessageFeed(GDAX.WebsocketClient):
    # ANSI color codes
    CYAN = "\033[1;36m"
    RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    NORMAL = "\033[0;0m"
    CLEARTOEND = "\033[K"

    def __init__(self, url, products, diff, show_time):
        # Initialize class variables
        self.products = products
        self.url = url
        self._btc = "BTC-USD" in self.products
        self._eth = "ETH-USD" in self.products
        self._ltc = "LTC-USD" in self.products
        self._diff = diff
        self._show_time = show_time

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
        self.last_msg_time = None

    def onOpen(self):
        self._set_open()
        self._print_message()

    def onMessage(self, msg):
        self.last_msg_time = time()

        if (datetime.today().day != self.today):
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
                self.btc_amt_change = self.new_btc_price / self.btc_open

                if (self.new_btc_price >= self.btc_open):
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
                self.eth_amt_change = self.new_eth_price / self.eth_open

                if (self.new_eth_price >= self.eth_open):
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
                self.ltc_amt_change = self.new_ltc_price / self.ltc_open

                if (self.new_ltc_price >= self.ltc_open):
                    self.ltc_up = True
                else:
                    self.ltc_up = False

                self.ltc_price = self.new_ltc_price
            else:
                self.ltc_change = False

        # If there has been a change in some value, print out the updated values
        if (self.btc_change or self.eth_change or self.ltc_change):
            self._print_message()

    def onClose(self):
        # Clear the screen
        print(term.clear)
        # Say goodbye
        with term.location(0, 0):
            print(self.CYAN + "-- Goodbye! --" + self.NORMAL)
        # Bring the cursor back
        if os_name == "posix":
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def _set_open(self):
        # Set today's date
        self.today = datetime.today().day
        # Get the day's opening price for each currency
        self.btc_open = float(GDAX.PublicClient(product_id="BTC-USD").getProduct24HrStats()["open"])
        self.eth_open = float(GDAX.PublicClient(product_id="ETH-USD").getProduct24HrStats()["open"])
        self.ltc_open = float(GDAX.PublicClient(product_id="LTC-USD").getProduct24HrStats()["open"])

    def _print_message(self):
        # clear terminal
        print(term.clear)

        # Show time of last message if option is enabled
        if self._show_time:
            with term.location(0, term.height - 1):
                # If we've received messages, print out last received time
                # else print "retrieving data"
                if self.last_msg_time:
                    t = strftime("%I:%M %p", localtime(self.last_msg_time))
                    sys.stdout.write("-- last update: %s --" % t)
                else:
                    sys.stdout.write("-- retrieving data --")

        # move to x,y location 0,0 (top left)
        with term.location(0, 0):
            sys.stdout.write(self.CLEARTOEND)

            # If we're showing BTC-USD, print values
            if (self._btc):
                if (self.btc_up):
                    sys.stdout.write(self.GREEN)
                else:
                    sys.stdout.write(self.RED)

                sys.stdout.write("BTC-USD: $%.2f" % self.btc_price)
                if self._diff:
                    if self.btc_up:
                        sys.stdout.write(" (+")
                    else:
                        sys.stdout.write(" (-")

                    sys.stdout.write("%.2f%%)" % self.btc_amt_change)

            # Show pipe separator if we're showing BTC-USD and ETH-USD
            if (self._btc and self._eth):
                sys.stdout.write(self.CYAN + " | ")

            # If we're showing ETH-USD, print values
            if (self._eth):
                if (self.eth_up):
                    sys.stdout.write(self.GREEN)
                else:
                    sys.stdout.write(self.RED)

                sys.stdout.write("ETH-USD: $%.2f" % self.eth_price)
                if self._diff:
                    if self.eth_up:
                        sys.stdout.write(" (+")
                    else:
                        sys.stdout.write(" (-")

                    sys.stdout.write("%.2f%%)" % self.eth_amt_change)

            # Show pipe separator if we're showing LTC-USD and ETH-USD or BTC-USD
            if (self._ltc and (self._eth or self._btc)):
                sys.stdout.write(self.CYAN + " | ")

            # If we're showing LTC-USD, print values
            if (self._ltc):
                if (self.ltc_up):
                    sys.stdout.write(self.GREEN)
                else:
                    sys.stdout.write(self.RED)

                sys.stdout.write("LTC-USD: $%.2f" % self.ltc_price)
                if self._diff:
                    if self.ltc_up:
                        sys.stdout.write(" (+")
                    else:
                        sys.stdout.write(" (-")

                    sys.stdout.write("%.2f%%)" % self.ltc_amt_change)

            sys.stdout.write("\r")
            sys.stdout.flush()


# Start the websocket client
ws_client = GDAXMessageFeed(url, prods, diff, show_time)
ws_client.start()

# Listen for Escape key to quit and close websocket if so
while (key != keys.ESCAPE):
    key = getkey()
    if (key == keys.ESCAPE):
        ws_client.close()
