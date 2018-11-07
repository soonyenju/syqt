#!/usr/bin/env python  
#coding=utf-8  
"""
这个代码缩进是空格不是tab注意！
"""
from PyQt5.QtGui  import *  #目测table的类应该是在qt.gui里面的
from PyQt5.QtCore import *    
from PyQt5.QtWidgets import *
class MyDialog(QDialog):  
    def __init__(self, fieldlist, reclist, parent=None):  
        super(MyDialog, self).__init__(parent) 
        self.fld = fieldlist
        self.rclst = reclist
        self.MyTable = QTableWidget(len(self.rclst), len(self.fld))
        strf = []
        for i in range(len(self.fld)): 
            strf.append(str(self.fld[i])) 
        self.MyTable.setHorizontalHeaderLabels(strf)
        #self.MyTable.setHorizontalHeaderLabels(['Name','Height','Weight'])  
        for i in range(len(strf)):
            recname = strf[i]
            for j in range(len(self.rclst)):
                rec = self.rclst[j]
                value = str(rec[recname])
                newItem = QTableWidgetItem(value)
                self.MyTable.setItem(j, i, newItem) 

        # example:
        # newItem = QTableWidgetItem("syj")  
        # self.MyTable.setItem(0, 0, newItem)  
          
        # newItem = QTableWidgetItem("10cm")  
        # self.MyTable.setItem(0, 1, newItem)  
          
        # newItem = QTableWidgetItem("60g")  
        # self.MyTable.setItem(0, 2, newItem)   
        
        layout = QHBoxLayout()  
        layout.addWidget(self.MyTable)  
        self.setLayout(layout)      
          
          
if __name__ == '__main__':  
    """
    直接执行不可，缺少必要参数，还需要集成其他函数
    """
    import sys  
    app = QApplication(sys.argv)  
    myWindow = MyDialog(fieldlist = None, reclist = None)  
    myWindow.show()  
    sys.exit(app.exec_())      
