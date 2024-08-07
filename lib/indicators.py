import numpy as np
import pandas as pd
import pandas_ta as ta
from finta import TA as finta


class Indicators:

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def last(self):
        return self.dataframe.iloc[-1]

    def resample(self, interval):

        # return self.dataframe.resample(interval).last()

        df = self.dataframe.resample(interval).agg({"Open": "first", "High": ["max"], "Low": ["min"],
                                                    "Close": "last", "Volume": ["sum"]})

        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        return df

    def price(self):
        return self.dataframe['Close'].iloc[-1]

    def rsi(self, period=14, outbound_column='rsi'):
        self.dataframe[outbound_column] = self.dataframe.ta.rsi(length=period)

        return self

    def mfi(self, length=14):
        return self.dataframe.ta.mfi(length=length).iloc[-1]

    def cmo(self, length=14):
        return self.dataframe.ta.cmo(length=length).iloc[-1]

    def cci(self, length=14):
        return self.dataframe.ta.cci(length=length).iloc[-1]

    def adx(self, period=14, outbound_column='adx'):
        # self.dataframe[outbound_column] = finta.ADX(self.dataframe, period=period)
        self.dataframe[outbound_column] = ta.adx(self.dataframe['High'], self.dataframe['Low'], self.dataframe['Close'],
                                                 length=period)[f"ADX_{period}"]

        return self

    def ema2_bands(self, ema1_period=21, ema2_period=150, atr_period=500, mult1=1.6, mult2=1.2):

        self.dataframe['range'] = ta.true_range(self.dataframe['High'], self.dataframe['Low'], self.dataframe['Close'])

        self.ema(period=ema1_period, inbound_column='close', outbound_column='ema1_tmp')
        self.ema(period=ema2_period, inbound_column='close', outbound_column='ema2_tmp')
        self.ema(period=atr_period, inbound_column='range', outbound_column='emarange')

        self.dataframe['ema1_upband'] = self.dataframe['ema1_tmp'] + self.dataframe['emarange'] * mult1
        self.dataframe['ema1_downband'] = self.dataframe['ema1_tmp'] - self.dataframe['emarange'] * mult1

        self.dataframe['ema2_upband'] = self.dataframe['ema2_tmp'] + self.dataframe['emarange'] * mult2
        self.dataframe['ema2_downband'] = self.dataframe['ema2_tmp'] - self.dataframe['emarange'] * mult2

        # max (ema1_downband, ema2_downband)
        self.dataframe['ema_down'] = np.where(
            self.dataframe['ema1_downband'] > self.dataframe['ema2_downband'],
            self.dataframe['ema1_downband'],
            self.dataframe['ema2_downband']
        )

        # min (ema1_upband, ema2_upband)
        self.dataframe['ema_up'] = np.where(
            self.dataframe['ema1_upband'] < self.dataframe['ema2_upband'],
            self.dataframe['ema1_upband'],
            self.dataframe['ema2_upband']
        )

        self.dataframe['ema_up'] = np.where(
            self.dataframe['ema_up'] > self.dataframe['ema_down'],
            self.dataframe['ema_up'],
            self.dataframe['ema_down']
        )

        self.drop(columns=['range', 'emarange', 'ema1_tmp', 'ema2_tmp', 'ema1_upband', 'ema1_downband', 'ema2_upband',
                           'ema2_downband'])

        return self

    def ema3tr_bands(self, ema1_period=21, ema2_period=9, ema3_period=150, atr_period=500,
                     mult1=1.6, mult2=1.2, mult3=1.2, emashort_prefix='emashort', emalong_prefix='emalong'):

        self.dataframe['range'] = ta.true_range(self.dataframe['High'], self.dataframe['Low'], self.dataframe['Close'])

        self.ema(period=ema1_period, inbound_column='close', outbound_column='ema1_tmp')
        self.ema(period=ema2_period, inbound_column='close', outbound_column='ema2_tmp')
        self.ema(period=ema3_period, inbound_column='close', outbound_column='ema3_tmp')
        self.ema(period=atr_period, inbound_column='range', outbound_column='emarange')

        self.dataframe['ema1_upband'] = self.dataframe['ema1_tmp'] + self.dataframe['emarange'] * mult1
        self.dataframe['ema1_downband'] = self.dataframe['ema1_tmp'] - self.dataframe['emarange'] * mult1

        self.dataframe['ema2_upband'] = self.dataframe['ema2_tmp'] + self.dataframe['emarange'] * mult2
        self.dataframe['ema2_downband'] = self.dataframe['ema2_tmp'] - self.dataframe['emarange'] * mult2
        self.dataframe['ema3_upband'] = self.dataframe['ema3_tmp'] + self.dataframe['emarange'] * mult3
        self.dataframe['ema3_downband'] = self.dataframe['ema3_tmp'] - self.dataframe['emarange'] * mult3

        # max (ema2_downband, ema3_downband)
        self.dataframe[f'{emalong_prefix}_down'] = np.where(
            self.dataframe['ema2_downband'] > self.dataframe['ema3_downband'],
            self.dataframe['ema2_downband'],
            self.dataframe['ema3_downband']
        )

        # max (ema1, emalong_down)
        self.dataframe[f'{emalong_prefix}_up'] = np.where(
            self.dataframe['ema1_upband'] > self.dataframe[f'{emalong_prefix}_down'],
            self.dataframe['ema1_upband'],
            self.dataframe[f'{emalong_prefix}_down']
        )

        # min (ema2_upband, ema3_upband)
        self.dataframe[f'{emashort_prefix}_down'] = np.where(
            self.dataframe['ema2_upband'] < self.dataframe['ema3_upband'],
            self.dataframe['ema2_upband'],
            self.dataframe['ema3_upband']
        )

        # min (ema1_downband, emashort_up
        self.dataframe[f'{emashort_prefix}_up'] = np.where(
            self.dataframe['ema1_downband'] < self.dataframe[f'{emashort_prefix}_down'],
            self.dataframe['ema1_downband'],
            self.dataframe[f'{emashort_prefix}_down']
        )

        self.drop(columns=['range', 'emarange', 'ema1_tmp', 'ema2_tmp', 'ema3_tmp', 'ema1_upband', 'ema1_downband',
                           'ema2_upband', 'ema2_downband', 'ema3_upband', 'ema3_downband'])

        return self

    def bbands(self, period=20, std=2):
        bbands = finta.BBANDS(self.dataframe, period=20, std_multiplier=std)
        self.dataframe['bbands_upper'] = bbands['BB_UPPER']
        self.dataframe['bbands_lower'] = bbands['BB_LOWER']

        self.cross('bbands_upper', 'Close', 'bb_upper_cross')
        self.cross('Close', 'bbands_lower', 'bb_lower_cross')

        self.drop(columns=['bbands_upper', 'bbands_lower'])

        return self

    def keltner(self, period=20, atr_period=10, kc_mult=2):

        # kc = finta.KC(self.dataframe, period=period, atr_period=atr_period, kc_mult=kc_mult)
        # print(kc)
        # self.dataframe['kc_upper'] = kc['KC_UPPER']
        # self.dataframe['kc_lower'] = kc['KC_LOWER']
        kc = ta.kc(self.dataframe['High'], self.dataframe['Low'], self.dataframe['Close'], length=period, scalar=kc_mult)

        self.dataframe['kc_center'] = kc[f'KCBe_{period}_{kc_mult}.0']

        # self.cross('kc_upper', 'Close', 'kc_upper_cross')
        # self.cross('Close', 'kc_lower', 'kc_lower_cross')
        #
        # self.drop(columns=['kc_upper', 'kc_lower'])

        return self

    def cci_bands(self, period=14, upper_band=100, lower_band=-100):

        self.dataframe['cci'] = finta.CCI(self.dataframe, period=period)
        self.dataframe['cci_upper'] = upper_band
        self.dataframe['cci_lower'] = lower_band

        self.cross('cci_upper', 'cci', 'cci_upper_cross')
        self.cross('cci', 'cci_lower', 'cci_lower_cross')

        self.drop(columns=['cci', 'cci_upper', 'cci_lower'])

        return self

    def pivot(self, left_bars=4, right_bars=2, min_tick=0.0001):
        pv = pd.DataFrame()
        pv["swh_cond"] = (
                (self.dataframe['High'] >= self.dataframe['High'].rolling(left_bars).max().shift(1))
                &
                (self.dataframe['High'] >= self.dataframe['High'].rolling(right_bars).max().shift(-right_bars))
        )

        pv["hprice"] = np.where(pv['swh_cond'], self.dataframe['High'], np.nan)
        pv["hprice"] = pv["hprice"].ffill().shift(right_bars).fillna(value=0)

        # Swing Low, Condition and lprice
        pv["swl_cond"] = (
                (self.dataframe['Low'] <= self.dataframe['Low'].rolling(left_bars).min().shift(1))
                &
                (self.dataframe['Low'] <= self.dataframe['Low'].rolling(right_bars).min().shift(-right_bars))
        )

        pv["lprice"] = np.where(pv['swl_cond'], self.dataframe['Low'], np.nan)
        pv["lprice"] = pv["lprice"].ffill().shift(right_bars).fillna(value=0)

        self.dataframe["lprice"] = self.dataframe['Low'].shift(-right_bars, fill_value=0).rolling(left_bars).min()
        self.dataframe['hprice'] = self.dataframe['High'].shift(-right_bars, fill_value=0).rolling(left_bars).max()

        # Long crossover
        # self.dataframe["long_pivot"] = np.where(
        #         (self.dataframe['High'] >= pv['hprice'].shift(1) + min_tick)
        #         &
        #         (self.dataframe['High'].shift(1) < pv['hprice'].shift(2) + min_tick),
        #         1.0, 0.0)
        self.dataframe["long_pivot"] = np.where(
            (self.dataframe['High'] >= pv['hprice'].shift(1))
            &
            (self.dataframe['High'].shift(1) < pv['hprice'].shift(2)),
            1.0, 0.0)

        # Short crossover
        # self.dataframe["short_pivot"] = np.where(
        #         (self.dataframe['Low'] <= pv['lprice'].shift(1) - min_tick)
        #         &
        #         (self.dataframe['Low'].shift(1) > pv['lprice'].shift(2) - min_tick),
        #         1.0, 0.0)
        self.dataframe["short_pivot"] = np.where(
            (self.dataframe['Low'] <= pv['lprice'].shift(1))
            &
            (self.dataframe['Low'].shift(1) > pv['lprice'].shift(2)),
            1.0, 0.0)

        # self.dataframe["trade_price"] = np.where(self.dataframe["long_pivot"],
        #                                          pv['hprice'] + min_tick,
        #                                          np.where(self.dataframe["short_pivot"],
        #                                          pv['lprice'] - min_tick, np.nan))

        return self

    def supertrend(self, length=10, multiplier=2, offset=0):

        st = self.dataframe.ta.supertrend(length=length, multiplier=multiplier, offset=offset)

        field_name = f"SUPERTd_{length}_{multiplier}.{offset}"

        self.dataframe['long_supertrend'] = np.where((st[field_name] > st[field_name].shift(1)), 1.0, 0.0)
        self.dataframe['short_supertrend'] = np.where((st[field_name] < st[field_name].shift(1)), 1.0, 0.0)

        return self

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

        return (self.dataframe['macdcross'].iloc[-1],
                self.dataframe['macdmin'].iloc[-1],
                self.dataframe['macdmax'].iloc[-1])

    def ema(self, period, inbound_column='Close', outbound_column='ema'):
        self.dataframe[outbound_column] = finta.EMA(self.dataframe, period=period, column=inbound_column)

        return self

    def debug(self, debug=True):

        if True:
            print(self.dataframe.to_string())

        return self

    def min(self, inbound_column, outbound_column):
        self.dataframe[outbound_column] = (np.where(
            (self.dataframe[inbound_column].shift(2) > self.dataframe[inbound_column].shift(1))
            &
            (self.dataframe[inbound_column].shift(0) > self.dataframe[inbound_column].shift(1)),
            1.0, 0.0))

        return self

    def max(self, inbound_column, outbound_column):
        self.dataframe[outbound_column] = (np.where(
            (self.dataframe[inbound_column].shift(2) < self.dataframe[inbound_column].shift(1))
            &
            (self.dataframe[inbound_column].shift(0) < self.dataframe[inbound_column].shift(1)),
            1.0, 0.0))

        return self

    def cross(self, first_column, second_column, outbound_column):
        self.dataframe[outbound_column] = 0.0
        self.dataframe[outbound_column] = np.where(self.dataframe[first_column] < self.dataframe[second_column], 1.0,
                                                   0.0)
        self.dataframe[outbound_column] = self.dataframe[outbound_column].diff()

        return self

    def diff(self, inbound_column, outbound_column):
        self.dataframe[outbound_column] = -self.dataframe[inbound_column].diff(-1).shift() / self.dataframe[
            inbound_column] * 100

        return self

    def crossprice(self, inbound_column, outbound_column):
        return self.cross(inbound_column, 'Close', outbound_column)

    def drop(self, columns=[]):
        self.dataframe.drop(columns=columns, axis=1, inplace=True)

        return self
