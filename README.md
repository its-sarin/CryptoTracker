# CryptoTracker
Terminal-based Cryptocurrency ticker using the GDAX api

![Screenshot](crypto_tracker_ss.png?raw=true)

### Requirements
* Python 2.7
* GDAX Python wrapper
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

Press <kbd>Escape</kbd> to quit
