import numpy as np
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
