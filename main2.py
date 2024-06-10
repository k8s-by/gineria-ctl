from api.ginarea import Ginarea
from api.bybit import Bybit
from lib.indicators import Indicators
import os
import time
import datetime

ARROW_UP = u'\u2191'
ARROW_DOWN = u'\u2193'

# Login and password in environment variables
GINAREA_LOGIN = os.environ["GINAREA_LOGIN"]  # login email
ENCRYPTED_PASSWORD = os.environ["GINAREA_PASSWORD"]  # This is not clear password. Get this value from F12 tools when login to gineria

SLEEP_TIMEOUT = 900  # once in 15 min start script

STOP_OFFSET = 0.001  # offset as 2.5% of the current price

BOT_LIST = [
    {
        'symbol': '1000BONKUSDT',
        'long_id': '4399148790',
        'short_id': '5177575237',
        'strategy': 'supertrend'
    },
    {
        'symbol': 'KASUSDT',
        'long_id': '6345446123',
        'short_id': '5462860523',
        'strategy': 'pivot'
    }
]



'''
ОБЯЗАТЕЛЬНО !!!
В long-боте должен быть установлен "Order trading range/From" (любое числовое значение)
В shot-боте "Order trading range/To"
'''


if __name__ == "__main__":
    # Connect to API
    api = Bybit()
    api.connect_to_api("Key", "Secret")

    # Connect to ginarea
    g = Ginarea(GINAREA_LOGIN, ENCRYPTED_PASSWORD)
    # g.check_token()
    # exit(0)

    while True:
        for i in BOT_LIST:

            symbol = i['symbol']
            strategy = i['strategy']

            now = datetime.datetime.now()

            # Get 15m dataframe
            try:
                # Get data from bybit for tf=15min, last 200 kline in usdt_features. Use category='spot' for spot data.
                df = api.get_dataframe(symbol, interval='15', limit=200, category='linear')

            except Exception as e:
                print(f"Failed to get {symbol} prices {e}")
                break

            idx = Indicators(df)

            data = idx.pivot(left_bars=4, right_bars=2).supertrend(length=10, multiplier=3).last()

            price = idx.price()
            new_limit = price * (1.0 - STOP_OFFSET)

            try:
                if strategy == 'pivot' and (data['long_supertrend'] == 1 or data['short_supertrend']):

                    long_id = i.get('long_id')
                    if long_id is not None:
                        bot = g.status(long_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [{strategy}] {bot['name']} updated {ARROW_DOWN} from {bot['bottom']} to {data['Low']}")
                        g.update(long_id, bottom=data['Low'])

                    short_id = i.get('short_id')
                    if short_id is not None:
                        bot = g.status(short_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [{strategy}]  {bot['name']} updated {ARROW_UP} from {bot['top']} to {data['High']}")
                        g.update(short_id, top=data['High'])

                elif strategy == 'supertend' and (data['long_supertrend'] == 1 or data['hort_supertrend'] == 1):

                    long_id = i.get('long_id')
                    if long_id is not None:
                        bot = g.status(long_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [{strategy}] {bot['name']} updated {ARROW_DOWN} from {bot['bottom']} to {data['Low']}")
                        g.update(long_id, bottom=data['Low'])

                    short_id = i.get('short_id')
                    if short_id is not None:
                        bot = g.status(short_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [{strategy}]  {bot['name']} updated {ARROW_UP} from {bot['top']} to {data['High']}")
                        g.update(short_id, top=data['High'])

                else:
                    long_id = i.get('long_id')
                    if long_id is not None:
                        bot = g.status(long_id)

                        if bot['bottom'] < new_limit:
                            print(
                                f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [price] {bot['name']} updated {ARROW_UP} from {bot['bottom']} to {new_limit}")
                            g.update(long_id, bottom=new_limit)


                    short_id = i.get('short_id')
                    if short_id is not None:
                        bot = g.status(short_id)

                        if bot['top'] > new_limit:
                            print(
                                f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [price] {bot['name']} updated {ARROW_DOWN} from {bot['top']} to {new_limit}")
                            g.update(short_id, top=new_limit)

            except Exception as e:
                print(f"Failed to update bot id {symbol}: {e}")

        time.sleep(SLEEP_TIMEOUT)


