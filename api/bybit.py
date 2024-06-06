from pybit.unified_trading import HTTP
from api.base import APIBase
import pandas as pd
import datetime


class Bybit(APIBase):
    client = ""

    def __init__(self, api_key="Key", api_secret="Secret"):
        self.api_key = api_key
        self.api_secret = api_secret

    def connect_to_api(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = HTTP(api_key=api_key, api_secret=api_secret, testnet=False)

    def get_api_key(self):
        print("Your Api Key: {}".format(self.api_key))

    def get_api_secret(self):
        print("Your Api Secret: {}".format(self.api_secret))

    def get_dataframe(self, symbol, interval, limit, category='linear'):

        result = self.client.get_kline(category=category, symbol=symbol, interval=interval, limit=limit).get('result')

        klines = result.get('list', None)

        if not klines:
            return

        ohlc_data = [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]), float(kline[5])] for kline in klines]

        df = pd.DataFrame(ohlc_data, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        timestamps = [datetime.datetime.fromtimestamp(int(kline[0]) / 1000) for kline in klines]
        df['Timestamp'] = timestamps
        df.set_index('Timestamp', inplace=True)

        df.sort_index(inplace=True)

        return df

