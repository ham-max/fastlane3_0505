# from datetime import *
# import pandas as pd
# import numpy as np
#
#
# time = "125315"
# nowtime = "20200504124800"
# nowtime = pd.to_datetime(nowtime)
#
# def is_same_candle(date, curdate, cur_time_val):
#     curdate = datetime.today().strftime("%Y%m%d") + curdate
#     curdate = pd.to_datetime(curdate)
#     timedelta = (date - curdate).seconds
#     timedelta = timedelta / 60
#     if timedelta > cur_time_val:
#         return False
#     elif timedelta < cur_time_val:
#         return True
#     else:
#         pass
#
# print(is_same_candle(nowtime, time, 3))
#
# new_candle = nowtime + timedelta(minutes=3)
# print(new_candle)
#
# array = [['125315', 252.6, 251.55, 252.95, 249.6], ['125315', 252.6, 251.55, 252.95, 249.6]]
# underlying_3_array = np.array(array)
# underlying_3_df = pd.DataFrame(underlying_3_array)
#
# print(underlying_3_df)
#
# underlying_3_df[3].iloc[-1] = 999
#
# print(underlying_3_df)
#
#
# def cal_cross(macd, macds):
#     if macd > macds:
#         return "call"
#     elif macd < macds:
#         return "put"
#     elif macd == macds:
#         return "par"
#
#
# a = 2.7
# b = 3.6
#
# m3 = cal_cross(a, b)
#
# print(m3)

# import time
# import threading
#
# def thread_run():
#     print("====", time.ctime(), "====")
#     for i in range(1, 21):
#
#         print('Thread running - ', i)
#     threading.Timer(2.5, thread_run).start()
#
# thread_run()
from fbchat import Client
#
# class Main():
#     def __init__(self):
#         self.facebook()


#
# if __name__=='__main__':
#     Main()

# import telegram
#
# telgm_token = '1232236027:AAG9n41tHK8zHzgV_gh5QY5TKB2I-z4nnUY'
# bot = telegram.Bot(token = telgm_token)
# bot.sendMessage(chat_id =  '-355062800', text = ("똘봇 테스트 %s" % 25))
# #1240234286 나
# #685002826 아빠
# #1082823436 엄마
import operator
# stats = {'a':1000, 'b':3000, 'c': 100, 'd':3000}
# a = max(stats, key=stats.get)
# print(a)
from pprint import pprint as pp

dt = {'57EP55': {'종목명': '한국EP55KOSPI200콜', '권리구분': '콜', '현재가': 195, '행사가': 260.0, '거래량': 74211440, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EP56': {'종목명': '한국EP56KOSPI200콜', '권리구분': '콜', '현재가': 290, '행사가': 257.5, '거래량': 50112650, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EM15': {'종목명': '한국EM15KOSPI200콜', '권리구분': '콜', '현재가': 70, '행사가': 265.0, '거래량': 49773060, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EP54': {'종목명': '한국EP54KOSPI200콜', '권리구분': '콜', '현재가': 120, '행사가': 262.5, '거래량': 19555070, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EP57': {'종목명': '한국EP57KOSPI200콜', '권리구분': '콜', '현재가': 410, '행사가': 255.0, '거래량': 18012010, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EM14': {'종목명': '한국EM14KOSPI200콜', '권리구분': '콜', '현재가': 45, '행사가': 267.5, '거래량': 9510010, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EM10': {'종목명': '한국EM10KOSPI200콜', '권리구분': '콜', '현재가': 5, '행사가': 277.5, '거래량': 5794790, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'57EM13': {'종목명': '한국EM13KOSPI200콜', '권리구분': '콜', '현재가': 20, '행사가': 270.0, '거래량': 5374470, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'},
'55ED05': {'종목명': 'NHED05KOSPI200콜', '권리구분': '콜', '현재가': 35, '행사가': 287.5, '거래량': 5147530, '잔존일수': 37, '스크린번호': '200', '주문용스크린번호': '400'},
'57EM12': {'종목명': '한국EM12KOSPI200콜', '권리구분': '콜', '현재가': 15, '행사가': 272.5, '거래량': 3658060, '잔존일수': 9, '스크린번호': '200', '주문용스크린번호': '400'}}

data_call=[]
for code in list(dt.keys()):
    volume = dt[code]["거래량"]
    data_call.append(volume)
max_call_volume = max(data_call)
for key in dt:
    if dt[key]["거래량"] == max_call_volume:
        max_call_code = key
print(max_call_code)
print(data_call)

dict={}
dict.update({'123':{'code': max_call_code, 'volume': max_call_volume}})
dict.update({'456':{'code': 'a', 'price' : 4875}})
print(dict)

print(max(1,1,3,3))


# print(dt.keys())
# print(dt.values())
# print(dt.items())
import operator
# data = []
# for code in list(dt.keys()):
#     volume = dt[code]["거래량"]
#     data.append(volume)
# max_volume = max(data)
# for key in dt:
#     if dt[key]["거래량"] == max_volume:
#         max_code = key
# print(max_code)
#
import datetime as datetime

a= datetime.time(hour=15, minute=30)
b= datetime.datetime.now().time()

c= datetime.date.today()
print("오늘은 %s" % c)

print(a)
print(b)

if b<a:
    print("2시 이전")
if b>a:
    print("2시 이후")


import math

c = math.floor(1.39850928)
print(c)

d = 420/390 -1
d="{:.1%}".format(d)
print(d)

text = "hello %s %s" % ("world", "by haemin")
print(text)

x = round(36637-10, -1)
print(x)

import openpyxl

wb = openpyxl.Workbook()
dest_filename = 'text.xlsx'
sheet = wb.active
sheet2 = wb.create_sheet()
sheet2.title = '2번째 시트'
sheet2['C1'] = '1월7일'
wb.save(filename=dest_filename)

print(datetime.datetime.now().time())
time = "142459"
timetime = datetime.datetime.strptime(time, '%H%M%S')
today = datetime.datetime.today()
print(timetime)
timetime = timetime.replace(year=today.year, month=today.month, day=today.day)
print(timetime)
timetime = timetime + datetime.timedelta(minutes=30)
print(timetime)

if timetime + datetime.timedelta(minutes=30) < datetime.datetime.now():
    print("제시간입니다.")
else:
    print("아닙니다")

print(today)



meme_rate = (310 - 300) / 300 * 100
print(meme_rate)
order_t = "130200"
order_t = datetime.datetime.strptime(order_t, '%H%M%S')
today = datetime.datetime.today()
order_t = order_t.replace(year=today.year, month=today.month, day=today.day)
order_t_5 = order_t + datetime.timedelta(minutes=5)
print(order_t_5)
if meme_rate > 5 or meme_rate < -20 or order_t_5 <= datetime.datetime.now():
    print("주문해야합니다")
else:
    print("아직아닙니다")

alarm_text = "매도주문 접수 3분 경과, 미체결량 주문 취소합니다. 추격 매도 시작합니다.\n종목 %s \n주문량 %s \n미체결 %s -- %s" % ('57', '236', '473', '249')
print(alarm_text)

import copy

haemin = 256
haemin_prev = copy.copy(haemin)
haemin = 983
print("%s, %s" % (haemin_prev, haemin))