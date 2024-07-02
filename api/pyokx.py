import okx.MarketData as MarketData
from api.base import APIBase
import pandas as pd
import datetime


class OKX(APIBase):
    client = ""

    def __init__(self, api_key="Key", api_secret="Secret"):
        self.api_key = api_key
        self.api_secret = api_secret

    def connect_to_api(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        flag = "0"  # live trading: 0, demo trading: 1
        self.client = MarketData.MarketAPI(flag=flag, debug=False)

    def get_api_key(self):
        print("Your Api Key: {}".format(self.api_key))

    def get_api_secret(self):
        print("Your Api Secret: {}".format(self.api_secret))

    def get_dataframe(self, symbol, interval, limit, category='linear'):

        result = self.client.get_candlesticks(instId=symbol, bar=interval, limit=limit)

        klines = result.get('data', None)

        if not klines:
            return

        ohlc_data = [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]), float(kline[5])] for kline in klines]

        df = pd.DataFrame(ohlc_data, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        timestamps = [datetime.datetime.fromtimestamp(int(kline[0]) / 1000) for kline in klines]
        df['Timestamp'] = timestamps
        df.set_index('Timestamp', inplace=True)

        df.sort_index(inplace=True)

        return df

