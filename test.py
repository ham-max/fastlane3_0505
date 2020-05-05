from datetime import *
import pandas as pd
import numpy as np


time = "125315"
nowtime = "20200504124800"
nowtime = pd.to_datetime(nowtime)

def is_same_candle(date, curdate, cur_time_val):
    curdate = datetime.today().strftime("%Y%m%d") + curdate
    curdate = pd.to_datetime(curdate)
    timedelta = (date - curdate).seconds
    timedelta = timedelta / 60
    if timedelta > cur_time_val:
        return False
    elif timedelta < cur_time_val:
        return True
    else:
        pass

print(is_same_candle(nowtime, time, 3))

new_candle = nowtime + timedelta(minutes=3)
print(new_candle)

array = [['125315', 252.6, 251.55, 252.95, 249.6], ['125315', 252.6, 251.55, 252.95, 249.6]]
underlying_3_array = np.array(array)
underlying_3_df = pd.DataFrame(underlying_3_array)

print(underlying_3_df)

underlying_3_df[3].iloc[-1] = 999

print(underlying_3_df)


def cal_cross(macd, macds):
    if macd > macds:
        return "call"
    elif macd < macds:
        return "put"
    elif macd == macds:
        return "par"


a = 2.7
b = 3.6

m3 = cal_cross(a, b)

print(m3)