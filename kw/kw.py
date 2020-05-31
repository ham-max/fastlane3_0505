import os
import sys
import pprint
import math
import copy
import openpyxl
import threading
import pandas as pd
import numpy as np
import datetime as datetime
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from config.kiwoomtype import *
from PyQt5.QtTest import *
import telegram


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스입니다.")

        #event loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ##############################

        #스크린번호 모음
        self.screen_my_info = "100"
        self.screen_real_elw = "200" #실시간으로 ELW데이터 요청용
        self.screen_real_underlying = "300" #실시간으로 기초자산 데이터 요청용
        self.screen_underlying_3 = "303"
        self.screen_underlying_5 = "305"
        self.screen_underlying_10 = "310"
        self.screen_underlying_30 = "330"
        self.screen_underlying_60 = "360"
        self.screen_order_stock = "400" #주문 요청용
        self.screen_market_time = "500" #장 시작/종료 여부 확인 요청용
        self.screen_elw = "600"
        ##############################

        #변수 및 딕셔너리 모음
        self.account_num = None
        self.underlying_3_df = pd.DataFrame()
        self.underlying_5_df = pd.DataFrame()
        self.underlying_10_df = pd.DataFrame()
        self.underlying_30_df = pd.DataFrame()
        self.underlying_60_df = pd.DataFrame()
        self.underlying_code = "101Q6000"
        self.account_stock_dict = {}
        self.jango_stock_dict = {}
        self.outstanding_order_dict = {}
        self.sales_log_dict = {}
        self.underlying_assets_dict = {}
        self.elw_dict = {}
        self.elw_else_dict = {}
        self.realType = RealType() #kiwoomtype에서 RealType 클래스 불러옴
        self.max_put_code = None
        self.max_call_code = None
        self.slow30 = None
        self.allcallbuymacd = None
        self.allputbuymacd = None
        self.buytype = None
        self.mesu_clock = datetime.time(hour=14, minute=45)
        self.time319 = datetime.time(hour=15, minute=19)
        self.telegram_id = '1240234286'
        #1240234286 나
        #685002826 아빠
        #1082823436 엄마
        #-355062800 3명 채팅방
        ##############################

        #종목분석용
        self.underlying_3 = []
        self.underlying_5 = []
        self.underlying_10 = []
        self.underlying_30 = []
        self.underlying_60 = []
        self.underlying_real = []
        self.calculator_data = []
        self.elw_call_list = []
        ##############################

        #계좌관련변수
        self.pocket_money = 0
        ##############################

        #코드 실행
        self.get_ocx_instance()
        f = open("file/elw", "w", encoding="utf8")
        f.close()
        self.event_slots() #받은 Slots 가져오기
        self.event_slots_real() #받은 실시간 Slots 가져오기
        self.signal_login_commConnect() #로그인 Event 요청
        self.get_account_info() #계좌번호 요청 & 반환
        self.signal_detail_account_info() #예수금 Event 요청
        self.signal_mystock_info() #잔고내역 Event 요청
        self.signal_outstanding_order() #미체결내역 Event 요청
        self.signal_market_time() #장시작여부 Event요청
        self.get_underlying_info() #선물지수 Info 가져오기
        self.get_elw_list() #ELW Info 가져오기
        self.find_max()
        self.read_underlying() #저장된 기초자산 불러오기
        self.screen_number_setting() #불러온 모든 종목에 대해 Screen number 지정해주기 (기초자산, ELW, 종목 등)
        self.get_realtime_data()
        self.telegram()
        self.thread_run()
        ##############################

    #반복 실행
    def thread_run(self):
        for i in range(1, 50000):
            print("===", datetime.datetime.now(), "===")
            self.db_3()
            self.db_5()
            self.db_10()
            self.db_30()
            self.db_60()
            self.print_result()
            self.buy_order()
            self.sell_order()
        threading.Timer(80, self.thread_run).start()

    #제어
    def get_ocx_instance(self):
        #Open API 제어 시작
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    #Events
    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")
        #Event - 로그인 요청 보내는 부분
        self.login_event_loop =QEventLoop()
        self.login_event_loop.exec_()

    def get_account_info(self):
        #Event - 계좌번호 요청 보내는 부분; 별도 Slot 없이 변수로 받음
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(';')[0]
        print("내 계좌번호 %s" % self.account_num) #이전-8135128711 #변경후-8137431711

    def signal_detail_account_info(self):
        print("내 계좌 현황")
        #Event - 예수금 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", "0",
                         self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def signal_mystock_info(self, sPrevNext="0"):
        print("계좌평가 잔고내역 - 페이지 %s" % sPrevNext)
        #Event - 계좌평가잔고 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", "0",
                         self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def signal_outstanding_order(self):
        print("미체결 요청")
        #Event - 미체결 요청 처리 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def signal_market_time(self):
        #Event - 장 시작인지 아닌지 알기 위한 요청 보내는 부분 (화면번호, 종목코드리스트, 실시간FID리스트, 실시간등록타입; 0또는 1)
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_market_time, "",
                         self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

    def get_realtime_data(self):
        for code in self.underlying_assets_dict.keys():  #실시간을 등록해줌
            screen_num = self.underlying_assets_dict[code]["스크린번호"]
            fids = self.realType.REALTYPE["주식체결"]["체결시간"]
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids,
                             "1")  #실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
            print("실시간 등록 코드: %s, 스크린번호: %s, fid 번호: %s" % (code, screen_num, fids))
        for code in self.elw_dict.keys():
            screen_num = self.elw_dict[code]["스크린번호"]
            fids = self.realType.REALTYPE["주식체결"]["체결시간"]
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids,
                             "1")  #실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.

    def get_elw_list(self, sPrevNext="0"):
        #Event - ELW KOSPI200 리스트 조건검색 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "기초자산코드", "201")
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "5")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "ELW조건검색요청", "opt30005", sPrevNext, self.screen_elw)

        # self.calculator_event_loop.exec_()

    def get_underlying_info(self):
        #Event - ELW KOSPI200 풋 리스트 조건검색 요청 보내는 부분
        print("선옵현재가정보요청")
        print("추종 KOSPI200 선물 종목: 101Q6000")
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선옵현재가정보요청", "opt50001", "0",
                         self.screen_real_underlying)

    def db_3(self, range=None, sPrevNext="0"):
        #Event - 데이터 요청용
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시간단위", "3")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선물옵션분차트요청", "OPT50029", sPrevNext,
                         self.screen_underlying_3)

        self.calculator_event_loop.exec_()

    def db_5(self, range=None, sPrevNext="0"):
        #Event - 데이터 요청용
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시간단위", "5")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선물옵션분차트요청", "OPT50029", sPrevNext,
                         self.screen_underlying_5)

        self.calculator_event_loop.exec_()

    def db_10(self, range=None, sPrevNext="0"):
        #Event - 데이터 요청용
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시간단위", "10")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선물옵션분차트요청", "OPT50029", sPrevNext,
                         self.screen_underlying_10)

        self.calculator_event_loop.exec_()

    def db_30(self, range=None, sPrevNext="0"):
        #Event - 데이터 요청용
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시간단위", "30")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선물옵션분차트요청", "OPT50029", sPrevNext,
                         self.screen_underlying_30)

        self.calculator_event_loop.exec_()

    def db_60(self, range=None, sPrevNext="0"):
        #Event - 데이터 요청용
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.underlying_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시간단위", "60")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선물옵션분차트요청", "OPT50029", sPrevNext,
                         self.screen_underlying_60)

        self.calculator_event_loop.exec_()

    #Slots
    def event_slots(self):
        #Slots - 받은 Slot 데이터 저장하는 부분
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
        self.OnReceiveMsg.connect(self.msg_slot)

    def event_slots_real(self):
        #Slots - 받은 Real time Slot 데이터 저장하는 부분
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejandata_slot)

    def login_slot(self, errcode):
        #Slot - 로그인 요청 받는 부분
        '''
        OnEventConnect
        :param errcode: 로그인 상태를 전달하는데 자세한 내용은 아래 상세내용 참고
        :return:
        '''
        print(errors(errcode))
        self.login_event_loop.exit()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        #Slot - TR 데이터 받는 부분
        '''
        OnReceiveTrData
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청id tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, String, String)", sTrCode, sRQName, 0, "예수금")
            deposit = int(deposit)
            orderable = self.dynamicCall("GetCommData(String, String, String, String)", sTrCode, sRQName, 0, "주문가능금액")
            orderable = int(orderable)
            print("예수금 %s원, 주문가능금액 %s원" % (format(int(deposit),","),format(int(orderable),",")))

            if orderable > 10000000:
                self.pocket_money = 10000000
            else:
                self.pocket_money = orderable

            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            purchased = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            print("총매입금액 %s" % format(int(purchased),","))

            valuation = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총평가금액")
            print("총평가금액 %s" % format(int(valuation), ","))

            profit_percent = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0,
                                              "총수익률(%)")
            print("총수익률(%%) %s" % float(profit_percent))

            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                        "종목번호")  #A:장내주식 J:ELW Q:ETN
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                possessed_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                                      i, "보유수량")
                purchased_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "매입가")
                earn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                             "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")
                total_amount = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                     "매매가능수량")

                code = code.strip()[1:]
                code_nm = code_nm.strip()
                possessed_quantity = int(possessed_quantity.strip())
                purchased_price = int(purchased_price.strip())
                earn_rate = float(earn_rate.strip())
                current_price = int(current_price.strip())
                total_amount = int(total_amount.strip())
                possible_quantity = int(possible_quantity.strip())

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                asd = self.account_stock_dict[code]

                asd.update({"종목명": code_nm})
                asd.update({"보유수량": possessed_quantity})
                asd.update({"매입가": purchased_price})
                asd.update({"수익률(%)": earn_rate})
                asd.update({"현재가": current_price})
                asd.update({"매입금액": total_amount})
                asd.update({"매매가능수량": possible_quantity})

                cnt += 1

                if code in self.jango_stock_dict:
                    pass
                else:
                    self.jango_stock_dict.update({code:{}})

                jd = self.jango_stock_dict[code]

                jd.update({"현재가": current_price})
                jd.update({"종목코드": code})
                jd.update({"종목명": code_nm})
                jd.update({"보유수량": possessed_quantity})
                jd.update({"주문가능수량": possible_quantity})
                jd.update({"매입단가": purchased_price})
                jd.update({"총매입가": total_amount})


            print("계좌 보유 종목 %s" % self.account_stock_dict)
            print("계좌 보유 종목 개수 %s" % cnt)

            if sPrevNext == "2":
                self.signal_mystock_info(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "주문상태")  #접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문구분")  #매도, 매수, 정정, 취소
                outstanding_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                                        i, "미체결수량")
                concluded_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                                      i, "체결수량")
                order_time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                                      i, "시간")

                code = code.strip()
                code_nm = code_nm.strip()
                order_nm = int(order_nm.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                outstanding_quantity = int(outstanding_quantity.strip())
                concluded_quantity = concluded_quantity.strip()
                order_time = order_time.strip()
                if concluded_quantity == "":
                    concluded_quantity = 0
                elif type(concluded_quantity) == int:
                    concluded_quantity = int(concluded_quantity)

                if order_nm in self.outstanding_order_dict.keys():
                    pass
                else:
                    self.outstanding_order_dict[order_nm] = {}

                ood = self.outstanding_order_dict[order_nm]

                ood.update({"종목코드": code})
                ood.update({"종목명": code_nm})
                ood.update({"주문번호": order_nm})
                ood.update({"주문상태": order_status})
                ood.update({"주문수량": order_quantity})
                ood.update({"주문가격": order_price})
                ood.update({"주문구분": order_gubun})
                ood.update({"미체결수량": outstanding_quantity})
                ood.update({"체결량": concluded_quantity})
                ood.update({"주문/체결시간": order_time})

                print("미체결 주문 : %s" % self.outstanding_order_dict[order_nm])

                cnt += 1

            self.detail_account_info_event_loop.exit()

        elif sRQName == "ELW조건검색요청":
            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            cnt = 0

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                position = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "권리구분")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "현재가")
                strike_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "행사가격")
                trade_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "거래량")
                strike_date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "만기일")
                left_days = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "잔존일수")

                code = code.strip()
                code_nm = code_nm.strip()
                position = position.strip()
                current_price = abs(int(current_price.strip()))
                strike_price = float(strike_price.strip())
                trade_volume = int(trade_volume.strip())
                strike_date = strike_date.strip()
                left_days = int(left_days.strip())

                f = open("file/elw", "a", encoding="utf8")
                f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                code, code_nm, position, current_price, strike_price, trade_volume, strike_date, left_days))
                f.close()

                cnt += 1

            f = open("file/elw", "r", encoding="utf8")
            lines = f.readlines()
            print("총 %s개 라인" % len(lines))
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    code = ls[0]
                    code_nm = ls[1]
                    position = ls[2]
                    current_price = int(ls[3])
                    strike_price = float(ls[4])
                    trade_volume = int(ls[5])
                    left_days = int(ls[7].split("\n")[0])

                    if left_days >= 2:
                        if code in self.elw_dict.keys():
                            self.elw_dict.update({code: {"종목명": code_nm, "권리구분": position, "현재가": current_price,
                                                         "행사가": strike_price, "거래량": trade_volume, "잔존일수": left_days}})
                        if code not in self.elw_dict.keys():
                            self.elw_dict.update({code:{}})
                            self.elw_dict.update({code: {"종목명": code_nm, "권리구분": position, "현재가": current_price,
                                                         "행사가": strike_price, "거래량": trade_volume, "잔존일수": left_days}})

                    else:
                        if code in self.elw_dict.keys():
                            del self.elw_dict[code]
                        else:
                            pass

            print("선택된 ELW 종목 %s개" % len(self.elw_dict))
            self.screen_number_setting()

            if sPrevNext == "2":
                self.get_elw_list(sPrevNext=sPrevNext)
            else:
                self.calculator_event_loop.exit()

        elif sRQName == "선옵현재가정보요청":

            f = open("file/underlying_assets", "w", encoding="utf8")
            f.close()

            code = self.underlying_code
            code_nm = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "종목명")
            current_price = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "현재가")
            left_days = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "잔존일수")

            code = code.strip()
            code_nm = code_nm.strip()
            current_price = abs(float(current_price.strip()))
            left_days = int(left_days.strip())

            f = open("file/underlying_assets", "a", encoding="utf8")
            f.write("%s\t%s\t%s\t%s\n" % (code, code_nm, current_price, left_days))
            f.close()

        elif sRQName == "선물옵션분차트요청":
            if sScrNo == self.screen_underlying_3:
                rows =self.dynamicCall('GetRepeatCnT(QString, QString)', sTrCode, sRQName)
                self.underlying_3 = []

                for i in range(rows):
                    data =[]
                    date =self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    close_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "현재가")
                    open_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "시가")
                    high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "고가")
                    low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "저가")
                    data.append(date.strip())
                    data.append(abs(float(close_price.strip())))
                    data.append(abs(float(open_price.strip())))
                    data.append(abs(float(high_price.strip())))
                    data.append(abs(float(low_price.strip())))
                    self.underlying_3.append(data.copy())

                self.underlying_3 = np.array(self.underlying_3)
                self.underlying_3_df = pd.DataFrame(self.underlying_3[:200])
                self.underlying_3_df.columns = ["date", "close", "open", "high", "low"]
                self.underlying_3_df['date'] = pd.to_datetime(self.underlying_3_df['date'])
                self.underlying_3_df = self.underlying_3_df.sort_values(by=['date'], ascending=True)
                self.underlying_3_df = self.underlying_3_df.reset_index(drop=True)

                self.underlying_3_df = self.get_macd(self.underlying_3_df)
                self.underlying_3_df = self.get_sto(self.underlying_3_df)
                self.underlying_3_df = self.underlying_3_df.reset_index(drop=True)

                macd = self.underlying_3_df["macd"].iloc[-1]
                macds = self.underlying_3_df["macds"].iloc[-1]
                slow_k = self.underlying_3_df["slow_k"].iloc[-1]
                slow_d = self.underlying_3_df["slow_d"].iloc[-1]

                self.m3 = self.cal_macd(macd, macds)
                self.s3 = self.cal_sto(slow_k, slow_d)

                self.calculator_event_loop.exit()

            elif sScrNo == self.screen_underlying_5:
                rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
                self.underlying_5 = []

                for i in range(rows):
                    data = []
                    date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    close_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "현재가")
                    open_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "시가")
                    high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "고가")
                    low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "저가")
                    data.append(date.strip())
                    data.append(abs(float(close_price.strip())))
                    data.append(abs(float(open_price.strip())))
                    data.append(abs(float(high_price.strip())))
                    data.append(abs(float(low_price.strip())))
                    self.underlying_5.append(data.copy())

                self.underlying_5 = np.array(self.underlying_5)
                self.underlying_5_df = pd.DataFrame(self.underlying_5[:200])
                self.underlying_5_df.columns = ["date", "close", "open", "high", "low"]
                self.underlying_5_df['date'] = pd.to_datetime(self.underlying_5_df['date'])
                self.underlying_5_df = self.underlying_5_df.sort_values(by=['date'], ascending=True)
                self.underlying_5_df = self.underlying_5_df.reset_index(drop=True)

                self.underlying_5_df = self.get_macd(self.underlying_5_df)
                self.underlying_5_df = self.get_sto(self.underlying_5_df)
                self.underlying_5_df = self.underlying_5_df.reset_index(drop=True)

                macd = self.underlying_5_df["macd"].iloc[-1]
                macds = self.underlying_5_df["macds"].iloc[-1]
                slow_k = self.underlying_5_df["slow_k"].iloc[-1]
                slow_d = self.underlying_5_df["slow_d"].iloc[-1]

                self.m5 = self.cal_macd(macd, macds)
                self.s5 = self.cal_sto(slow_k, slow_d)
                print(self.underlying_5_df["close"].iloc[-1])

                self.calculator_event_loop.exit()

            elif sScrNo == self.screen_underlying_10:
                rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
                self.underlying_10 = []

                for i in range(rows):
                    data = []
                    date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    close_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "현재가")
                    open_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "시가")
                    high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "고가")
                    low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "저가")
                    data.append(date.strip())
                    data.append(abs(float(close_price.strip())))
                    data.append(abs(float(open_price.strip())))
                    data.append(abs(float(high_price.strip())))
                    data.append(abs(float(low_price.strip())))
                    self.underlying_10.append(data.copy())

                self.underlying_10 = np.array(self.underlying_10)
                self.underlying_10_df = pd.DataFrame(self.underlying_10[:200])
                self.underlying_10_df.columns = ["date", "close", "open", "high", "low"]
                self.underlying_10_df['date'] = pd.to_datetime(self.underlying_10_df['date'])
                self.underlying_10_df = self.underlying_10_df.sort_values(by=['date'], ascending=True)
                self.underlying_10_df = self.underlying_10_df.reset_index(drop=True)

                self.underlying_10_df = self.get_macd(self.underlying_10_df)
                self.underlying_10_df = self.get_sto(self.underlying_10_df)
                self.underlying_10_df = self.underlying_10_df.reset_index(drop=True)

                macd = self.underlying_10_df["macd"].iloc[-1]
                macds = self.underlying_10_df["macds"].iloc[-1]
                slow_k = self.underlying_10_df["slow_k"].iloc[-1]
                slow_d = self.underlying_10_df["slow_d"].iloc[-1]

                self.m10 = self.cal_macd(macd, macds)
                self.s10 = self.cal_sto(slow_k, slow_d)

                self.calculator_event_loop.exit()

            elif sScrNo == self.screen_underlying_30:
                rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
                self.underlying_30 = []

                for i in range(rows):
                    data = []
                    date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    close_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "현재가")
                    open_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "시가")
                    high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "고가")
                    low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "저가")
                    data.append(date.strip())
                    data.append(abs(float(close_price.strip())))
                    data.append(abs(float(open_price.strip())))
                    data.append(abs(float(high_price.strip())))
                    data.append(abs(float(low_price.strip())))
                    self.underlying_30.append(data.copy())

                self.underlying_30 = np.array(self.underlying_30)
                self.underlying_30_df = pd.DataFrame(self.underlying_30[:200])
                self.underlying_30_df.columns = ["date", "close", "open", "high", "low"]
                self.underlying_30_df['date'] = pd.to_datetime(self.underlying_30_df['date'])
                self.underlying_30_df = self.underlying_30_df.sort_values(by=['date'], ascending=True)
                self.underlying_30_df = self.underlying_30_df.reset_index(drop=True)

                self.underlying_30_df = self.get_macd(self.underlying_30_df)
                self.underlying_30_df = self.get_sto(self.underlying_30_df)
                self.underlying_30_df = self.underlying_30_df.reset_index(drop=True)

                macd = self.underlying_30_df["macd"].iloc[-1]
                macds = self.underlying_30_df["macds"].iloc[-1]
                slow_k = self.underlying_30_df["slow_k"].iloc[-1]
                slow_d = self.underlying_30_df["slow_d"].iloc[-1]

                self.m30 = self.cal_macd(macd, macds)
                self.s30 = self.cal_sto(slow_k, slow_d)

                self.calculator_event_loop.exit()

            elif sScrNo == self.screen_underlying_60:
                rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
                self.underlying_60 = []

                for i in range(rows):
                    data = []
                    date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    close_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                   "현재가")
                    open_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "시가")
                    high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "고가")
                    low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                 "저가")
                    data.append(date.strip())
                    data.append(abs(float(close_price.strip())))
                    data.append(abs(float(open_price.strip())))
                    data.append(abs(float(high_price.strip())))
                    data.append(abs(float(low_price.strip())))
                    self.underlying_60.append(data.copy())

                self.underlying_60 = np.array(self.underlying_60)
                self.underlying_60_df = pd.DataFrame(self.underlying_60[:200])
                self.underlying_60_df.columns = ["date", "close", "open", "high", "low"]
                self.underlying_60_df['date'] = pd.to_datetime(self.underlying_60_df['date'])
                self.underlying_60_df = self.underlying_60_df.sort_values(by=['date'], ascending=True)
                self.underlying_60_df = self.underlying_60_df.reset_index(drop=True)

                self.underlying_60_df = self.get_macd(self.underlying_60_df)
                self.underlying_60_df = self.get_sto(self.underlying_60_df)
                self.underlying_60_df = self.underlying_60_df.reset_index(drop=True)

                macd = self.underlying_60_df["macd"].iloc[-1]
                macds = self.underlying_60_df["macds"].iloc[-1]
                slow_k = self.underlying_60_df["slow_k"].iloc[-1]
                slow_d = self.underlying_60_df["slow_d"].iloc[-1]

                self.m60 = self.cal_macd(macd, macds)
                self.s60 = self.cal_sto(slow_k, slow_d)

                self.calculator_event_loop.exit()

    def print_result(self):
        self.signal_list = [self.m3, self.s3, self.m5, self.s5, self.m10, self.s10, self.m30, self.s30, self.m60,
                            self.s60]
        self.semi_signal_list = [self.m3, self.s3, self.m30, self.s30, self.m60, self.s60]
        self.call_sign_cnt = self.signal_list.count("call")
        self.put_sign_cnt = self.signal_list.count("put")
        self.par_sign_cnt = self.signal_list.count("par")
        self.semi_call_sign_cnt = self.semi_signal_list.count("call")
        self.semi_put_sign_cnt = self.semi_signal_list.count("put")
        self.slow30_prev = copy.copy(self.slow30)
        self.slow30 = self.underlying_30_df["slow_k"].iloc[-1]
        print("60분 신호 %s %s 30분 신호 %s %s \n10분 신호 %s %s 5분 신호 %s %s 3분 신호 %s %s" % (
        self.m60, self.s60, self.m30, self.s30, self.m10, self.s10, self.m5, self.s5, self.m3, self.s3))
        print(self.jango_stock_dict)
        if self.call_sign_cnt == 10:
            self.sign = "Allcall"
            print("올콜 %s개" % self.call_sign_cnt)
            self.bot.sendMessage(chat_id=self.telegram_id,
                                 text=("올콜\n30분 S-Sto %s" % self.slow30))
        elif self.put_sign_cnt == 10:
            self.sign = "Allput"
            print("올풋 %s개" % self.put_sign_cnt)
            self.bot.sendMessage(chat_id=self.telegram_id,
                                 text=("올풋\n30분 S-Sto %s" % self.slow30))
        elif self.call_sign_cnt == 9 and self.par_sign_cnt == 1:
            self.sign = "Allcall"
            print("올콜 파 1개 \n30분 S-Sto %s\n60분 신호 %s %s 30분 신호 %s %s \n10분 신호 %s %s 5분 신호 %s %s 3분 신호 %s %s" % (
            self.underlying_30_df["slow_k"].iloc[-1], self.m60, self.s60, self.m30, self.s30, self.m10, self.s10,
            self.m5, self.s5, self.m3, self.s3))
            self.bot.sendMessage(chat_id=self.telegram_id, text=(
                        "올콜 파 1개 \n30분 S-Sto %s\n60분 %s %s 30분 %s %s \n10분 %s %s 5분 %s %s 3분 %s %s" % (
                self.slow30, self.m60, self.s60, self.m30, self.s30, self.m10, self.s10,
                self.m5, self.s5, self.m3, self.s3)))
        elif self.put_sign_cnt == 9 and self.par_sign_cnt == 1:
            self.sign = "Allput"
            print("올풋 파 1개 \n30분 S-Sto %s\n60분 신호 %s %s 30분 신호 %s %s \n10분 신호 %s %s 5분 신호 %s %s 3분 신호 %s %s" % (
            self.slow30, self.m60, self.s60, self.m30, self.s30, self.m10, self.s10,
            self.m5, self.s5, self.m3, self.s3))
            self.bot.sendMessage(chat_id=self.telegram_id, text=(
                        "올풋 파 1개 \n30분 S-Sto %s\n60분 %s %s 30분 %s %s \n10분 %s %s 5분 %s %s 3분 %s %s" % (
                self.slow30, self.m60, self.s60, self.m30, self.s30, self.m10, self.s10,
                self.m5, self.s5, self.m3, self.s3)))
        elif self.semi_call_sign_cnt == 6:
            self.sign = "Semicall"
            print("반콜")
            # self.bot.sendMessage(chat_id=self.telegram_id,
            #                      text=("반콜\n30분 S-Sto %s" % self.slow30))
        elif self.semi_put_sign_cnt == 6:
            self.sign = "Semiput"
            print("반풋")
            # self.bot.sendMessage(chat_id=self.telegram_id,
            #                      text=("반풋\n30분 S-Sto %s" % self.slow30))
        else:
            self.sign = "None"
            print("매수신호 없음; Call %s개, Put %s개" % (self.call_sign_cnt, self.put_sign_cnt))

    def buy_order(self):
        # 매수 조건:
        # 1) 올콜 2) 계좌잔고 10만원 이상 3) 2시 이전
        self.signal_detail_account_info()
        if self.sign == "Allcall" and self.pocket_money > 100000 and datetime.datetime.now().time() < self.mesu_clock:
            buy_quantity = self.pocket_money / self.elw_dict[self.max_put_code]["현재가"] - 10
            buy_quantity = round(buy_quantity, -1)
            buy_quantity = int(buy_quantity)
            order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                             ["신규매수", self.elw_dict[self.max_call_code]["주문용스크린번호"],
                                              self.account_num, 1, self.max_call_code, buy_quantity,
                                              self.elw_dict[self.max_call_code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
            #SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
            #nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
            #sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
            if order_success == 0:
                print("매수주문 전달 성공")
                calmesu = lambda x, y: "풋_진(0-4)" if x == "Allput" and y<5 else "풋_선(5-20)" if x == "Allput" and y>=5 and y <=20 else \
                    "풋_미(21-100))" if x == "Allput" and y >20 else "콜_진(96-100)" if x == "Allcall" and y>95 else "콜_선(80-95)" if x == "Allcall" and y <=95 and y >= 80 else \
                    "콜_미(0-79)" if x == "Allcall" and y <80 else "기타매수"
                self.mesucode = calmesu(self.sign, self.slow30)
                self.mesusign = self.sign
                self.mesuslow30 = self.slow30
                alarm_text = "%s 매수접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % self.mesucode
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

            else:
                print("매수주문 전달 실패")

        #매수 조건:
        #1) 올풋 2) 계좌잔고 10만원 이상 3) 2시 이전
        if self.sign == "Allput" and self.pocket_money > 100000 and datetime.datetime.now().time() < self.mesu_clock:
            buy_quantity = self.pocket_money / self.elw_dict[self.max_put_code]["현재가"] - 10
            buy_quantity = round(buy_quantity, -1)
            buy_quantity = int(buy_quantity)
            alarm_text = "%s 매수접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % "올풋"
            order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                             ["신규매수", self.elw_dict[self.max_put_code]["주문용스크린번호"],
                                              self.account_num, 1, self.max_put_code, buy_quantity,
                                              self.elw_dict[self.max_put_code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
            #SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
            #nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
            #sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
            if order_success == 0:
                print("매수주문 전달 성공")
                calmesu = lambda x, y: "풋_진(0-4)" if x == "Allput" and y<5 else "풋_선(5-20)" if x == "Allput" and y>=5 and y <=20 else \
                    "풋_미(21-100))" if x == "Allput" and y >20 else "콜_진(96-100)" if x == "Allcall" and y>95 else "콜_선(80-95)" if x == "Allcall" and y <=95 and y >= 80 else \
                    "콜_미(0-79)" if x == "Allcall" and y <80 else "기타매수"
                self.mesucode = calmesu(self.sign, self.slow30)
                self.mesusign = self.sign
                self.mesuslow30 = self.slow30
                alarm_text = "%s 매수접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % self.mesucode
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
            else:
                print("매수주문 전달 실패")

        for order_nm in self.outstanding_order_dict.keys():
            ood = self.outstanding_order_dict[order_nm]
            buy_t = ood["주문/체결시간"]
            order_q = ood["주문수량"]
            outst_q = ood["미체결수량"]
            code = ood["종목코드"]
            order_p = ood["주문가격"]
            order_gubun = ood["주문구분"]
            buy_t = datetime.datetime.strptime(buy_t, '%H%M%S')
            today = datetime.datetime.today()
            buy_t = buy_t.replace(year=today.year, month=today.month, day=today.day)
            buy_t_1 = buy_t + datetime.timedelta(minutes=1)

            if order_gubun == "매수" and buy_t_1 <= datetime.datetime.now() and outst_q > 0:
                order_success = self.dynamicCall(
                    "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                    ["매수취소", self.elw_dict[code]["주문용스크린번호"],
                     self.account_num, 3, code, outst_q,
                     order_p, self.realType.SENDTYPE["거래구분"]["지정가"], order_nm])
                # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                outst_portion = outst_q / order_q
                outst_portion = "{:.1%}".format(outst_portion)
                alarm_text = "매수주문 접수 1분 경과, 미체결량 주문 취소합니다. \n%s \n주문량 %s \n미체결 %s (%s)" % (code, order_q, outst_q, outst_portion)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                if order_success == 0:
                    print("매수취소주문 전달 성공")
                else:
                    print("매수취소주문 전달 실패")

            if order_gubun == "매도" and buy_t_1 <= datetime.datetime.now() and outst_q > 0:
                order_success = self.dynamicCall(
                    "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                    ["매도취소", self.elw_dict[code]["주문용스크린번호"],
                     self.account_num, 3, code, outst_q,
                     order_p, self.realType.SENDTYPE["거래구분"]["지정가"], order_nm])
                # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                outst_portion = outst_q / order_q
                outst_portion = "{:.1%}".format(outst_portion)
                alarm_text = "매도주문 접수 1분 경과, 미체결량 주문 취소합니다. 추격 매도 시작합니다. \n종목 %s \n주문량 %s \n미체결 %s (%s)\n현재단가 %s원(기존미체결 %s원)" \
                             "\n접수 완료 시 완료 메세지가 뜹니다." % (code, order_q, outst_q, outst_portion,self.elw_dict[code]["현재가"], order_p)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                if order_success == 0:
                    print("매도취소주문 전달 성공")
                else:
                    print("매도취소주문 전달 실패")

                if code not in self.jango_stock_dict.keys():
                    pass
                if code in self.jango_stock_dict.keys():
                    jsd = self.jango_stock_dict[code]
                    sell_p = self.elw_dict[code]["현재가"]
                    left_p = jsd["주문가능수량"]
                    buy_p = jsd["매입단가"]

                    if outst_q <= left_p:
                        outst_q = outst_q
                    if outst_q > left_p:
                        outst_q = left_p

                    order_success = self.dynamicCall(
                        "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                        ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                         self.account_num, 2, code, outst_q,
                         sell_p, self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                    # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                    # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                    # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))

                    if order_success == 0:
                        print("매도주문 전달 성공")
                    else:
                        print("매도주문 전달 실패")

    def sell_order(self):
        for order_nm in self.sales_log_dict.keys():
            sld = self.sales_log_dict[order_nm]
            date = sld["일자"]
            code = sld["종목코드"]  # 종목코드
            order_q = sld["주문수량"]  # 주문수량
            outst_q = sld["미체결수량"]
            buy_t = sld["주문/체결시간"]  # 매수체결시간
            buy_p = sld["체결가"]  # 체결가
            order_c = sld["매수코드"]  # 매수 코드, 풋_선(5-20), 풋_미(21-100))

            if code not in self.jango_stock_dict.keys():
                pass
            if code in self.jango_stock_dict.keys():
                jsd = self.jango_stock_dict[code]
                ed = self.elw_dict[code]
                if jsd["주문가능수량"] == 0:
                    pass
                else:
                    meme_rate = (ed["현재가"] - buy_p) / buy_p * 100

                    if order_c == "풋_진(0-4)" or order_c == "콜_진(96-100)":
                        if meme_rate > 15 or meme_rate < -20 or datetime.datetime.now().time() >= self.time319:
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            if meme_rate > 15:
                                alarm_text = "%s 수익률 %s 익절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if meme_rate < -20:
                                alarm_text = "%s 수익률 %s 손절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if datetime.datetime.now().time() >= self.time319:
                                alarm_text = "%s 현재 시각 3시 19분입니다. 매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % order_c
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                        if (order_c == "콜_진(96-100)" and self.slow30 < 95) or (order_c == "풋_진(0-4)" and self.slow30 > 5):
                            sell_quantity = (order_q - outst_q) * 0.5 - 10
                            sell_quantity = round(sell_quantity, -1)
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"] * 0.5 - 10
                                sell_quantity = round(sell_quantity, -1)
                                sell_quantity = int(sell_quantity)
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            alarm_text = "%s S-Sto %s 크로스, 반매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, self.slow30)
                            print(alarm_text)
                            self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                        if (order_c == "콜_진(96-100)" and self.slow30 < 85) or (order_c == "풋_진(0-4)" and self.slow30 > 15):
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            alarm_text = "%s S-Sto %s 크로스, 잔량매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, self.slow30)
                            print(alarm_text)
                            self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                    if order_c == "풋_선(5-20)" or order_c == "콜_선(80-95)":
                        if meme_rate > 11 or meme_rate < -20 or datetime.datetime.now().time() >= self.time319:
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            if meme_rate > 15:
                                alarm_text = "%s 수익률 %s 익절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if meme_rate < -20:
                                alarm_text = "%s 수익률 %s 손절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if datetime.datetime.now().time() >= self.time319:
                                alarm_text = "%s \n 현재 시각 3시 19분입니다. 매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % order_c
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")
                        if (order_c =="콜_선(80-95)" and self.slow30 > 95 and self.slow30_prev < 95) or (order_c =="풋_선(5-20)" and self.slow30 <5 and self.slow30_prev > 5):
                            sell_quantity = (order_q - outst_q) * 0.5 - 10
                            sell_quantity = round(sell_quantity, -1)
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"] * 0.5 -10
                                sell_quantity = round(sell_quantity, -1)
                                sell_quantity = int(sell_quantity)
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            alarm_text = "%s S-Sto %s 크로스, 반매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, self.slow30)
                            print(alarm_text)
                            self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                                 ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                                  self.account_num, 2, code, sell_quantity,
                                                  self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")
                        if (order_c =="콜_선(80-95)" and self.slow30 <80) or (order_c =="풋_선(5-20)" and self.slow30 >20):
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            alarm_text = "%s S-Sto %s 크로스, 잔량매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, self.slow30)
                            print(alarm_text)
                            self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                                 ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                                  self.account_num, 2, code, sell_quantity,
                                                  self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                    if order_c == "풋_미(21-100))" or order_c == "콜_미(0-79)":
                        buy_t = datetime.datetime.strptime(buy_t, '%H%M%S')
                        today = datetime.datetime.today()
                        buy_t = buy_t.replace(year=today.year, month=today.month, day=today.day)
                        buy_t_30 = buy_t + datetime.timedelta(minutes=30)
                                                
                        if meme_rate > 5 or meme_rate < -20 or buy_t_30 <= datetime.datetime.now():
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            if meme_rate > 5:
                                alarm_text = "%s 수익률 %s 익절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if meme_rate < -20:
                                alarm_text = "%s 수익률 %s 손절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if buy_t_30 <= datetime.datetime.now():
                                alarm_text = "%s 시간 30분 경과 매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % order_c
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

                    if order_c == "기타매수":
                        buy_t = datetime.datetime.strptime(buy_t, '%H%M%S')
                        today = datetime.datetime.today()
                        buy_t = buy_t.replace(year=today.year, month=today.month, day=today.day)
                        buy_t_5 = buy_t + datetime.timedelta(minutes=5)

                        if meme_rate > 5 or meme_rate < -5 or buy_t_5 <= datetime.datetime.now():
                            sell_quantity = order_q - outst_q
                            sell_quantity = int(sell_quantity)
                            if sell_quantity < self.jango_stock_dict[code]["주문가능수량"]:
                                sell_quantity = sell_quantity
                            else:
                                sell_quantity = self.jango_stock_dict[code]["주문가능수량"]
                            sell_price = ed["현재가"]
                            sell_profit = ed["현재가"] / buy_p - 1
                            sell_profit = "{:.1%}".format(sell_profit)
                            sell_profit_amount = (sell_price - buy_p) * sell_quantity

                            if meme_rate > 5:
                                alarm_text = "%s 수익률 %s 익절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if meme_rate < -20:
                                alarm_text = "%s 수익률 %s 손절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % (order_c, sell_profit)
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                            if buy_t_5 <= datetime.datetime.now():
                                alarm_text = "%s 시간 5분 경과 매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % order_c
                                print(alarm_text)
                                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                            order_success = self.dynamicCall(
                                "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                                 self.account_num, 2, code, sell_quantity,
                                 self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                            if order_success == 0:
                                print("매도주문 전달 성공")
                            else:
                                print("매도주문 전달 실패")

        data_code = []
        for order_nm in self.sales_log_dict.keys():
            code = self.sales_log_dict[order_nm]["종목코드"]
            data_code.append(code)
        for code in self.jango_stock_dict.keys():
            if code in data_code:
                pass
            if code not in data_code:
                jsd = self.jango_stock_dict[code]
                ed = self.elw_dict[code]
                sell_quantity = jsd["주문가능수량"]
                sell_quantity = int(sell_quantity)
                buy_p = jsd["매입단가"]  # 체결가
                meme_rate = (ed["현재가"] - buy_p) / buy_p * 100
                meme_rate = (ed["현재가"] - buy_p) / buy_p * 100
                if meme_rate > 5 or meme_rate < -20 or datetime.datetime.now().time() >= self.time319:
                    sell_price = ed["현재가"]
                    sell_profit = ed["현재가"] / buy_p - 1
                    sell_profit = "{:.1%}".format(sell_profit)
                    sell_profit_amount = (sell_price - buy_p) * sell_quantity
                    if meme_rate > 5:
                        alarm_text = "%s 수익률 %s 익절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % ("기타잔고", sell_profit)
                        print(alarm_text)
                        self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                    if meme_rate < -20:
                        alarm_text = "%s 수익률 %s 손절매도접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % ("기타잔고", sell_profit)
                        print(alarm_text)
                        self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)
                    if datetime.datetime.now().time() >= self.time319:
                        alarm_text = "%s 현재 시각 3시 19분입니다. 매도 접수합니다. \n접수 완료 시 완료 메세지가 뜹니다." % "기타잔고"
                        print(alarm_text)
                        self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                    order_success = self.dynamicCall(
                        "SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                        ["신규매도", self.elw_dict[code]["주문용스크린번호"],
                         self.account_num, 2, code, sell_quantity,
                         self.elw_dict[code]["현재가"], self.realType.SENDTYPE["거래구분"]["지정가"], ""])
                    # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                    # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                    # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))
                    if order_success == 0:
                        print("매도주문 전달 성공")
                    else:
                        print("매도주문 전달 실패")

    def realdata_slot(self, sCode, sRealType, sRealData):
        #Slot - 실시간 데이터를 받는 부분
        '''
        OnReceiveRealData
        :param sCode: 종목코드
        :param sRealType: 리얼타입
        :param sRealData: 실시간 데이터 전문
        :return:
        '''
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]["장운영구분"]
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == "0":
                print("장 시작 전")

            elif value == "3":
                print("장 시작")

            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
                self.bot.sendMessage(chat_id=self.telegram_id, text="장 종료, 동시호가로 넘어갑니다.")

            elif value == "4":
                print("3시30분 장 종료")
                self.bot.sendMessage(chat_id=self.telegram_id, text="3시30분 장 종료되었습니다.")

                for code in self.elw_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.elw_dict[code]["스크린번호"], sCode)

                for code in self.elw_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.elw_dict[code]["스크린번호"], sCode)

                QTest.qWait(5000)

                sys.exit()

            else:
                print("!장이 시작했는지 안 했는지 모르겠다!")

        elif sRealType == "주식체결":

            a = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["체결시간"])  #HHMMSS
            b = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["현재가"])  #+ 또는 - ; 음봉은 -로 나옴
            b = abs(int(b))
            c = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["전일대비"])  #+ 또는 - ; 음봉은 -로 나옴
            c = abs(int(c))
            d = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["등락율"])
            d = float(d)
            e = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["(최우선)매도호가"])  #매도 시장가
            e = abs(int(e))
            f = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["(최우선)매수호가"])
            f = abs(int(f))
            # g = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
            #                      self.realType.REALTYPE[sRealType]["거래량"])  #매도 시장가
            # g = abs(int(g))
            h = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["누적거래량"])
            h = abs(int(h))
            i = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["고가"])
            i = abs(int(i))
            j = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["시가"])
            j = abs(int(j))
            k = self.dynamicCall("GetCommRealData(Qstring, int)", sCode,
                                 self.realType.REALTYPE[sRealType]["저가"])
            k = abs(int(k))

            # if sCode not in self.elw_dict:
            #     self.elw_dict.update({sCode:{}})
            # else:
            ed = self.elw_dict[sCode]
            ed.update({"체결시간": a})
            ed.update({"현재가": b})
            ed.update({"전일대비": c})
            ed.update({"등락율": d})
            ed.update({"(최우선)매도호가": e})
            ed.update({"(최우선)매수호가": f})
            # ecd.update({"거래량": g})
            ed.update({"거래량": h}) #opt30005 의 "거래량" = Realtime "주식체결" 피드의 "누적거래량"
            ed.update({"고가": i})
            ed.update({"시가": j})
            ed.update({"저가": k})

            print(self.elw_dict)

    def chejandata_slot(self, sGubun, nItemCnt, sFIdList):
        #Slot - 체결, 잔고 데이터를 받는 부분
        '''
        OnReceiveChejanData
        :param sGubun: 체결구분 접수와 체결시 '0'값, 국내주식 잔고전달은 '1'값, 파생잔고 전달은 '4'
        :param nItemCnt:
        :param sFIdList:
        :return:
        '''
        #미체결/체결
        if int(sGubun) == 0:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["계좌번호"])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["종목코드"])
            sCode = sCode.strip()[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["종목명"])
            stock_name = stock_name.strip()
            original_order_nm = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["원주문번호"])
            order_nm = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문번호"])
            order_nm = int(order_nm.strip())
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문상태"])
            #(접수, 확인, 체결) (10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부)
            order_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문수량"])
            order_quantity = int(order_quantity)
            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문가격"])
            order_price = int(order_price)
            outstanding_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["미체결수량"])
            if outstanding_quantity == "":
                outstanding_quantity = 0
            else:
                outstanding_quantity = int(outstanding_quantity)
            sign_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["체결량"])
            if sign_quantity == "":
                sign_quantity = 0
            else:
                sign_quantity = int(sign_quantity)
            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문구분"])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
            sign_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문/체결시간"])
            sign_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["체결가"])
            if sign_price == "":
                sign_price = 0
            else:
                sign_price = int(sign_price)
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["현재가"])
            current_price = abs(int(current_price))
            prior_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["(최우선)매도호가"])
            prior_sell_price = abs(int(prior_sell_price))
            prior_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["(최우선)매수호가"])
            prior_buy_price = abs(int(prior_buy_price))

            #새로 들어온 주문이면 주문 번호 할당
            if order_nm not in self.outstanding_order_dict.keys():
                self.outstanding_order_dict.update({order_nm: {}})

            ood = self.outstanding_order_dict[order_nm]
            ood.update({"종목코드": sCode})
            ood.update({"종목명": stock_name})
            ood.update({"원주문번호": original_order_nm})
            ood.update({"주문상태": order_status})
            ood.update({"주문수량": order_quantity})
            ood.update({"주문가격": order_price})
            ood.update({"미체결수량": outstanding_quantity})
            ood.update({"체결량": sign_quantity})
            ood.update({"주문구분": order_gubun})
            ood.update({"주문/체결시간": sign_time_str})
            ood.update({"체결가": sign_price})
            ood.update({"현재가": current_price})
            ood.update({"(최우선)매도호가": prior_buy_price})
            ood.update({"(최우선)매수호가": prior_sell_price})

            if outstanding_quantity == 0:
                del self.outstanding_order_dict[order_nm]

            print("미체결 주문 : %s" % self.outstanding_order_dict[order_nm])

            print("\n거래 요청 내역 %s" % self.outstanding_order_dict)

            if order_status == "접수" and order_gubun == "매수":
                if order_nm not in self.sales_log_dict.keys():
                    self.sales_log_dict.update({order_nm:{}})

                sld = self.sales_log_dict[order_nm]
                sld.update({"일자": datetime.date.today()})
                sld.update({"종목코드": sCode})
                sld.update({"종목명": stock_name})
                sld.update({"원주문번호": original_order_nm})
                sld.update({"주문상태": order_status})
                sld.update({"주문수량": order_quantity})
                sld.update({"미체결수량": outstanding_quantity})
                sld.update({"체결량": sign_quantity})
                sld.update({"주문가격": order_price})
                sld.update({"체결가": sign_price})
                sld.update({"주문구분": order_gubun})
                sld.update({"주문/체결시간": sign_time_str})
                sld.update({"매수코드": self.mesucode})
                sld.update({"매수조건": self.mesusign})
                sld.update({"매수S-sto": self.mesuslow30})

                order_amount = order_quantity * order_price
                order_amount = format(order_amount, ",")
                alarm_text = "%s -- %s \n%s, 총 %s원\n매입단가 %s 매입수량 %s 행사가 %s" % ("<<매수접수완료>>", self.mesucode,
                    sCode, order_amount, order_price, order_quantity, self.elw_dict[sCode]["행사가"])
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

            if order_status == "접수" and order_gubun == "매도":
                order_amount = order_quantity * order_price
                order_amount = format(order_amount, ",")
                buy_p = self.jango_stock_dict[sCode]["매입단가"]
                sell_profit = order_price / buy_p - 1
                sell_profit = "{:.1%}".format(sell_profit)
                sell_profit_amount = (order_price - buy_p) * order_quantity
                sell_profit_amount = format(int(sell_profit_amount), ",")

                alarm_text = "%s -- %s\n수량 %s주 \n단가 %s원(매입단가 %s원)\n총 %s 원\n예상수익금액 %s원 예상수익율 %s" % (
                        "<<매도접수완료>>", sCode, order_quantity, order_price, buy_p,
                        order_amount, sell_profit_amount, sell_profit)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

            if order_status == "접수" and (order_gubun == "매도취소" or order_gubun == "매수취소"):
                alarm_text = "%s -- %s\n수량 %s주" % ("<<취소접수완료>>", sCode, order_quantity)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

            if order_status == "체결" and order_gubun == "매수":
                wb = openpyxl.load_workbook("Tradelog.xlsx")
                meme = wb.get_sheet_by_name('매수')
                meme.append([datetime.date.today(), order_gubun,original_order_nm,order_nm, sCode, stock_name, order_status, order_quantity, outstanding_quantity,
                             sign_time_str, sign_price, self.mesusign, self.mesuslow30, self.mesucode])
                wb.save("Tradelog.xlsx")
                wb.close

                if order_nm not in self.sales_log_dict.keys():
                    self.sales_log_dict.update({order_nm: {}})
                    sld = self.sales_log_dict[order_nm]
                    sld.update({"일자": datetime.date.today()})
                    sld.update({"매수코드": "기타매수"})
                    sld.update({"종목코드": sCode})
                    sld.update({"종목명": stock_name})
                    sld.update({"원주문번호": original_order_nm})
                    sld.update({"주문수량": order_quantity})
                    sld.update({"주문가격": order_price})
                    sld.update({"주문구분": order_gubun})

                sld = self.sales_log_dict[order_nm]
                sld.update({"주문상태": order_status})
                sld.update({"미체결수량": outstanding_quantity})
                sld.update({"체결가": sign_price})
                sld.update({"체결량": sign_quantity})
                sld.update({"주문/체결시간": sign_time_str})

                sign_amount = sign_quantity * sign_price
                sign_amount = format(sign_amount, ",")
                sign_portion = sld["체결량"] / sld["주문수량"]
                sign_portion = "{:.1%}".format(sign_portion)
                left_portion = sld["미체결수량"] / sld["주문수량"]
                left_portion = "{:.1%}".format(left_portion)
                alarm_text = "%s -- %s \n%s\n총 %s주 중 %s주 체결 (s%)\n미체결 수량 %s주 (%s)" % ("<<매수체결>>", sld["매수코드"],
                    ood["종목코드"], ood["주문수량"], ood["체결량"], sign_portion, ood["미체결수량"], left_portion)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)


                self.signal_detail_account_info()

            if order_status == "체결" and order_gubun == "매도":
                wb = openpyxl.load_workbook("Tradelog.xlsx")
                meme = wb.get_sheet_by_name('매도')
                meme.append([datetime.date.today(),order_gubun, original_order_nm, order_nm, sCode, stock_name, order_status, order_quantity, outstanding_quantity,
                             sign_time_str, sign_price, "none", self.slow30, 0])
                wb.save("Tradelog.xlsx")
                wb.close
                alarm_text = "%s \n%s\n총 %s주 중 %s주 체결 (s%)\n미체결 수량 %s주 (%s)" % ("<<매도체결>>",
                    ood["종목코드"], ood["주문수량"], ood["체결량"], sign_portion, ood["미체결수량"], left_portion)
                print(alarm_text)
                self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

                self.signal_detail_account_info()

        #잔고 데이터
        elif int(sGubun) == 1:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["계좌번호"])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["종목코드"])
            sCode = sCode[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["종목명"])
            stock_name = stock_name.strip()
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["현재가"])
            current_price = abs(int(current_price))
            stock_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["보유수량"])
            stock_quantity = int(stock_quantity)
            if stock_quantity == "":
                stock_quantity = 0
            else:
                stock_quantity = int(stock_quantity)
            possible_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["주문가능수량"])
            if possible_quantity == "":
                possible_quantity = 0
            else:
                possible_quantity = int(possible_quantity)
            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["매입단가"])
            buy_price = int(buy_price)
            buy_amount = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["총매입가"])
            buy_amount = int(buy_amount)
            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["매도매수구분"])
            meme_gubun = self.realType.REALTYPE["매도수구분"][meme_gubun]
            prior_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["(최우선)매도호가"])
            prior_sell_price = abs(int(prior_sell_price))
            prior_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["(최우선)매수호가"])
            prior_buy_price = abs(int(prior_buy_price))

            if sCode not in self.jango_stock_dict.keys():
                self.jango_stock_dict.update({sCode: {}})

            jsd = self.jango_stock_dict[sCode]
            jsd.update({"현재가": current_price})
            jsd.update({"종목코드": sCode})
            jsd.update({"종목명": stock_name})
            jsd.update({"보유수량": stock_quantity})
            jsd.update({"주문가능수량": possible_quantity})
            jsd.update({"매입단가": buy_price})
            jsd.update({"총매입가": buy_amount})

            if stock_quantity == 0:
                del self.jango_stock_dict[sCode]

            chejan_text ="체결 후 잔고 %s" % self.jango_stock_dict
            print(chejan_text)
            self.bot.sendMessage(chat_id=self.telegram_id, text=chejan_text)

    def find_max(self):
        #누적거래량 최대 Call 종목 찾기
        if len(self.elw_dict) > 10:
            dt = copy.deepcopy(self.elw_dict)
            data_call = []
            for code in list(dt.keys()):
                if dt[code]["권리구분"] == "콜" and dt[code]["현재가"] >= 300:
                    volume = dt[code]["거래량"]
                    data_call.append(volume)
            max_call_volume = max(data_call)
            for key in dt:
                if dt[key]["거래량"] == max_call_volume and dt[key]["권리구분"] == "콜":
                    self.max_call_code = key

            #누적거래량 최대 Put 종목 찾기
            data_put = []
            for code in list(dt.keys()):
                if dt[code]["권리구분"] == "풋" and dt[code]["현재가"] >= 300:
                    volume = dt[code]["거래량"]
                    data_put.append(volume)
            max_put_volume = max(data_put)
            for key in dt:
                if dt[key]["거래량"] == max_put_volume and dt[key]["권리구분"] == "풋":
                    self.max_put_code = key
        else:
            pass
        threading.Timer(10,self.find_max).start()

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        #Slot - 송수신 메시지 받는 부분
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

    ##############################종목 불러오기
    def read_underlying(self):
        if os.path.exists("file/underlying_assets"):
            f = open("file/underlying_assets", "r", encoding="utf8")
            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")
                    #101Q6000	F 202006	258.1	44
                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = float(ls[2])
                    stock_price = abs(stock_price)
                    left_days = float(ls[3].split("\n")[0])

                    self.underlying_assets_dict.update(
                        {stock_code: {"종목명": stock_name, "현재가": stock_price, "잔존일수": left_days}})

                    if left_days <= 3:
                        alarm_text = "선물 만기일 %s일 남았습니다. 프로그램 업데이트가 필요합니다." % left_days
                        print(alarm_text)
                        self.bot.sendMessage(chat_id=self.telegram_id, text=alarm_text)

            print("선택된 기초자산 종목 %s" % self.underlying_assets_dict)


    def screen_number_setting(self):
        screen_overwrite_elw = []
        screen_overwrite_underlying = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)

        #미체결에 있는 종목들
        for order_nm in self.outstanding_order_dict.keys():
            code = self.outstanding_order_dict[order_nm]["종목코드"]
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)

        #잔고에 있는 종목들
        for code in self.jango_stock_dict.keys():
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)

        #ELW 포트폴리오에 담겨 있는 종목들
        for code in self.elw_dict.keys():
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)

        #기초자산 포트폴리오에 담겨 있는 종목들 스크린 할당
        for code in self.underlying_assets_dict.keys():
            if code not in screen_overwrite_underlying:
                screen_overwrite_underlying.append(code)

        #스크린번호 할당
        cnt = 1
        for code in screen_overwrite_underlying:
            temp_screen = int(self.screen_real_underlying)
            order_screen = int(self.screen_real_underlying)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_underlying = str(temp_screen)

            if code in self.underlying_assets_dict.keys():
                self.underlying_assets_dict[code].update({"스크린번호": str(self.screen_real_underlying)})
            cnt += 1

        print("기초자산 종목 %s개 스크린번호 할당 완료" % len(self.underlying_assets_dict))

        cnt = 1
        for code in screen_overwrite_elw:
            temp_screen = int(self.screen_real_elw)
            order_screen = int(self.screen_order_stock)

            if (cnt % 50) == 0:
                temp_screen += 1  #스크린 번호 하나 당 종목 코드 50개까지만 할당해주겠다.
                self.screen_real_elw = str(temp_screen)

            if (cnt % 50) == 0:
                order_screen += 1
                self.screen_order_stock = str(order_screen)

            if code in self.elw_dict.keys():  #주문용으로도 사용, 실시간 업데이트 할 때에도 쓰려고 하나로 모은 것임
                self.elw_dict[code].update({"스크린번호": str(self.screen_real_elw)})
                self.elw_dict[code].update({"주문용스크린번호": str(self.screen_order_stock)})

            elif code not in self.elw_dict.keys():
                self.elw_dict.update({code:{"스크린번호": str(self.screen_real_elw), "주문용스크린번호": str(self.screen_order_stock)}})

            cnt += 1

        print("구매목표 콜 종목 %s개 스크린번호 할당 완료" % len(self.elw_dict))

        print("구매목표 풋 종목 %s개 스크린번호 할당 완료" % len(self.elw_dict))

    ###계산함수
    def get_macd(self, df):

        df = pd.DataFrame(df)

        ma_12 = df.close.ewm(span=12).mean()
        ma_26 = df.close.ewm(span=26).mean()
        macd = ma_12 - ma_26
        macds = macd.ewm(span=9).mean()
        macd = round(macd, 2)
        macds = round(macds, 2)

        df = df.assign(macd=macd, macds=macds).dropna()

        return df

    def get_sto(self, df, n=5, m=3, t=3):
        df = pd.DataFrame(df)

        ndays_high = df.high.rolling(window=n, min_periods=0).max()
        ndays_low = df.low.rolling(window=n, min_periods=0).min()

        ndays_high = pd.to_numeric(ndays_high)
        ndays_low = pd.to_numeric(ndays_low)
        df.close = pd.to_numeric(df.close)

        fast_k = (df.close - ndays_low) / (ndays_high - ndays_low)
        fast_k = fast_k * 100
        slow_k = fast_k.rolling(m).mean()
        slow_d = slow_k.rolling(t).mean()

        fast_k = round(fast_k, 2)
        slow_k = round(slow_k, 2)
        slow_d = round(slow_d, 2)

        df = df.assign(slow_k=slow_k, slow_d=slow_d).dropna()

        return df

    def cal_macd(self, macd, macds):
        if macd > macds:
            return "call"
        elif macd < macds:
            return "put"
        elif macd == macds:
            return "par"

    def cal_sto(self, slow_k, slow_d):
        if slow_k > slow_d:
            return "call"
        elif slow_k < slow_d:
            return "put"
        elif slow_k == slow_d:
            return "par"
        else:
            pass

    def telegram(self):
        telgm_token = '1232236027:AAG9n41tHK8zHzgV_gh5QY5TKB2I-z4nnUY'
        self.bot = telegram.Bot(token=telgm_token)
        start_text2 = "<<똘봇 감지 시작합니다.>>"
        self.bot.sendMessage(chat_id=self.telegram_id, text=start_text2)

