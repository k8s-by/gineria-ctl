from api.ginarea import Ginarea
from api.bybit import Bybit
from lib.indicators import Indicators
import datetime
import time
import os

# Login and password in environment variables

# login email
GINAREA_LOGIN = os.environ["GINAREA_LOGIN"]

# This is not clear password. Get this value from F12 tools when login to gineria
ENCRYPTED_PASSWORD = os.environ["GINAREA_PASSWORD"]

# Run the check once per SLEEP_TIME
SLEEP_TIMEOUT = 300

# Offset as 2.5% of the current price
STOP_OFFSET = 0.001

BOT_LIST = [
    {
        'symbol': '1000BONKUSDT',
        'long_id': '4399148790',
        'short_id': '5177575237'
    },
    {
        'symbol': 'KASUSDT',
        'long_id': '6345446123',
        'short_id': '5462860523'
    }
]

'''
ОБЯЗАТЕЛЬНО !!!
В long-боте должен быть установлен "Order trading range/From" (любое числовое значение)
В shot-боте "Order trading range/To"
'''

ARROW_UP = u'\u2191'
ARROW_DOWN = u'\u2193'

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

            now = datetime.datetime.now()

            # Get 15m dataframe
            try:
                # Get data from bybit for tf=15min, last 200 kline in usdt_features. Use category='spot' for spot data.
                df = api.get_dataframe(symbol, interval='15', limit=200, category='linear')

            except Exception as e:
                print(f"Failed to get {symbol} prices {e}")
                break

            idx = Indicators(df)

            data = idx.max('Close', 'pricemax').pivot(min_tick=0.0001).last()


            # LONG BOT
            long_id = i.get('long_id')
            if long_id is not None:

                try:
                    bot = g.status(long_id)

                    new_limit = idx.price() * (1.0 - STOP_OFFSET)

                    # setup current price as limit
                    if bot['bottom'] < new_limit:
                        print(f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" {bot['name']} updated {ARROW_UP} from {bot['bottom']} to {new_limit}")
                        g.update(long_id, bottom=new_limit)

                    # check pivot // long_pivot field
                    if data['long_pivot'] == 1:
                        print(f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" {bot['name']} updated {ARROW_DOWN} from {bot['bottom']} to {new_limit}")
                        g.update(long_id, bottom=new_limit)

                except Exception as e:
                    print(f"Failed to update bot id {symbol}/{long_id}: {e}")

            # SHORT BOT
            short_id = i.get('short_id')
            if short_id is not None:

                try:
                    bot = g.status(short_id)

                    new_limit = idx.price() * (1.0 + STOP_OFFSET)

                    if bot['top'] > new_limit:
                        print(f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" {bot['name']} updated {ARROW_DOWN} from {bot['top']} to {new_limit}")
                        g.update(short_id, top=new_limit)

                    # check pivot // short_pivot field
                    if data['short_pivot'] == 1:
                        print(f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" {bot['name']} updated {ARROW_UP} from {bot['bottom']} to {new_limit}")
                        g.update(short_id, top=new_limit)

                except Exception as e:
                    print(f"Failed to update bot id {symbol}/{short_id}: {e}")

        time.sleep(SLEEP_TIMEOUT)
