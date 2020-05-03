import os
import sys
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomtype import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스입니다.")

        ############### event loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ##############################

        ############### 스크린번호 모음
        self.screen_my_info = "100"
        self.screen_real_elw = "200" #실시간으로 ELW데이터 요청용
        self.screen_real_underlying = "300" #실시간으로 기초자산 데이터 요청용
        self.screen_order_stock = "400" #주문 요청용
        self.screen_market_time = "500" #장 시작/종료 여부 확인 요청용
        self.screen_elw = "600"
        ##############################

        ############### 변수 및 딕셔너리 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.jango_stock_dict = {}
        self.outstanding_order_dict = {}
        self.underlying_assets_dict = {}
        self.elw_call_dict = {}
        self.elw_put_dict = {}
        self.elw_else_dict = {}
        self.realType = RealType() #kiwoomtype에서 RealType 클래스 불러옴
        ##############################

        ############### 종목분석용
        self.calculator_data = []
        self.elw_call_list = []
        ##############################

        ############### 계좌관련변수
        self.pocket_money = 0
        self.pocket_money_percent = 0.5
        ##############################

        ############### 코드 실행
        self.get_ocx_instance()
        self.event_slots() #받은 Slots 가져오기
        self.event_slots_real() #받은 실시간 Slots 가져오기
        self.signal_login_commConnect() #로그인 Event 요청
        self.get_account_info() #계좌번호 요청 & 반환
        self.signal_detail_account_info() #예수금 Event 요청
        self.signal_mystock_info() #잔고내역 Event 요청
        self.signal_outstanding_order() #미체결내역 Event 요청
        self.signal_market_time() #장시작여부 Event요청
        self.read_underlying() #저장된 기초자산 불러오기
        self.get_elw_call_list() #ELW 종목 분석용, 임시용으로 실행
        self.get_elw_put_list()#ELW 종목 분석용, 임시용으로 실행
        self.read_elw_call() #저장된 ELW 종목 불러오기
        self.read_elw_put()  # 저장된 ELW 종목 불러오기
        self.screen_number_setting() #불러온 모든 종목에 대해 Screen number 지정해주기 (기초자산, ELW, 종목 등)
        for code in self.elw_call_dict.keys():
            screen_num = self.elw_call_dict[code]["스크린번호"]
            fids = self.realType.REALTYPE["주식체결"]["체결시간"]
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1") #실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
            print("실시간 등록 코드: %s, 스크린번호: %s, fid 번호: %s" % (code, screen_num, fids))
        for code in self.elw_put_dict.keys():
            screen_num = self.elw_put_dict[code]["스크린번호"]
            fids = self.realType.REALTYPE["주식체결"]["체결시간"]
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1") #실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
            print("실시간 등록 코드: %s, 스크린번호: %s, fid 번호: %s" % (code, screen_num, fids))
        for code in self.underlying_assets_dict.keys():
            screen_num = self.underlying_assets_dict[code]["스크린번호"]
            fids = self.realType.REALTYPE["주식체결"]["체결시간"]
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1") #실시간 시세를 받으려는 종목코드와 FID 리스트를 이용해서 실시간 시세를 등록하는 함수입니다.
            print("실시간 등록 코드: %s, 스크린번호: %s, fid 번호: %s" % (code, screen_num, fids))
        ##############################



    ############################## 제어
    def get_ocx_instance(self):
        #Open API 제어 시작
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")


    ############################## Events
    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")
        #Event - 로그인 요청 보내는 부분
        self.login_event_loop =QEventLoop()
        self.login_event_loop.exec_()

    def get_account_info(self):
        #Event - 계좌번호 요청 보내는 부분; 별도 Slot 없이 변수로 받음
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(';')[0]
        print("내 계좌번호 %s" % self.account_num) #8135128711

    def signal_detail_account_info(self):
        print("내 계좌 현황")
        #Event - 예수금 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def signal_mystock_info(self, sPrevNext="0"):
        print("계좌평가 잔고내역 - 페이지 %s" % sPrevNext)
        #Event - 계좌평가잔고 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", "0", self.screen_my_info)

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
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_market_time, "", self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

    def get_elw_call_list(self):
        print("ELW 콜 리스트 요청")
        #Event - ELW KOSPI200 콜 리스트 조건검색 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "기초자산코드", "201")
        self.dynamicCall("SetInputValue(QString, QString)", "권리구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "5")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "ELW조건검색요청 - 콜", "opt30005", "0", self.screen_elw)

        self.detail_account_info_event_loop.exec_()

    def get_elw_put_list(self):
        print("ELW 픗 리스트 요청")
        #Event - ELW KOSPI200 풋 리스트 조건검색 요청 보내는 부분
        self.dynamicCall("SetInputValue(QString, QString)", "기초자산코드", "201")
        self.dynamicCall("SetInputValue(QString, QString)", "권리구분", "2")
        self.dynamicCall("SetInputValue(QString, QString)", "정렬구분", "5")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "ELW조건검색요청 - 풋", "opt30005", "0", self.screen_elw)

        self.detail_account_info_event_loop.exec_()


    ############################## Slots
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
            print("예수금 %s" % format(int(deposit),","))

            self.pocket_money = int(deposit) * self.pocket_money_percent
            self.pocket_money = self.pocket_money /4 #있는 예수금 중 X%/4 만큼만 사용해서 종목 구매; 사다보면 계속 전체의 X%/4 만큼 사게 됨

            orderable = self.dynamicCall("GetCommData(String, String, String, String)", sTrCode, sRQName, 0, "주문가능금액")
            print("주문가능금액 %s" % format(int(orderable),","))

            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            purchased = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            print("총매입금액 %s" % format(int(purchased),","))

            valuation = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총평가금액")
            print("총평가금액 %s" % format(int(valuation), ","))

            profit_percent = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            print("총수익률(%%) %s" % float(profit_percent))

            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드") #A:장내주식 J:ELW Q:ETN
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                possessed_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                purchased_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                earn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_amount = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

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
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") #접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") #매도, 매수, 정정, 취소
                outstanding_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                concluded_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결수량")

                code = code.strip()[1:]
                code_nm = code_nm.strip()
                order_nm = int(order_nm.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                outstanding_quantity = int(outstanding_quantity.strip())
                concluded_quantity = int(concluded_quantity.strip())

                if order_nm in self.outstanding_order_dict:
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
                ood.update({"체결수량": concluded_quantity})

                print("미체결 주문 : %s" % self.outstanding_order_dict[order_nm])

                cnt += 1

            self.detail_account_info_event_loop.exit()


        elif sRQName == "ELW조건검색요청 - 콜":
            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            print("KOSPI200 ELW 콜 개수: %s" % rows)
            cnt = 0

            f = open("file/elw_call", "w", encoding="utf8")
            f.close()

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                position = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "권리구분")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                strike_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "행사가격")
                trade_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                strike_date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "만기일")
                left_days = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "잔존일수")

                code = code.strip()
                code_nm = code_nm.strip()
                position = position.strip()
                current_price = abs(int(current_price.strip()))
                strike_price = float(strike_price.strip())
                trade_volume = int(trade_volume.strip())
                strike_date = strike_date.strip()
                left_days = int(left_days.strip())

                f = open("file/elw_call", "a", encoding="utf8")
                f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (code, code_nm, position, current_price, strike_price, trade_volume, strike_date, left_days))
                f.close()

                cnt += 1

            self.detail_account_info_event_loop.exit()

        elif sRQName == "ELW조건검색요청 - 풋":
            rows = self.dynamicCall("GetRepeatCnT(QString, QString)", sTrCode, sRQName)
            print("KOSPI200 ELW 풋 개수: %s" % rows)
            cnt = 0

            f = open("file/elw_put", "w", encoding="utf8")
            f.close()

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                position = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "권리구분")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                strike_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "행사가격")
                trade_volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                strike_date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "만기일")
                left_days = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "잔존일수")

                code = code.strip()
                code_nm = code_nm.strip()
                position = position.strip()
                current_price = abs(int(current_price.strip()))
                strike_price = float(strike_price.strip())
                trade_volume = int(trade_volume.strip())
                strike_date = strike_date.strip()
                left_days = int(left_days.strip())

                f = open("file/elw_put", "a", encoding="utf8")
                f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (code, code_nm, position, current_price, strike_price, trade_volume, strike_date, left_days))
                f.close()

                cnt += 1

            self.detail_account_info_event_loop.exit()

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

            elif value == "4":
                print("3시30분 장 종료")

                for code in self.elw_call_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.elw_call_dict[code]["스크린번호"], sCode)

                for code in self.elw_put_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.elw_put_dict[code]["스크린번호"], sCode)


                QTest.qWait(5000)

                self.file_delete()
                # self.calculator_func()

                sys.exit()

            else:
                print("!장이 시작했는지 안 했는지 모르겠다!")

        elif sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["체결시간"])         #HHMMSS
            b = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["현재가"])          #+ 또는 - ; 음봉은 -로 나옴
            b = abs(int(b))
            c = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["전일대비"])         #+ 또는 - ; 음봉은 -로 나옴
            c = abs(int(c))
            d = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["등락율"])
            d = float(d)
            e = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["(최우선)매도호가"]) #매도 시장가
            e = abs(int(e))
            f = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["(최우선)매수호가"])  # 매도 시장가
            f = abs(int(f))
            g = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["거래량"])  # 매도 시장가
            g = abs(int(g))
            h = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["누적거래량"])  # 매도 시장가
            h = abs(int(h))
            i = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["고가"])  # 매도 시장가
            i = abs(int(i))
            j = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["시가"])  # 매도 시장가
            j = abs(int(j))
            k = self.dynamicCall("GetCommRealData(Qstring, int)", sCode, self.realType.REALTYPE[sRealType]["저가"])  # 매도 시장가
            k = abs(int(k))

            # 콜 종목 실시간 업데이트
            ecd = self.elw_call_dict[sCode]
            ecd.update({"체결시간": a})
            ecd.update({"현재가": b})
            ecd.update({"전일대비": c})
            ecd.update({"등락율": d})
            ecd.update({"(최우선)매도호가": e})
            ecd.update({"(최우선)매수호가": f})
            ecd.update({"거래량": g})
            ecd.update({"누적거래량": h})
            ecd.update({"고가": i})
            ecd.update({"시가": j})
            ecd.update({"저가": k})

            print(self.elw_call_dict[sCode])

            # 풋 종목 실시간 업데이트
            epd = self.elw_put_dict[sCode]
            epd.update({"체결시간": a})
            epd.update({"현재가": b})
            epd.update({"전일대비": c})
            epd.update({"등락율": d})
            epd.update({"(최우선)매도호가": e})
            epd.update({"(최우선)매수호가": f})
            epd.update({"거래량": g})
            epd.update({"누적거래량": h})
            epd.update({"고가": i})
            epd.update({"시가": j})
            epd.update({"저가": k})

            print(self.elw_put_dict[sCode])


            # 기초자산 종목 실시간 업데이트
            uad = self.underlying_assets_dict[sCode]
            uad.update({"체결시간": a})
            uad.update({"현재가": b})
            uad.update({"전일대비": c})
            uad.update({"등락율": d})
            uad.update({"(최우선)매도호가": e})
            uad.update({"(최우선)매수호가": f})
            uad.update({"거래량": g})
            uad.update({"누적거래량": h})
            uad.update({"고가": i})
            uad.update({"시가": j})
            uad.update({"저가": k})

            print(self.underlying_assets_dict[sCode])

            #이전 계좌 잔고 평가 내역에 있고 오늘 사지 않은 주식인 경우, 신규 매도
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                asd = self.account_stock_dict[sCode]

                meme_rate = (b - asd["매입가"]) / asd["매입가"] * 100


                #####매도 조건
                if asd["매매가능수량"] > 0 and (meme_rate > 5 or meme_rate < (-5)):
                    order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                                     ["신규매도", self.elw_stocks_dict[sCode]["주문용스크린번호"], self.account_num, 2,
                                                     sCode, asd["매매가능수량"], 0, self.realType.SENDTYPE["거래구분"]["시장가"], ""])
                    #SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                    #nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                    #sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))

                    if order_success == 0:
                        print("매도주문 전달 성공")
                        del self.account_stock_dict[sCode]


                    else:
                        print("매도주문 전달 실패")


            # 오늘 산 잔고에 있을 경우, 신규 매도
            elif sCode in self.jango_stock_dict():
                print("%s %s" % ("신규 매도를 한다2", sCode))

            # 등락율이 2.0% 이상이고 오늘 산 잔고에 없을 경우 신규 매수
            elif d > 2.0 and sCode not in self.jango_stock_dict:
                print("%s %s" % ("신규 매수를 한다", sCode))

                buy_quantity = self.pocket_money / e
                buy_quantity = int(buy_quantity)

                order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                                     ["신규매수", self.elw_stocks_dict[sCode]["주문용스크린번호"], self.account_num, 1,
                                                     sCode, buy_quantity, b, self.realType.SENDTYPE["거래구분"]["지정가"], ""])
            # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
            # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
            # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))

                if order_success == 0:
                    self.logging.logger.debug("매수주문 전달 성공")
                else:
                    self.logging.logger.debug("매수주문 전달 실패")



            outstanding_list = list(self.outstanding_order_dict) #복사 하는 이유 - for 문 돌리는 중에 미체결에 추가 주문이 들어오면 에러가 나기 때문임
            for order_nm in outstanding_list:
                code = self.outstanding_order_dict[order_nm]["종목코드"]
                order_price = self.outstanding_order_dict[order_nm]["주문가격"]
                outstanding_quantity = self.outstanding_order_dict[order_nm]["미체결수량"]
                order_gubun = self.outstanding_order_dict[order_nm]["주문구분"]

                #매수 미체결주문량이 남아 있고, 현재가가 주문가보다 높은 경우
                if order_gubun == "매수" and outstanding_quantity > 0 and e > order_price:
                    order_success = self.dynamicCall("SendOrder(Qstring, Qstring, Qstring, int, Qstring, int, int, Qstring, Qstring)",
                                                     ["매수취소", self.elw_stocks_dict[sCode]["주문용스크린번호"], self.account_num, 3,
                                                      sCode, 0, 0, self.realType.SENDTYPE["거래구분"]["지정가"], order_nm])
                    # SendOrder(sRQName(사용자구분명), sScreenNo(화면번호), sAccNo,
                    # nOrderType(주문유형 1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정),
                    # sCode, nQty, nPrice, sHogaGb, sOrgOrderNo(원주문번호))

                    if order_success == 0:
                        self.logging.logger.debug("매수취소 전달 성공")
                    else:
                        self.logging.logger.debug("매수취소 전달 실패 ")

                elif outstanding_quantity == 0:
                    del self.outstanding_order_dict[order_nm]


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
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["종목코드"])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["종목명"])
            stock_name = stock_name.strip()
            original_order_nm = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["원주문번호"])
            order_nm = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문번호"])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문상태"])
                # (접수, 확인, 체결) (10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부)
            order_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문수량"])
            order_quantity = int(order_quantity)
            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["주문가격"])
            order_price = int(order_price)
            outstanding_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["주문체결"]["미체결수량"])
            outstanding_quantity = int(outstanding_quantity)
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
            ood.update({"주문구분": order_gubun})
            ood.update({"주문/체결시간": sign_time_str})
            ood.update({"체결가": sign_price})
            ood.update({"현재가": current_price})
            ood.update({"(최우선)매도호가": prior_buy_price})
            ood.update({"(최우선)매수호가": prior_sell_price})

            print(self.outstanding_order_dict)

        #잔고 데이터
        elif int(sGubun) == 1:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["계좌번호"])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["종목코드"])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["종목명"])
            stock_name = stock_name.strip()
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["현재가"])
            current_price = abs(int(current_price))
            stock_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["보유수량"])
            stock_quantity = int(stock_quantity)
            possible_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE["잔고"]["주문가능수량"])
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
            jsd.update({"현재가": current_price})
            jsd.update({"보유수량": stock_quantity})
            jsd.update({"주문가능수량": possible_quantity})
            jsd.update({"매입단가": buy_price})
            jsd.update({"총매입가": buy_amount})
            jsd.update({"매도매수구분": meme_gubun})
            jsd.update({"(최우선)매도호가": prior_sell_price})
            jsd.update({"(최우선)매수호가": prior_buy_price})

            print(self.jango_stock_dict)

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        # Slot - 송수신 메시지 받는 부분
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

    def file_delete(self):
        if os.path.isfile("file/elw_stocks"):
            os.remove("file/elw_stocks")



    ############################## 종목 불러오기
    def read_underlying(self):
        if os.path.exists("file/underlying_assets"):
            f = open("file/underlying_assets", "r", encoding="utf8")
            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split(",")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = float(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.underlying_assets_dict.update({stock_code: {"종목명" : stock_name, "현재가" : stock_price}})

            print("선택된 기초자산 종목 %s" % self.underlying_assets_dict)

    def read_elw_call(self):
        if os.path.exists("file/elw_call"):
            f = open("file/elw_call", "r", encoding="utf8")
            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    code = ls[0]
                    code_nm = ls[1]
                    position = ls[2]
                    current_price = ls[3]
                    strike_price = ls[4]
                    trade_volume = ls[5]
                    left_days = ls[7].split("\n")[0]

                    self.elw_call_dict.update({code: {"종목명": code_nm, "권리구분": position, "현재가": current_price, "행사가" : strike_price, "거래량": trade_volume, "잔존일수": left_days}})

            print("선택된 ELW 콜 종목 %s" % self.elw_call_dict)

    def read_elw_put(self):
        if os.path.exists("file/elw_put"):
            f = open("file/elw_put", "r", encoding="utf8")
            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    code = ls[0]
                    code_nm = ls[1]
                    position = ls[2]
                    current_price = ls[3]
                    strike_price = ls[4]
                    trade_volume = ls[5]
                    left_days = ls[7].split("\n")[0]

                    self.elw_put_dict.update({code: {"종목명": code_nm, "권리구분": position, "현재가": current_price, "행사가" : strike_price, "거래량": trade_volume, "잔존일수": left_days}})

            print("선택된 ELW 풋 종목 %s" % self.elw_call_dict)


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

        #ELW 콜 포트폴리오에 담겨 있는 종목들
        for code in self.elw_call_dict.keys():
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)

        #ELW 풋 포트폴리오에 담겨 있는 종목들
        for code in self.elw_put_dict.keys():
            if code not in screen_overwrite_elw:
                screen_overwrite_elw.append(code)


        #스크린번호 할당
        cnt = 1
        for code in screen_overwrite_elw:
            temp_screen = int(self.screen_real_elw)
            order_screen = int(self.screen_order_stock)

            if (cnt % 50) ==0:
                temp_screen += 1 #스크린 번호 하나 당 종목 코드 50개까지만 할당해주겠다.
                self.screen_real_elw = str(temp_screen)

            if (cnt % 50) ==0:
                order_screen += 1
                self.screen_order_stock = str(order_screen)

            if code in self.elw_call_dict.keys(): #주문용으로도 사용, 실시간 업데이트 할 때에도 쓰려고 하나로 모은 것임
                self.elw_call_dict[code].update({"스크린번호": str(self.screen_real_elw)})
                self.elw_call_dict[code].update({"주문용스크린번호": str(self.screen_order_stock)})

            if code in self.elw_put_dict.keys(): #주문용으로도 사용, 실시간 업데이트 할 때에도 쓰려고 하나로 모은 것임
                self.elw_put_dict[code].update({"스크린번호": str(self.screen_real_elw)})
                self.elw_put_dict[code].update({"주문용스크린번호": str(self.screen_order_stock)})

            elif code not in self.elw_else_dict.keys():
                self.elw_else_dict.update({code: {"스크린번호": str(self.screen_real_elw), "주문용스크린번호": str(self.screen_real_elw)}})

            cnt +=1

        print("구매목표 콜 종목 %s" % self.elw_call_dict)
        print("구매목표 풋 종목 %s" % self.elw_put_dict)

        # 기초자산 포트폴리오에 담겨 있는 종목들 스크린 할당
        for code in self.underlying_assets_dict.keys():
            if code not in screen_overwrite_underlying:
                screen_overwrite_underlying.append(code)

        cnt = 1
        for code in screen_overwrite_underlying:
            temp_screen = int(self.screen_real_underlying)
            order_screen = int(self.screen_real_underlying)

            if (cnt %50) ==0:
                temp_screen += 1
                self.screen_real_underlying = str(temp_screen)

            if code in self.underlying_assets_dict.keys():
                self.underlying_assets_dict[code].update({"스크린번호": str(self.screen_real_underlying)})
            cnt +=1

        print("기초자산 종목 %s" % self.underlying_assets_dict)





