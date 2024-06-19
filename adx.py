from api.ginarea import Ginarea
from api.bybit import Bybit
from lib.indicators import Indicators
import os
import time
import datetime

ARROW_UP = u'\u2191'
ARROW_DOWN = u'\u2193'

# Login and password in environment variables
GINAREA_LOGIN = os.environ["GINAREA_LOGIN"]
ENCRYPTED_PASSWORD = os.environ["GINAREA_PASSWORD"]

SLEEP_TIMEOUT = 60  # once in 15 min start script

TOP_OFFSET = 1.003
BOTTOM_OFFSET = 0.097


ADX_LIMIT = 25

BOT_LIST = [
    {
        'symbol': '1000BONKUSDT',
        'long_id': '4399148790',
        'short_id': '5177575237'
    }
]


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

            data = idx.adx().last()

            try:
                if data['adx'] < ADX_LIMIT:
                    long_id = i.get('long_id')
                    if long_id is not None:
                        bot = g.status(long_id)

                        bottom = float(data['Close'] * BOTTOM_OFFSET)
                        top = float(data['Close'] * TOP_OFFSET)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [adx] {bot['name']} enabled {bot['bottom']}->{bottom} {bot['top']}->{top}")

                        g.update(long_id, bottom=bottom, top=top, disable=False)

                    short_id = i.get('short_id')
                    if short_id is not None:
                        bot = g.status(short_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [adx] {bot['name']} enabled {bot['bottom']}->{bottom} {bot['top']}->{top}")
                        g.update(short_id, bottom=bottom, top=top, disable=False)

                if data['adx'] >= ADX_LIMIT:
                    long_id = i.get('long_id')
                    if long_id is not None:
                        bot = g.status(long_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [adx] {bot['name']} disabled")
                        g.update(long_id, disable=True)

                    short_id = i.get('short_id')
                    if short_id is not None:
                        bot = g.status(short_id)

                        print(
                            f"\"{now.strftime('%Y-%m-%d %H:%M:%S')}\" [adx] {bot['name']} disabled")
                        g.update(short_id, disable=True)

            except Exception as e:
                print(f"Failed to update bot id {symbol}: {e}")

        time.sleep(SLEEP_TIMEOUT)


