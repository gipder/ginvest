from PyQt5.QtCore import *
from kiwoom import Kiwoom
from PyQt5.QtWidgets import *

class Thread1(QThread):
    def __init__(self, parent): #부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent) #부모의 윈도우 창을 초기화 한다.
        self.parent = parent     #부모의 윈도우를 사용하기 위한 조건


        #### 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ####

        #### 사용되는 변수
        self.Acc_Screen = "1000" 
        #계좌평가잔고내역을 받기위한 스크린 
        #1~9999까지 총 9999개 존재 1개당 50개의 데이터를 저장
        #기관 매수 종목이 60개면 한개의 스크린에 50개의 종목 저장
        #그래서 총 2개의 스크린이 필요
        #만약 1개의 스크린에 60개의 종목을 넣으면 앞의 10개 삭제

        #### 슬롯
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)
        #### 이벤트 루프
        self.detail_account_info_event_loop = QEventLoop()
        #### 계좌정보 가져오기
        self.getItemList() #종목 이름 받아오기
        self.detail_account_mystock() #계좌평가잔고내역 가져오기

    def getItemList(self):
        marketList = ["0", "10"]

        for market in marketList:
            codeList = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(";")[:-1]

            for code in codeList:
                name = self.k.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)
                self.k.All_Stock_Code.update({code: {"종목명": name}})

    def detail_account_mystock(self, sPrevNext="0"):

        print("계좌평가잔고내역 조회")
        account = self.parent.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        print("최종 선택 계좌는 %s" % self.account_num)

        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")  # 모의투자 0000
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.Acc_Screen)
        self.detail_account_info_event_loop.exec_()
        #출처: https://auto-trading.tistory.com/entry/주식자동매매-17강-계좌평가잔고내역요청4-서버에-내역-요청하기opw00018 [경제적 자유(주식자동매매, 파이썬 코딩):티스토리]

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "계좌평가잔고내역요청":

            column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
            colCount = len(column_head)
            rowCount = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.parent.stocklistTableWidget_2.setColumnCount(colCount)                 # 행 갯수
            self.parent.stocklistTableWidget_2.setRowCount(rowCount)                    # 열 갯수 (종목 수)
            self.parent.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입

            self.rowCount = rowCount

            print("계좌에 들어있는 종목 수 %s" % rowCount)

            totalBuyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)"))
            #출처: https://auto-trading.tistory.com/entry/주식자동매매-18강-계좌평가잔고내역요청6-Tr-데이터-받아오기싱글데이터 [경제적 자유(주식자동매매, 파이썬 코딩):티스토리]