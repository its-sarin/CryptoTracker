# CryptoTracker
Simple terminal-based Cryptocurrency price tracker using the GDAX api

Default view:
![Screenshot](crypto_tracker_ss.png?raw=true)
With price differences suppressed:
![Screenshot](crypto_tracker_ss_diff.png?raw=true)

### Requirements
* Python 2.7
* [GDAX Python wrapper](https://github.com/danpaquin/GDAX-Python)
* getkey
* blessings

```sh
pip install GDAX getkey blessings
```

### Usage

To show all three cryptocurrencies (BTC, ETH, LTC):
```sh
python crypto_tracker.py
```

To limit which cryptocurrencies to track:
```sh
python crypto_tracker.py -b
python crypto_tracker.py -e
python crypto_tracker.py -l
python crypto_tracker.py -b -l
```

To display the percent difference since day's open price:
```sh
python crypto_tracker.py -p
python crypto_tracker.py --pdiff
```

To display time of last received update:
```sh
python crypto_tracker.py -t
python crypto_tracker.py --time
```

Press <kbd>Escape</kbd> to quit

### Known Issues
* Websocket does on occasion drop out, either due to server or client connection. When this happens there is no automatic reconnect and you will have to quit out manually and restart. For this reason, an optional display of last update time was added so it's easier to notice when this has happened.
