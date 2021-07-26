import biomega2
from imp import *
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

global channeling                                                                           # 阻抗测试中的通道
global current_process_state                                                                # 当前程序处于的界面标志
global imp_receive                                                                          # 阻抗界面允许接收透传标志
global man_state                                                                            # 控制界面状态区分标志位
global man_receive                                                                          # 控制界面允许接收透传标志
global ele_receive                                                                          # 电镀界面允许接收透传标志
channeling = 0                                                                              # 默认阻抗测试通道从0开始
current_process_state = "控制"                                                              # 默认控制界面
imp_receive = "停止"                                                                        # 默认阻抗界面不允许接收透传
man_state = "阻抗"                                                                          # 默认控制界面
man_receive = "停止"                                                                        # 默认控制界面不允许接收透传
ele_receive = "停止"


class Win(QMainWindow, biomega2.Ui_MainWindow):                                             # 主窗口，继承MainWindow

    def __init__(self):
        super().__init__()
        self.com = QSerialPort()                                                            # 新建一个串口类，用于与下位机通讯
        self.setupUi(self)                                                                  # 执行类中的setupUi函数

        # 界面切换
        self.ELEButton.clicked.connect(self.change_to_ele)                                  # 切换至电镀界面
        self.IMPButton.clicked.connect(self.change_to_imp)                                  # 切换至阻抗界面
        self.MANButton.clicked.connect(self.change_to_man)                                  # 切换至控制界面

        # 电镀界面
        self.horizontalSlider.sliderMoved.connect(self.ele_slider_control)                  # 链接滑动条与槽函数

        # 控制界面
        self.Imp_radioButton.clicked.connect(self.radio_imp)                                # 阻抗选择按钮
        self.Ele_radioButton.clicked.connect(self.radio_ele)                                # 电镀选择按钮
        self.horizontalSlider_2.sliderMoved.connect(self.man_slider_control)                # 滑动条

        # 开始按钮
        self.StartButton.clicked.connect(self.everything_possible)
        # 取消按钮
        self.CancelButton.clicked.connect(self.cancel_operation)

        # 底部菜单
        self.ScanButton.clicked.connect(self.scan_port)
        self.OpenButton.clicked.connect(self.open_device)

        # 接收数据
        self.com.readyRead.connect(self.receive_data)

        #接收另一个窗口发回的信号
        ImpDialog.plateSignal.connect(self.plating_select)

    # 切换至电镀界面
    def change_to_ele(self):
        global current_process_state, imp_receive, channeling
        current_process_state = "电镀"                                               # 设置程序状态为电镀
        self.stackedWidget.setCurrentIndex(0)                                        # 切换当前显示的页面
        imp_receive = "停止"                                                         # 停止接收阻抗数据
        channeling = 0                                                               # 阻抗通道计数清零
        ImpDialog.dialogSignal.emit(300, "与君初相识，犹如故人归")                   # 清空阻抗界面的所有值
        ImpDialog.close()                                                            # 关闭阻抗弹窗
        self.lcdNumber.display(str(round(0, 3)))                                     # 清空控制模式阻抗值显示

    # 切换至阻抗界面
    def change_to_imp(self):
        global current_process_state
        self.lcdNumber.display(str(round(0, 3)))                                     # 清空控制模式阻抗值显示
        current_process_state = "阻抗"                                               # 设置程序状态为阻抗
        self.stackedWidget.setCurrentIndex(1)                                        # 切换当前显示的页面
        self.label_16.setText(str(0))
        # ImpDialog.plateSignal.connect(self.plating_select)
        ImpDialog.show()                                                             # 显示阻抗窗口

    # 切换至控制界面
    def change_to_man(self):
        global current_process_state, imp_receive, channeling
        current_process_state = "控制"                                               # 设置程序状态为控制
        self.stackedWidget.setCurrentIndex(2)                                        # 切换当前显示的页面
        imp_receive = "停止"                                                         # 停止接收阻抗数据
        channeling = 0                                                               # 阻抗通道计数清零
        ImpDialog.dialogSignal.emit(300, "与君初相识，犹如故人归")                   # 清空阻抗界面的所有值
        self.label_16.setText(str(0))
        ImpDialog.close()                                                            # 关闭阻抗弹窗

    # 电镀界面

    # 滑动条
    def ele_slider_control(self):
        ele_value = self.horizontalSlider.value() - 2048                             # 将滑动条的值减去2048 ，以归零电流值
        a0 = str(round(0.00586 * ele_value, 2))                                      # 将滑动条的值转换为电流值
        self.label_12.setText(a0)                                                    # 显示电流值

    # 控制界面

    def radio_imp(self):
        global man_state
        man_state = "阻抗"                                                           # 将控制模式中的状态置为阻抗

    def radio_ele(self):
        global man_state
        man_state = "电镀"                                                           # 将控制模式中的状态置为电镀

    # 滑动条
    def man_slider_control(self):
        man_value = self.horizontalSlider_2.value() - 2048                           # 同上一滑动条，为控制模式中的滑动条
        a1 = str(round(0.00586 * man_value, 2))
        self.label_21.setText(a1)

    # 底部菜单（done）

    # 扫描串口（done）
    def scan_port(self):
        self.comboBox_3.clear()                                                      # 清除上一次扫描到的串口
        self.DeviceButton.setChecked(0)                                              # 重置设备连接状态
        port_numb = QSerialPortInfo.availablePorts()                                 # 获取可用串口数据
        for info in port_numb:
            strings = info.portName()
            self.comboBox_3.addItem(strings)                                         # 将串口名称填入相应选择框内

    # 打开串口(done)
    def open_device(self):

        self.com.setBaudRate(QSerialPort.Baud115200)                                 # 设置串口参数
        self.com.setDataBits(QSerialPort.Data8)
        self.com.setStopBits(QSerialPort.OneStop)
        self.com.setParity(QSerialPort.NoParity)
        self.com.setPortName(self.comboBox_3.currentText())                          # 打开当前选择的串口
        self.com.open(QSerialPort.ReadWrite)
        if self.com.isOpen():                                                        # 如果成功打开串口，即认为成功连接设备
            self.DeviceButton.setChecked(1)
        gg = [0xff, 0x11, 0xee, 0xff, 0xaa, 0xaa, 0xaa, 0xaa]                        # 第三位为EE，打开串口时初始化一下机器，不然会不响应信号（bug）

        self.com.write(bytes(gg))

    # 接收数据（doing）

    def receive_data(self):
        global imp_receive, man_receive, ele_receive
        global channeling

        gg = self.com.readAll()                                                       # 读取串口数据

        if current_process_state == "阻抗":                                           # 处于阻抗模式下收到数据

            if gg == b"\xcc\xaa\xcc":                                                 # 收到结束指令时停止刷新数据
                imp_receive = "停止"
                channeling = 0                                                        # 阻抗通道计数清零
                print("停止")

            if imp_receive == "开始":                                                 # 在标志位为开始的情况下，将下位机传来的阻抗数据直接显示
                ImpDialog.dialogSignal.emit(channeling, str(round(gg.toFloat()[0], 3)))     # 向阻抗窗口发射信号，将通道以及阻抗数据递交
                channeling = channeling + 1                                           # 每次进行之后通道数+1

            if gg == b"\xcc\xaa\xbb":                                                 # 收到开始指令后将标志位置位
                imp_receive = "开始"
                channeling = 0

        if current_process_state == "电镀":                                           # 等待添加当前电镀通道显示

            if gg == b"\xcc\xbb\xcc":

                ele_receive = "停止"

            if ele_receive == "开始":

                self.label_16.setText(str(gg.toInt()[0]))

            if gg == b"\xcc\xcc\xcc":

                ele_receive = "开始"

            # print(ele_receive)

        if current_process_state == "控制":

            if gg == b"\xcc\xaa\xcc":

                man_receive = "停止"

                # self.lcdNumber.display(str(round(0, 3)))

            if man_receive == "开始":

                self.lcdNumber.display(str(round(gg.toFloat()[0], 3)))                 # 每收到一次数据就刷新一次显示

            if gg == b"\xaa\xcc\xaa":

                man_receive = "开始"

    # 开始按键

    def everything_possible(self):
        global channeling
        global current_process_state
        global man_state
        global imp_receive
        if current_process_state == "阻抗":

            imp_receive = "停止"

            ImpDialog.dialogSignal.emit(300, "与君初相识，犹如故人归")          # 清空阻抗界面的所有值

            channeling = 0  # 阻抗通道计数清零

            if self.AdaptorBox.currentText() == "No Adaptor":  # 如果没有选择适配器，即按原始的通道定义来
                gg = [0xff, 0xa1, 0xbb, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]  # 此处第三位向下位机反馈电极模式
            if self.AdaptorBox.currentText() == "MMA-32":  # 32通道电极
                gg = [0xff, 0xa2, 0xbb, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
            if self.AdaptorBox.currentText() == "MMA-64":  # 64通道电极
                gg = [0xff, 0xa3, 0xbb, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
            if self.AdaptorBox.currentText() == "Prof.Dr.Lu":  # 卢老师专供电极，40通道
                gg = [0xff, 0xa4, 0xbb, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]

            self.com.write(bytes(gg))

        if current_process_state == "电镀":

            self.label_16.setText(str(0))

            if self.AdaptorBox.currentText() == "No Adaptor":  # 如果没有选择适配器，即按原始的通道定义来
                gg = [0xff, 0xa1, 0xcc, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]  # 此处第三位向下位机反馈电极模式
            if self.AdaptorBox.currentText() == "MMA-32":  # 32通道电极
                gg = [0xff, 0xa2, 0xcc, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
            if self.AdaptorBox.currentText() == "MMA-64":  # 64通道电极
                gg = [0xff, 0xa3, 0xcc, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
            if self.AdaptorBox.currentText() == "Prof.Dr.Lu":  # 卢老师专供电极，40通道
                gg = [0xff, 0xa4, 0xcc, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]

            gg[3] = int(self.during_time.value()/100)                           # 持续时间注意这里改成了毫秒

            gg[4] = self.pause_time.value()                                     # 暂停时间

            linshi = self.horizontalSlider.value()                              # 将进度条的值赋拆分高低八位

            gg[5] = (linshi >> 8) & 0xff

            gg[6] = linshi & 0xff

            self.com.write(bytes(gg))                                           # 向下位机发送数据

        if current_process_state == "控制":

            if man_state == "阻抗":

                if self.AdaptorBox.currentText() == "No Adaptor":  # 如果没有选择适配器，即按原始的通道定义来
                    gg = [0xff, 0xa1, 0xdd, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]  # 此处第三位向下位机反馈电极模式
                if self.AdaptorBox.currentText() == "MMA-32":  # 32通道电极
                    gg = [0xff, 0xa2, 0xdd, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
                if self.AdaptorBox.currentText() == "MMA-64":  # 64通道电极
                    gg = [0xff, 0xa3, 0xdd, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]
                if self.AdaptorBox.currentText() == "Prof.Dr.Lu":  # 卢老师专供电极，40通道
                    gg = [0xff, 0xa4, 0xdd, 0xff, 0xbb, 0xbb, 0xbb, 0xbb]

                gg[4] = int(self.comboBox_4.currentText())                      # 选择通道

                self.com.write(bytes(gg))

            if man_state == "电镀":

                if self.AdaptorBox.currentText() == "No Adaptor":  # 如果没有选择适配器，即按原始的通道定义来
                    gg = [0xff, 0xa1, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]  # 此处第三位向下位机反馈电极模式
                if self.AdaptorBox.currentText() == "MMA-32":  # 32通道电极
                    gg = [0xff, 0xa2, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]
                if self.AdaptorBox.currentText() == "MMA-64":  # 64通道电极
                    gg = [0xff, 0xa3, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]
                if self.AdaptorBox.currentText() == "Prof.Dr.Lu":  # 卢老师专供电极，40通道
                    gg = [0xff, 0xa4, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]

                gg[4] = int(self.comboBox_4.currentText())                      # 选择通道

                nidie = self.horizontalSlider_2.value()                         # 将进度条的值赋拆分高低八位

                gg[5] = (nidie >> 8) & 0xff

                gg[6] = nidie & 0xff

                gg[7] = int(self.man_during_time.value() / 100)                 # 需要设置单次的电镀时间

                self.com.write(bytes(gg))

    # 取消按键
    def cancel_operation(self):
        gg = [0xff, 0x11, 0xee, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]                   # 第三位为EE，下位机即进行初始化
        self.com.write(bytes(gg))

    #接收标记通道并进行电镀
    def plating_select(self, par1, par2, par3):

        if self.AdaptorBox.currentText() == "No Adaptor":  # 如果没有选择适配器，即按原始的通道定义来
            gg = [0xff, 0xa1, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]  # 此处第三位向下位机反馈电极模式
        if self.AdaptorBox.currentText() == "MMA-32":  # 32通道电极
            gg = [0xff, 0xa2, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]
        if self.AdaptorBox.currentText() == "MMA-64":  # 64通道电极
            gg = [0xff, 0xa3, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]
        if self.AdaptorBox.currentText() == "Prof.Dr.Lu":  # 卢老师专供电极，40通道
            gg = [0xff, 0xa4, 0xdd, 0x00, 0xbb, 0xbb, 0xbb, 0xbb]

        gg[4] = int(par1)

        gg[5] = (int(par2) >> 8) & 0xff

        gg[6] = int(par2) & 0xff

        gg[7] = int(par3)

        self.com.write(bytes(gg))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ImpDialog = ImpDialog()
    w = Win()
    w.show()
    # ImpDialog.plateSignal.connect(w.plating_select)
    sys.exit(app.exec_())
