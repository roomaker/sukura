import sys

import dialog
from biotry import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QElapsedTimer, QCoreApplication, QRegExp
from PyQt5.QtGui import *

global Schannal
global pla_cha
global impedance
Schannal = 0
pla_cha = [0 for i in range(64)]
impedance = ["0" for k in range(64)]


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


class ImpDialog(QDialog, dialog.Ui_dialog):  # 继承类

    dialogSignal = pyqtSignal(int, str)                   # 传输阻抗数据信号
    plateSignal = pyqtSignal(int, int, int)              # 传输电镀通道信号

    def __init__(self, arg=None):
        super(ImpDialog, self).__init__(arg)
        self.setupUi(self)
        reg = QRegExp("^-?(12|1?[0-1]?(\\.\\d{1,2})?|\\d(\\.\\d{1,2})?)$")
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)
        self.lineEdit_2.setValidator(validator)
        self.model = QStandardItemModel(32, 4)
        self.model.setHorizontalHeaderLabels(['通道', '阻抗', '通道', '阻抗'])
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setAttribute(Qt.WA_QuitOnClose, False)  # 给子窗口设置这个可以保证主窗口关闭同时子窗口也关闭
        for row in range(32):
            for column in range(1):
                item = QStandardItem('通道%s' % (row + 1))
                # 设置每个位置的文本值
                self.model.setItem(row, column, item)

        for row in range(32):
            for column in range(1):
                item = QStandardItem('通道%s' % (row + 33))
                # 设置每个位置的文本值
                self.model.setItem(row, column + 2, item)
            # 实例化表格视图，设置模型为自定义的模型

        self.tableView.setItemDelegateForColumn(0, EmptyDelegate(self))
        self.tableView.setItemDelegateForColumn(2, EmptyDelegate(self))

        self.dialogSignal.connect(self.getdata)
        self.savebutton.clicked.connect(self.save_data)
        self.platebutton.clicked.connect(self.plating_channels)

    def getdata(self, parameter1, parameter2):
        global Schannal
        if parameter1 < 32:
            item = QStandardItem('%s' % parameter2)
            impedance[parameter1] = parameter2
            if self.checkBox.isChecked() == 1:
                if float(parameter2) > float(self.lineEdit.text()):
                    item.setBackground(QColor('Yellow'))
                    pla_cha[Schannal] = parameter1
                    Schannal = Schannal + 1
            self.model.setItem(parameter1, 1, item)

        if 31 < parameter1 < 64:
            item = QStandardItem('%s' % parameter2)
            impedance[parameter1] = parameter2
            if self.checkBox.isChecked() == 1:
                if float(parameter2) > float(self.lineEdit.text()):
                    item.setBackground(QColor('Yellow'))
                    pla_cha[Schannal] = parameter1
                    Schannal = Schannal + 1
            self.model.setItem(parameter1-32, 3, item)

        if parameter1 > 63:
            pass

        # 清空当前值
        if parameter1 == 300:                      # 在控制界面按下start按键后传递的参数

            Schannal = 0

            for row in range(32):
                item = QStandardItem('')
                self.model.setItem(row, 1, item)

            for row in range(32):
                item = QStandardItem('')
                self.model.setItem(row, 3, item)

    def plating_channels(self):

        global pla_cha                                # 读取此前写入的数组

        t = QElapsedTimer()

        for gxs in range(64):                         # 轮询该数组

            if pla_cha[gxs] != 0:                     # 如果有非零的存在，即为记录下的通道

                self.plateSignal.emit(pla_cha[gxs]+1, int(round((int(self.lineEdit_2.text()) + 12)/0.00586)), int(int(self.spinBox.text())/100))

                t.start()

                while t.elapsed() < 1000 + int(self.spinBox.text()):

                    QCoreApplication.processEvents()

        pla_cha = [0 for i in range(64)]

    def save_data(self):

        filename, ok = QFileDialog.getSaveFileName(self, '满地都是六便士，你们却抬头看见了月亮🌙。------ 吴人冠寄语', 'C;/', "Txt files(*.txt)")
        if filename != "":
            with open(file=filename, mode='a+', encoding='utf-8') as file:
                for row in range(32):
                    file.write('通道%s:   ' % (row + 1)+impedance[row] + '      通道%s:   ' % (row + 33) + impedance[row+32]+ "\n")
                file.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # w = Win()
    window = ImpDialog()
    window.show()
    sys.exit(app.exec_())
