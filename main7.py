from api.ginarea import Ginarea
from api.pyokx import OKX
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
        'symbol': 'ETH-USDT-SWAP',
        'long_id': '4396470606',
        'strategy': 'ema_bands',
        'min_orders': 40,
        'max_orders': 40,
        'order_step': 10,
        'autogrid': False
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
        df = api.get_dataframe(symbol, interval='5m', limit=500, category='linear')

    except Exception as e:
        logger.error(f"Failed to get {symbol} prices {e}")
        return None

    idx = Indicators(df)

    data = (idx.ema3tr_bands(ema1_period=21, ema2_period=21, ema3_period=21, atr_period=300,
                             mult1=1.6, mult2=1.6, mult3=1.6)
            .rsi()
            .last())

    return data


def get_data_1h(api, symbol, interval='1', limit=200, category='linear'):
    try:
        # Get data from bybit for tf=5min, last 200 kline in usdt_features. Use category='spot' for spot data.
        df = api.get_dataframe(symbol, interval='1H', limit=300, category='linear')

    except Exception as e:
        logger.error(f"Failed to get {symbol} prices {e}")
        return None

    idx = Indicators(df)

    data = (idx.keltner().last())

    return data


def long_bot_update(g, df, symbol, bot_id, strategy='ema_bands'):
    try:
        bot = g.status(bot_id)

        logger.info(
            f"[{strategy}] {bot['name']} updated from {bot['bottom']:.9f}->{df['emalong_down']:.9f}  {bot['top']:.9f}->{df['emalong_up']:.9f}")
        g.update(bot_id, bottom=df['emalong_down'], top=df['emalong_up'])

    except Exception as e:
        logger.error(f"Failed to update bot id {symbol}/{bot_id}: {e}")


def short_bot_update(g, df, symbol, bot_id, strategy='ema_bands'):
    try:
        bot = g.status(bot_id)

        logger.info(
            f"[{strategy}] {bot['name']} updated from {bot['bottom']:.9f}->{df['emashort_up']:.9f}  {bot['top']:.9f}->{df['emashort_down']:.9f}")
        g.update(bot_id, bottom=df['emashort_up'], top=df['emashort_down'])

    except Exception as e:
        logger.error(f"Failed to update bot id {symbol}/{bot_id}: {e}")


async def bot_update(i):
    # Connect to API
    api = OKX()
    api.connect_to_api("-1", "-1")

    # Connect to ginarea
    g = Ginarea(GINAREA_LOGIN, ENCRYPTED_PASSWORD, retries=5)

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


async def order_update(i):
    # Connect to ginarea
    g = Ginarea(GINAREA_LOGIN, ENCRYPTED_PASSWORD, retries=5)

    symbol = i['symbol']
    long_id = i.get('long_id')
    short_id = i.get('short_id')
    min_orders = i.get('min_orders')
    max_orders = i.get('max_orders')
    order_step = i.get('order_step')

    logger.info(f"Order update of {symbol} started")

    while True:

        # long bot order number update
        if long_id is not None:
            bot = g.stats(long_id)

            if bot['orderCount'] >= bot['orderTotal']:

                if bot['orderTotal'] >= max_orders:
                    logger.error(
                        f"Bot {bot['name']} has reached order limit. Increasing not possible."
                    )

                else:
                    logger.info(
                        f"Bot {bot['name']} orderTotal increased from {bot['orderTotal']} to {bot['orderTotal'] + order_step}")

                    g.update(long_id, orders=bot['orderTotal'] + order_step)

            elif (bot['orderCount'] < (bot['orderTotal'] - order_step * 1.5)
                  and
                  (bot['orderTotal'] - order_step > min_orders)):

                logger.info(
                    f"Bot {bot['name']} decreasing orderTotal from {bot['orderTotal']} to {bot['orderTotal'] - order_step}")

                g.update(long_id, orders=bot['orderTotal'] - order_step)

        # short bot order number update
        # TODO

        await asyncio.sleep(28800)


async def gridstep_update(i):
    # Connect to ginarea
    g = Ginarea(GINAREA_LOGIN, ENCRYPTED_PASSWORD, retries=5)

    symbol = i['symbol']
    long_id = i.get('long_id')
    short_id = i.get('short_id')
    autogrid = i.get('autogrid')
    min_gridstep = i.get('min_gridstep')
    max_gridstep = i.get('max_gridstep')

    if autogrid:
        logger.warning(f"Gridstep update of {symbol} started")

        while True:

            api = OKX()
            api.connect_to_api("-1", "-1")

            # long bot order number update
            if long_id is not None:

                data = get_data_1h(api, symbol)
                bot = g.stats(long_id)

                if data['Close'] > data['kc_center']:
                    if bot['gridstep'] != max_gridstep:
                        logger.warning(
                            f"Bot {bot['name']} gridstep updated to {max_gridstep}")
                        g.update(long_id, gridstep=max_gridstep)

                else:
                    if bot['gridstep'] != min_gridstep:
                        logger.warning(
                            f"Bot {bot['name']} gridstep updated to {min_gridstep}")
                        g.update(long_id, gridstep=min_gridstep)

            # short bot order number update
            # TODO

            await asyncio.sleep(3600)


async def main():
    tasks = []

    for i in BOT_LIST:
        tasks.append(bot_update(i))
        tasks.append(order_update(i))
        tasks.append(gridstep_update(i))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logger.add('main1.log', retention='2d')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
