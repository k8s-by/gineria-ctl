import numpy as np
import pandas as pd
import pandas_ta as ta
from finta import TA as finta


class Indicators:

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def price(self):
        return self.dataframe['Close'].iloc[-1]

    def rsi(self, length=14):
        return self.dataframe.ta.rsi(length=length).iloc[-1]

    def mfi(self, length=14):
        return self.dataframe.ta.mfi(length=length).iloc[-1]

    def cmo(self, length=14):
        return self.dataframe.ta.cmo(length=length).iloc[-1]

    def cci(self, length=14):
        return self.dataframe.ta.cci(length=length).iloc[-1]

    def macd_strategy(self, fast=12, slow=26, signal=9, debug=False):
        macd = self.dataframe.ta.macd(fast=fast, slow=slow, signal=signal)

        macd['cross'] = 0.0
        macd['cross'] = np.where(macd['MACD_12_26_9'] > macd['MACDs_12_26_9'], 1.0, 0.0)
        self.dataframe['macdcross'] = macd['cross'].diff()

        self.dataframe['macdmin'] = (np.where(
            (macd['MACD_12_26_9'].shift(2) > macd['MACD_12_26_9'].shift(1))
            &
            (macd['MACD_12_26_9'] > macd['MACD_12_26_9'].shift(1)),
            1.0, 0.0))

        self.dataframe['macdmax'] = (np.where(
            (macd['MACD_12_26_9'].shift(2) < macd['MACD_12_26_9'].shift(1))
            &
            (macd['MACD_12_26_9'] < macd['MACD_12_26_9'].shift(1)),
            1.0, 0.0))

        if debug:
            print(self.dataframe.to_string())

        return self.dataframe['macdcross'].iloc[-1], self.dataframe['macdmin'].iloc[-1], self.dataframe['macdmax'].iloc[-1]
