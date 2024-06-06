from api.ginarea import Ginarea
from api.bybit import Bybit
from lib.indicators import Indicators
import time
import os

# Login and password in environment variables
GINAREA_LOGIN = os.environ["GINAREA_LOGIN"]  # login email
ENCRYPTED_PASSWORD = os.environ["GINAREA_PASSWORD"]  # This is not clear password. Get this value from F12 tools when login to gineria

SLEEP_TIMEOUT = 900  # once in 15 min start script

STOP_OFFSET = 0.001  # offset as 2.5% of the current price

BOT_LIST = [
    # {
    #     'symbol': 'DOGEUSDT',
    #     'short_id': ''
    # },
    {
        'symbol': '1000BONKUSDT',
        'long_id': '',
        'short_id': ''
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

    while True:
        for i in BOT_LIST:

            symbol = i['symbol']

            # Get 15m dataframe
            try:
                # Get data from bybit for tf=15min, last 200 kline in usdt_features. Use category='spot' for spot data.
                df = api.get_dataframe(symbol, interval='15', limit=200, category='linear')

            except Exception as e:
                print(f"Failed to get {symbol} prices {e}")
                break

            idx = Indicators(df)

            idx.macd_strategy(debug=True)

            # LONG BOT
            long_id = i.get('long_id')
            if long_id is not None:

                try:
                    bot = g.status(long_id)

                    new_limit = idx.price() * (1.0 - STOP_OFFSET)

                    if bot['bottom'] < new_limit:
                        print(f"Bot {bot['name']} updated, limit changed from {bot['bottom']:.6f} to {new_limit:.6f}")
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
                        print(f"Bot {bot['name']} updated, limit changed from {bot['top']:.6f} to {new_limit:.6f}")
                        g.update(short_id, top=new_limit)

                except Exception as e:
                    print(f"Failed to update bot id {symbol}/{short_id}: {e}")

        time.sleep(SLEEP_TIMEOUT)
