from api.ginarea import Ginarea
from api.bybit import Bybit
from lib.indicators import Indicators
import os
import time
import datetime
import asyncio
from functools import wraps
from loguru import logger
from requests import HTTPError

ARROW_UP = u'\u2191'
ARROW_DOWN = u'\u2193'

# Login and password in environment variables
GINAREA_LOGIN = os.environ["GINAREA_LOGIN"]
ENCRYPTED_PASSWORD = os.environ["GINAREA_PASSWORD"]

SLEEP_TIMEOUT = 300

STOP_OFFSET = 0.000

BOT_LIST = [
    {
        'symbol': 'CHZUSDT',
        'long_id': '5879141682',
        'strategy': 'ema_bands'
    },
    {
        'symbol': 'GALAUSDT',
        'long_id': '5992216014',
        'strategy': 'ema_bands'
    },
    {
        'symbol': 'WLDUSDT',
        'long_id': '5755294292',
        'strategy': 'ema_bands'
    },
]


def timeit(func):
    async def process(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        st = time.time()
        result = await process(func, *args, **kwargs)
        ed = time.time()
        logger.info(f"{func.__name__} took time: {ed - st:.3f} secs")
        return result

    return wrapper


def get_data(api, symbol, interval='1', limit=200, category='linear'):
    try:
        # Get data from bybit for tf=5min, last 200 kline in usdt_features. Use category='spot' for spot data.
        df = api.get_dataframe(symbol, interval='5', limit=500, category='linear')

    except Exception as e:
        logger.error(f"Failed to get {symbol} prices {e}")
        return None

    idx = Indicators(df)

    data = (idx.ema3tr_bands(ema1_period=21, ema2_period=9, ema3_period=150, atr_period=500,
                             mult1=1.6, mult2=1.2, mult3=1.2)
            .rsi()
            .last())

    return data


def long_bot_update(g, df, symbol, bot_id, strategy='ema_band'):
    try:
        bot = g.status(bot_id)

        logger.info(
            f"[{strategy}] {bot['name']} updated from {bot['bottom']:.4f}->{df['emalong_down']:.4f}  {bot['top']:.4f}->{df['emalong_up']:.4f}")
        g.update(bot_id, bottom=df['emalong_down'], top=df['emalong_up'])

    except Exception as e:
        logger.error(f"Failed to update bot id {symbol}/{bot_id}: {e}")


def short_bot_update(g, data, symbol, bot_id, strategy='supertrend'):
    try:
        bot = g.status(bot_id)

        # TODO

    except Exception as e:
        logger.error(f"Failed to update bot id {symbol}/{bot_id}: {e}")


async def bot_update(i):
    # Connect to API
    api = Bybit()
    api.connect_to_api("Key", "Secret")

    # Connect to ginarea
    g = Ginarea(GINAREA_LOGIN, ENCRYPTED_PASSWORD, retries=3)

    symbol = i['symbol']
    strategy = i['strategy']
    long_id = i.get('long_id')
    short_id = i.get('short_id')

    logger.info(f"Thread of {symbol} started")

    while True:
        start_time = time.time()

        # get data
        data = get_data(api, symbol)

        # long bot update
        if long_id is not None:
            long_bot_update(g, data, symbol, long_id, strategy)

        # short bot update
        if short_id is not None:
            short_bot_update(g, data, symbol, short_id, strategy)

        # measure runtime and sleep
        run_time = time.time() - start_time

        if run_time < SLEEP_TIMEOUT:
            # time.sleep(SLEEP_TIMEOUT - run_time)

            await asyncio.sleep(SLEEP_TIMEOUT)


async def main():
    tasks = []

    for i in BOT_LIST:
        tasks.append(bot_update(i))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logger.add('main1.log', retention='10d')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
