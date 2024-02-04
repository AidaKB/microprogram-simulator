from PyQt5 import  QtWidgets,uic
from PyQt5.QtWidgets import QWidget,QMessageBox
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
import re
opcodes = {"0000":"ADD", "0001":"BRANCH", "0010":"STORE", "0011":"EXCHANGE", "0100":"LOAD", "0101":"AND", "0111":"ADM", "1111":"HLT"}
F1 = {"000":"NOP", "001":"ADD", "010":"CLRAC", "011":"INCAC", "100":"DRTAC", "101":"DRTAR", "110":"PCTAR", "111":"WRITE"}
F2 = {"000":"NOP", "001":"SUB", "010":"OR", "011":"AND", "100":"READ", "101":"ACTDR", "110":"INCDR", "111":"PCTDR"}
F3 = {"000":"NOP", "001":"XOM", "010":"COM", "011":"SHL", "100":"SHR", "101":"INCPC", "110":"ARTPC", "111":"RES"}
CD = {"00":"U", "01":"I", "10":"S", "11":"Z"}
BR = {"00":"JMP", "01":"CALL", "10":"RET", "11":"MAP"}
class Myclass(QtWidgets.QMainWindow):
    def __init__(self):
        self.AC="0"*16
        self.PC="0"*11
        self.AR="0"*11
        self.DR="0"*16
        self.CAR="0"*7
        self.SBR="0"*7
        class RAMRegister():
            def __init__(self):
                self.i="0"
                self.opcode="0"*4
                self.add="0"*11
            def __str__(self) :
                return self.i+self.opcode+self.add
            def __repr__(self):
                return self.i+self.opcode+self.add
        class MRegister():
            def __init__(self):
                self.f1="000"
                self.f2="000"
                self.f3="000"
                self.cd="00"
                self.br="00"
                self.ad="0"*7
            def __str__(self) :
                return self.f1+self.f2+self.f3+self.cd+self.br+self.ad
            def __repr__(self):
                return self.f1+self.f2+self.f3+self.cd+self.br+self.ad
        self.control_memory = [MRegister() for i in range(128)] 
        #initial control memory
        #FETCH operation
        #1. FETCH: AR ← PC                              -> PCTAR U JMP NEXT         -> 110 000 000 00 00 1000001
        self.control_memory[64] = "11000000000001000001"
        #2. DR ← M[AR], PC ← PC + 1                     -> READ, INCPC U JMP NEXT   -> 000 100 101 00 00 1000010
        self.control_memory[65] = "00010010100001000010"
        #3. AR ← DR(10-0),     
        #CAR(5-2) ← DR(14-11), CAR (7,6,0) ← 0        -> DRTAR U MAP              -> 101 000 000 00 11 0000000
        self.control_memory[66] = "10100000000110000000"

        #INDRCT operation
        #1. INDRCT: DR ← M[AR]                          -> READ U JMP NEXT          -> 100 000 000 00 00 1000100
        self.control_memory[67] = "10000000000001000100"
        #2. AR ← DR(10–0)                               -> DRTAR U RET              -> 101 000 000 00 10

        #ADD operation
        #1. ADD: NOP I CALL INDRCT      -> 000 000 000 01 01 1000011
        self.control_memory[0] = "00000000001011000011"       
        #2. READ U JMP NEXT             -> 000 100 000 00 00 0000010
        self.control_memory[1] = "00010000000000000010"
        #3. ADD U JMP FETCH             -> 001 000 000 00 00 1000000
        self.control_memory[2] = "00100000000001000000"

        #BRANCH operation
        #1. BRANCH: NOP S JMP OVER      -> 000 000 000 10 00 0000110
        self.control_memory[4] = "00000000010000000110"       
        #2. NOP U JMP FETCH             -> 000 000 000 00 00 1000000
        self.control_memory[5] = "00000000000001000000"
        #3. OVER: NOP I CALL INDRCT     -> 000 000 000 01 01 1000011
        self.control_memory[6] = "00000000001011000011"
        #4. ARTPC U JMP FETCH           -> 000 000 110 00 00 1000000
        self.control_memory[7] = "00000011000001000000"

        #STORE operation
        #1. NOP I CALL INDRCT           -> 000 000 000 01 01 1000011
        self.control_memory[8] = "00000000001011000011"
        #2. ACTDR U JMP NEXT            -> 000 101 000 00 00 0001001
        self.control_memory[9] = "00010100000000001010"
        #3. WRITE U JMP FETCH           -> 111 000 000 00 00 1000000
        self.control_memory[10] = "11100000000001000000"

        #EXCHANGE operation
        #1. EXCH: NOP I CALL INDRCT     -> 000 000 000 01 01 1000011
        self.control_memory[12] = "00000000001011000011"
        #2. READ U JMP NEXT             -> 100 000 000 00 00 0001101
        self.control_memory[13] = "00010000000000001110"
        #3. ACTDR, DRTAC U JMP NEXT     -> 101 101 000 00 00 0001110
        self.control_memory[14] = "10010100000000001111"
        #4. WRITE U JMP FETCH           -> 111 000 000 00 00 1000000
        self.control_memory[15] = "11100000000001000000"
        #LOAD operation
        #1. LOAD; NOP I CALL INDRCT     -> 000 000 000 01 01 1000011
        self.control_memory[16] = "00000000001011000011"
        #2. READ U JMP NEXT             -> 100 000 000 00 00 0010001
        self.control_memory[17] = "00010000000000010010"
        #3. DRTAC U JMP FETCH           -> 101 101 000 00 00 1000000
        self.control_memory[18] = "10000000000001000000"

        #AND operation
        #1. AND: NOP I CALL INDRCT      -> 000 000 000 01 01 1000011
        self.control_memory[20] = "00001100001011000011"       
        #2. READ U JMP NEXT             -> 000 100 000 00 00 0010110
        self.control_memory[21] = "00010000000000010110"
        #3. AND U JMP FETCH             -> 001 000 000 00 00 1000000
        self.control_memory[22] = "01100000000001000000"

        #ADM operation
        #1. ADM: NOP I CALL INDRCT      -> 000 000 000 01 01 1000011
        self.control_memory[24] = "00000000001011000011"       
        #2. READ U JMP NEXT             -> 000 100 000 00 00 0000010
        self.control_memory[25] = "00010000000000011010"
        #3. ADD U JMP NEXT             -> 001 000 000 00 00 1000000
        self.control_memory[26] = "00100000000000011011"
        #4. WRITE U JMP FETCH           -> 111 000 000 00 00 1000000
        self.control_memory[27] = "11100000000001000000"
        super(Myclass, self).__init__()
        uic.loadUi('f:/projects/mymicroprogram/mainwindow.ui',self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.show()
        f = self.textEdit.font()
        f.setPointSize(27)
        self.commandList=[]
        self.labels={}
        self.pushButton.clicked.connect(self.get_program)
        self.pushButton_3.clicked.connect(self.execute)####################################new
        self.pushButton_2.clicked.connect(self.debug)
        self.RAM=[RAMRegister() for i in range(2048)]
        self.tableWidget.setColumnWidth(0,30)
        self.tableWidget.setColumnWidth(1,80)
        self.tableWidget.setColumnWidth(2,200)
        self.tableWidget.setRowCount(2048)

        for row in range(0,2048):
            data=QtWidgets.QTableWidgetItem("0")
            data.setTextAlignment(Qt.AlignHCenter) 
            self.tableWidget.setItem(row,0,data)
            data=QtWidgets.QTableWidgetItem("0"*4)
            data.setTextAlignment(Qt.AlignHCenter) 
            self.tableWidget.setItem(row,1,data)
            data=QtWidgets.QTableWidgetItem("0"*11)
            data.setTextAlignment(Qt.AlignHCenter) 
            self.tableWidget.setItem(row,2,data)
    def set_program_in_memory(self,tableWidget,num,add):
            data=QtWidgets.QTableWidgetItem(num[0])
            data.setTextAlignment(Qt.AlignHCenter) 
            tableWidget.setItem(add,0,data)
            data=QtWidgets.QTableWidgetItem(num[1:5])
            data.setTextAlignment(Qt.AlignHCenter) 
            tableWidget.setItem(add,1,data)
            data=QtWidgets.QTableWidgetItem(num[5:])
            data.setTextAlignment(Qt.AlignHCenter) 
            tableWidget.setItem(add,2,data)
    def dec_to_signed_bin_16bit(self,num):
        binary = bin(abs(num))[2:]
        binary = binary.zfill(16)
        if num < 0:
            binary = ''.join(['1' if b == '0' else '0' for b in binary])
            binary = bin(int(binary, 2) + 1)[2:].zfill(16)
        return binary
    def hex_to_16bit_binary(self,hex_string):
        binary_string = bin(int(hex_string, 16))[2:]
        binary_string = binary_string.zfill(16)
        return binary_string
    def debug(self):
        micro_operation = str(self.control_memory[int(self.CAR, 2)])
        if micro_operation[0:6] == "100101":
            self.TMP = self.AC
            self.AC = self.DR
            self.DR = self.TMP
        else:
            if micro_operation[0:3] == "000":     # NOP
                pass
            elif micro_operation[0:3] == "001":     # ADD
                self.AC = str(bin(int(self.AC, 2) + int(self.DR, 2))[2:].zfill(16))
            elif micro_operation[0:3] == "010":     # CLRAC
                self.AC = "0" * 16
            elif micro_operation[0:3] == "011":     # INCAC
                self.AC = str(bin(int(self.AC, 2) + 1)[2:].zfill(16))
            elif micro_operation[0:3] == "100":     # DRTAC
                self.AC = self.DR
            elif micro_operation[0:3] == "101":     # DRTAR
                self.AR = self.DR[5:16]
            elif micro_operation[0:3] == "110":     # PCTAR
                self.AR = self.PC
            elif micro_operation[0:3] == "111":     # WRITE
                self.RAM[int(self.AR, 2)] = self.DR
            if micro_operation[3:6] == "000":     # NOP
                pass
            elif micro_operation[3:6] == "001":     # SUB
                self.AC = str(bin(int(self.AC, 2) - int(self.DR, 2))[2:].zfill(16))
            elif micro_operation[3:6] == "010":     # OR
                self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) | bin(int(self.DR, 2))[2:].zfill(16))
            elif micro_operation[3:6] == "011":     # AND
                self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) & bin(int(self.DR, 2))[2:].zfill(16))
            elif micro_operation[3:6] == "100":     # READ
                self.DR = str(self.RAM[int(self.AR, 2)])
            elif micro_operation[3:6] == "101":     # ACTDR
                self.DR = self.AC
            elif micro_operation[3:6] == "110":     # INCDR
                self.DR = str(bin(int(self.DR, 2) + 1)[2:].zfill(16))
            elif micro_operation[3:6] == "111":     # PCTDR
                self.DR = self.DR[:5] + self.PC
        if micro_operation[6:9] == "000":     # NOP
            pass
        elif micro_operation[6:9] == "001":     # XOR
            self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) ^ bin(int(self.DR, 2))[2:].zfill(16))
        elif micro_operation[6:9] == "010":     # COM
            self.AC = str(~int(self.AC, 2) & 0b1111111111111111)[2:].zfill(16)
        elif micro_operation[6:9] == "011":     # SHL
            self.AC = str(bin(int(self.AC, 2) << 1)[2:].zfill(16))
        elif micro_operation[6:9] == "100":     # SHR
            self.AC = str(bin(int(self.AC, 2) >> 1)[2:].zfill(16))
        elif micro_operation[6:9] == "101":     # INCPC
            self.PC = str(bin(int(self.PC, 2) + 1)[2:].zfill(11))
        elif micro_operation[6:9] == "110":     # ARTPC
            self.PC = self.AR
        elif micro_operation[6:9] == "111":     # RES
            pass
        if micro_operation[9:11] == "00":     # U -> always
            if micro_operation[11:13] == "00":
                self.CAR = micro_operation[13:20]   #AD
            elif micro_operation[11:13] == "01":
                self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                self.CAR = micro_operation[13:20]   #AD
            elif micro_operation[11:13] == "10":
                self.CAR = self.SBR
            elif micro_operation[11:13] == "11":
                if self.DR[1:5] == "1111": #HLT
                    print("HLT")
                    message_box = QMessageBox()
                    message_box.setWindowTitle('Error Box')
                    message_box.setText("Debug is finished")
                    response = message_box.exec()
                self.CAR = "0" + self.DR[1:5] + "00"

        elif micro_operation[9:11] == "01":     # I -> indirect
            if self.DR[0] == "1":
                if micro_operation[11:13] == "00":
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "01":
                    self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "10":
                    self.CAR = self.SBR
                elif micro_operation[11:13] == "11":
                    if self.DR[1:5] == "1111": #HLT
                        print("HLT")
                        message_box = QMessageBox()
                        message_box.setWindowTitle('Error Box')
                        message_box.setText("Debug is finished")
                        response = message_box.exec()
                    self.CAR = "0" + self.DR[1:5] + "00"
            else:
                if micro_operation[11:13] == "00":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "01":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "10":
                    pass
                elif micro_operation[11:13] == "11":
                    pass

        elif micro_operation[9:11] == "10":     # S negative
            if self.AC[0] == "1":
                if micro_operation[11:13] == "00":
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "01":
                    self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "10":
                    self.CAR = self.SBR
                elif micro_operation[11:13] == "11":
                    if self.DR[1:5] == "1111": #HLT
                        print("HLT")
                        message_box = QMessageBox()
                        message_box.setWindowTitle('Error Box')
                        message_box.setText("Debug is finished")
                        response = message_box.exec()
                    self.CAR = "0" + self.DR[1:5] + "00"
            else:
                if micro_operation[11:13] == "00":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "01":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "10":
                    pass
                elif micro_operation[11:13] == "11":
                    pass

        elif micro_operation[9:11] == "11":     # zero
            if self.AC == "0000000000000000":
                if micro_operation[11:13] == "00":
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "01":
                    self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "10":
                    self.CAR = self.SBR
                elif micro_operation[11:13] == "11":
                    if self.DR[1:5] == "1111": #HLT
                        print("HLT")
                        message_box = QMessageBox()
                        message_box.setWindowTitle('Error Box')
                        message_box.setText("Debug is finished")
                        response = message_box.exec()
                    self.CAR = "0" + self.DR[1:5] + "00"
            else:
                if micro_operation[11:13] == "00":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "01":
                    self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                elif micro_operation[11:13] == "10":
                    pass
                elif micro_operation[11:13] == "11":
                    pass
        self.ac.setText('AC:'+self.AC)
        self.dr.setText('DR:'+self.DR)
        self.pc.setText('PC:'+self.PC)
        self.ar.setText('AR:'+self.AR)
        self.car.setText('CAR:'+self.CAR)
        self.sbr.setText('SBR:'+self.AC)
        

    def execute(self):
        self.CAR = str( bin(64)[2:].zfill(7) )
        while True:
            micro_operation = str(self.control_memory[int(self.CAR, 2)])
            if micro_operation[0:6] == "100101":
                self.TMP = self.AC
                self.AC = self.DR
                self.DR = self.TMP
            else:
                if micro_operation[0:3] == "000":     # NOP
                    pass
                elif micro_operation[0:3] == "001":     # ADD
                    self.AC = str(bin(int(self.AC, 2) + int(self.DR, 2))[2:].zfill(16))
                elif micro_operation[0:3] == "010":     # CLRAC
                    self.AC = "0" * 16
                elif micro_operation[0:3] == "011":     # INCAC
                    self.AC = str(bin(int(self.AC, 2) + 1)[2:].zfill(16))
                elif micro_operation[0:3] == "100":     # DRTAC
                    self.AC = self.DR
                elif micro_operation[0:3] == "101":     # DRTAR
                    self.AR = self.DR[5:16]
                elif micro_operation[0:3] == "110":     # PCTAR
                    self.AR = self.PC
                elif micro_operation[0:3] == "111":     # WRITE
                    self.RAM[int(self.AR, 2)] = self.DR
                if micro_operation[3:6] == "000":     # NOP
                    pass
                elif micro_operation[3:6] == "001":     # SUB
                    self.AC = str(bin(int(self.AC, 2) - int(self.DR, 2))[2:].zfill(16))
                elif micro_operation[3:6] == "010":     # OR
                    self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) | bin(int(self.DR, 2))[2:].zfill(16))
                elif micro_operation[3:6] == "011":     # AND
                    self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) & bin(int(self.DR, 2))[2:].zfill(16))
                elif micro_operation[3:6] == "100":     # READ
                    self.DR = str(self.RAM[int(self.AR, 2)])
                elif micro_operation[3:6] == "101":     # ACTDR
                    self.DR = self.AC
                elif micro_operation[3:6] == "110":     # INCDR
                    self.DR = str(bin(int(self.DR, 2) + 1)[2:].zfill(16))
                elif micro_operation[3:6] == "111":     # PCTDR
                    self.DR = self.DR[:5] + self.PC
            if micro_operation[6:9] == "000":     # NOP
                pass
            elif micro_operation[6:9] == "001":     # XOR
                self.AC = str(bin(int(self.AC, 2))[2:].zfill(16) ^ bin(int(self.DR, 2))[2:].zfill(16))
            elif micro_operation[6:9] == "010":     # COM
                self.AC = str(~int(self.AC, 2) & 0b1111111111111111)[2:].zfill(16)
            elif micro_operation[6:9] == "011":     # SHL
                self.AC = str(bin(int(self.AC, 2) << 1)[2:].zfill(16))
            elif micro_operation[6:9] == "100":     # SHR
                self.AC = str(bin(int(self.AC, 2) >> 1)[2:].zfill(16))
            elif micro_operation[6:9] == "101":     # INCPC
                self.PC = str(bin(int(self.PC, 2) + 1)[2:].zfill(11))
            elif micro_operation[6:9] == "110":     # ARTPC
                self.PC = self.AR
            elif micro_operation[6:9] == "111":     # RES
                pass
            if micro_operation[9:11] == "00":     # U -> always
                if micro_operation[11:13] == "00":
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "01":
                    self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    self.CAR = micro_operation[13:20]   #AD
                elif micro_operation[11:13] == "10":
                    self.CAR = self.SBR
                elif micro_operation[11:13] == "11":
                    if self.DR[1:5] == "1111": #HLT
                        print("HLT")
                        break
                    self.CAR = "0" + self.DR[1:5] + "00"

            elif micro_operation[9:11] == "01":     # I -> indirect
                if self.DR[0] == "1":
                    if micro_operation[11:13] == "00":
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "01":
                        self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "10":
                        self.CAR = self.SBR
                    elif micro_operation[11:13] == "11":
                        if self.DR[1:5] == "1111": #HLT
                            print("HLT")
                            break
                        self.CAR = "0" + self.DR[1:5] + "00"
                else:
                    if micro_operation[11:13] == "00":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "01":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "10":
                        pass
                    elif micro_operation[11:13] == "11":
                        pass

            elif micro_operation[9:11] == "10":     # S negative
                if self.AC[0] == "1":
                    if micro_operation[11:13] == "00":
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "01":
                        self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "10":
                        self.CAR = self.SBR
                    elif micro_operation[11:13] == "11":
                        if self.DR[1:5] == "1111": #HLT
                            print("HLT")
                            break
                        self.CAR = "0" + self.DR[1:5] + "00"
                else:
                    if micro_operation[11:13] == "00":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "01":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "10":
                        pass
                    elif micro_operation[11:13] == "11":
                        pass

            elif micro_operation[9:11] == "11":     # zero
                if self.AC == "0000000000000000":
                    if micro_operation[11:13] == "00":
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "01":
                        self.SBR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                        self.CAR = micro_operation[13:20]   #AD
                    elif micro_operation[11:13] == "10":
                        self.CAR = self.SBR
                    elif micro_operation[11:13] == "11":
                        if self.DR[1:5] == "1111": #HLT
                            print("HLT")
                            break
                        self.CAR = "0" + self.DR[1:5] + "00"
                else:
                    if micro_operation[11:13] == "00":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "01":
                        self.CAR = str(bin(int(self.CAR,2) + 1)[2:].zfill(7))
                    elif micro_operation[11:13] == "10":
                        pass
                    elif micro_operation[11:13] == "11":
                        pass
        self.ac.setText('AC:'+self.AC)
        self.dr.setText('DR:'+self.DR)
        self.pc.setText('PC:'+self.PC)
        self.ar.setText('AR:'+self.AR)
        self.car.setText('CAR:'+self.CAR)
        self.sbr.setText('SBR:'+self.AC)
                

    def get_program(self):
        text=self.textEdit.toPlainText()
        self.commandList = text.split('\n')
        self.commandList=list(filter(None, self.commandList))
        for command in self.commandList:
            if "ORG" in command:
                startAdd=command[4:]
                startAdd=int(startAdd)
                self.PC=self.dec_to_signed_bin_16bit(startAdd)
            if "," in command:
                index=command.find(',')
                lable=command[0:index]
                self.labels[lable]=self.commandList.index(command)
        output_string = ' '.join(self.commandList)
        def send_alert(message):
            message_box = QMessageBox()
            message_box.setWindowTitle('Error Box')
            message_box.setText(message)
            response = message_box.exec()
        if "ORG" not in output_string:
            send_alert("You didn't input the start address")
        elif "END" not in output_string:
            send_alert("You didn't input the endpoint ")
        elif "HLT" not in output_string:
            send_alert("You didn't input HLT")
        index =self.commandList.index('HLT')
        for c in range(index+1,len(self.commandList)):
            if "DEC" in self.commandList[c]:
                num = [int(d) for d in re.findall(r'-?\d+', self.commandList[c])]
                num = ''.join(str(e) for e in num)
                num=int(num)
                num=self.dec_to_signed_bin_16bit(num)
                self.set_program_in_memory(self.tableWidget,num,(startAdd+c-2))
                self.RAM[startAdd+c-1].i=num[0]
                self.RAM[startAdd+c-1].opcode=num[1:5]
                self.RAM[startAdd+c-1].add=num[5:]
            elif "HEX" in self.commandList[c]:
                result = self.commandList[c].split()
                num=result[-1]
                num=self.hex_to_16bit_binary(num)
                self.set_program_in_memory(self.tableWidget,num,(startAdd+c-2))
                self.RAM[startAdd+c-1].i=num[0]
                self.RAM[startAdd+c-1].opcode=num[1:5]
                self.RAM[startAdd+c-1].add=num[5:]
        for c in range(1,index+1):
            result = self.commandList[c].split()
            if result[0]=="ADD":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0000"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0000"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="BRANCH":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0001"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0001"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="STORE":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0010"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0010"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="EXCHANGE":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0011"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0011"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="LOAD":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0100"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0100"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="AND":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0101"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0101"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            elif result[0]=="ADM":
                    if result[-1]=="I":
                        self.RAM[startAdd+c-1].i="1"
                        self.RAM[startAdd+c-1].opcode="0111"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
                    else:
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="0111"
                        num=self.dec_to_signed_bin_16bit((self.labels[result[1]]+startAdd-1))
                        self.RAM[startAdd+c-1].add=num[-11:]
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))

            elif result[0]=="HLT":
                        self.RAM[startAdd+c-1].i="0"
                        self.RAM[startAdd+c-1].opcode="1111"
                        self.RAM[startAdd+c-1].add="00000000001"
                        data=self.RAM[startAdd+c-1].i+self.RAM[startAdd+c-1].opcode+self.RAM[startAdd+c-1].add
                        self.set_program_in_memory(self.tableWidget,data,(startAdd+c-2))
            else:
                    send_alert(f"You entered an invalid command! at line: {c}")

app=QtWidgets.QApplication(sys.argv)
mywindow=Myclass()
sys.exit(app.exec_())
