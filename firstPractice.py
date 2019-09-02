# 파이썬 3.6.8 32bit 환경에서 실습
# 증권사 open api 이용을 위해서는 32bit로 환경 설정 해야됨

# 원래 사용하던 interpreter는 AppData\nLocal 에 있는 python 3.7

import sys

# pyqt5는 GUI 프로그램을 만들 수 있게 해주는 프레임워크
from builtins import super
from email.charset import QP

from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QPushButton, QPushButton, QPushButton


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyStock")
        self.setGeometry(100, 100, 500, 400)  # 윈도우 안에서의 팝업 시킬 위치 지정

        # API 모듈 가져오기?
        self.kiwoom = QAxWidget("KHOPENAPI.KHopenAPICtrl.1")

        # 버튼 두개 달아주기
        btn1 = QPushButton("로그인", self)
        btn1.move(20, 20)
        btn1.clicked.connect(self.btn1_clicked)

        btn2 = QPushButton("확인", self)
        btn2.move(20, 70)  # move 함수는 위치 지정 해주는 건가?
        btn2.clicked.connect(self.bnt2_clicked)

        self.edit_text = QTextEdit(self)
        self.edit_text.setGeometry(10, 100, 400, 300)
        self.edit_text.setEnabled(False)

    def btn1_clicked(self):

        ret = self.kiwoom.dynamicCall("CommConnect()")

    def bnt2_clicked(self, id):
        # GetConnectState 현재 접속 상태를 반환하는 함수
        if self.kiwoom.dynamicCall("GetConnectState()") == 0:
            # GetConnectState 의 반환값은 0과 1(미연결 , 연결)
            self.statusBar().showMessage("연결이 안되어 있습니다.")

        else:
            log_info_id = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_ID"])
            log_info_name = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_NAME"])
            log_info_accno = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
            print(log_info_id + " " + log_info_name + " " + log_info_accno + " ")
            self.statusBar().showMessage(log_info_id + "님 연결이 완료 되었습니다.")
            # 연결이 완료 되면
            self.edit_text.append("로그인 ID : " + log_info_id)
            self.edit_text.append("로그인 NAME : " + log_info_name)
            self.edit_text.append("로그인 계좌 번호 : " + log_info_accno)



class CodeReceive(QMainWindow):

    def __init__(self):
        super().__init__()

        self.kiwoom = QAxWidget("KHOPENAPI.KHopenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        # 로그인 끝나고
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        self.setWindowTitle("종목 코드 확인하는 창")
        self.setGeometry(300, 300, 500, 300)  # 윈도우 안에서의 팝업 시킬 위치 지정

        label = QLabel("종목 코드 :  ", self)
        label.move(20, 20)

        # edit Text 하나 만들기
        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 20)
        # self.code_edit.setText("039490")

        btn1 = QPushButton("조회", self)
        btn1.move(190, 20)
        btn1.clicked.connect(self.btn1_clicked)

        # edit text 모양으로 결괏값을 보여주는 창
        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 400, 150)
        # 유저가 조작할 필요 없으니까 enabled(False)
        self.text_edit.setEnabled(False)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")

    def btn1_clicked(self):
        code = self.code_edit.text()
        self.text_edit.append("종목 코드 : " + code)  # 결괏값 실제 뿌리는 코드

        # void SetInputValue(BSTR sID, BSTR sValue)
        # openApi.SetInputValue(“종목코드”, “000660”);
        # openApi.SetInputValue(“계좌번호”, “5015123401”);
        # SQL 처럼 사용
        self.kiwoom.dynamicCall("SetInputValue(QString, QStrng)", "종목코드", code)
        # LONG CommRqData(BSTR sRQName, BSTR sTrCode, long nPrevNext, BSTR sScreenNo)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int,QStirng)", trcode, "", rqname, 0,
                                           "종목명")
            # opt10001 명령에서 조회 할 수 있는 것들에는 거래량, 현재가 종목명 등등 KOA studio로 확인할 수 있음
            vol = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int,QStirng)", trcode, "", rqname, 0,
                                          "거래량")
            cur = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0,
                                          "현재가")
            total = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,
                                            0, "시가총액")

            self.text_edit.append("종목 명 : " + name.strip())
            self.text_edit.append("거래량 : " + vol.strip())
            self.text_edit.append("현재가 : " + cur.strip())
            self.text_edit.append("시가총액 : " + total.strip())


class StockList(QMainWindow):
    def __init__(self):
        super().__init__()

        self.kiwoom = QAxWidget("KHOPENAPI.KHopenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.setWindowTitle("종목 코드 전체")
        self.setGeometry(500, 500, 400, 200)

        btn1 = QPushButton("종목 코드 얻기", self)
        btn1.move(190, 10)
        btn1.clicked.connect(self.btn_clicked)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(10, 10, 170, 130)

    def btn_clicked(self):
        ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kospi_code_list = ret.split(';')
        kospi_code_name = []

        for i in kospi_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [i])
            kospi_code_name.append(i + " : " + name)

        self.listWidget.addItems(kospi_code_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    code = CodeReceive()
    code.show()
    list = StockList()
    list.show()
    app.exec_()
