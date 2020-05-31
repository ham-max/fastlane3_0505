# elif sRealType == "선물시세":
#     data = []
#
#     time = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["체결시간"])         #HHMMSS
#     time = datetime.today().strftime("%Y%m%d") + time
#     time = pd.to_datetime(time)
#     close_price = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["현재가"])          #+ 또는 - ; 음봉은 -로 나옴
#     close_price = abs(float(close_price))
#     open_price = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["시가"])
#     open_price = abs(float(open_price))
#     high_price = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["고가"])
#     high_price = abs(float(high_price))
#     low_price = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["저가"])
#     low_price = abs(float(low_price))
#
#     candle_3_time = self.underlying_3_df["date"].iloc[-1]
#     candle_3_time = pd.to_datetime(candle_3_time)
#     new_candle_3_time = candle_3_time + timedelta(minutes=3)
#
#     # TR 데이터가 2분에 한 번 업데이트 된다는 전제 하
#     # underlying 분봉 df에 붙여넣기 작업
#     if self.is_same_candle(candle_3_time, time, 3) == True: # 실시간 시세가 마지막 업데이트 시간 대비 3분이 안 지난 경우
#         #종가 업데이트
#         self.underlying_3_df["close"].iloc[-1] = close_price
#         #고가, 저가 업데이트
#         if close_price > self.underlying_3_df["high"].iloc[-1]:
#             self.underlying_3_df["high"].iloc[-1] = close_price
#         elif close_price < self.underlying_3_df["low"].iloc[-1]:
#             self.underlying_3_df["low"].iloc[-1] = close_price
#
#     else:
#         #새로운 row 추가 (날짜명은 +3으로)
#         data.append(new_candle_3_time)
#         data.append(close_price)
#         data.append(open_price)
#         data.append(high_price)
#         data.append(low_price)
#
#         a = pd.DataFrame(data)
#         self.underlying_3_df.append(a)
#         self.underlying_3_df.reset_index(drop=True)
#
#     self.get_macd()
#     self.get_sto()
#
#     print(self.underlying_3_df)
#
#     macd = self.underlying_3_df["macd"].iloc[-1]
#     macds = self.underlying_3_df["macds"].iloc[-1]
#     slow_k = self.underlying_3_df["slow_k"].iloc[-1]
#     slow_d = self.underlying_3_df["slow_d"].iloc[-1]
#
#     m3 = self.cal_macd(macd, macds)
#     s3 = self.cal_sto(slow_k, slow_d)
#
#     print("m3 %s s3 %s" % (m3, s3))
# 실시간 차트:  [['125315', 252.6, 251.55, 252.95, 249.6], ['125315', 252.6, 251.55, 252.95, 249.6]]
# 분봉 차트 : ['20200504124800', 252.5, 252.8, 252.95, 252.45]


