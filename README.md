# CryptoTracker
Simple terminal-based Cryptocurrency price tracker using the GDAX api

Default view:
![Screenshot](crypto_tracker_ss.png?raw=true)
With price differences suppressed:
![Screenshot](crypto_tracker_ss_nodiff.png?raw=true)

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

To suppress display of price difference since day's open price:
```sh
python crypto_tracker.py --nodiff
```

Press <kbd>Escape</kbd> to quit
