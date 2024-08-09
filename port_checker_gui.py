import os
import socket
import sys
from functools         import cache
from PySide6.QtCore    import QSize, Qt
from PySide6.QtGui     import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QRadioButton, QWidget
from requests          import get
from time              import sleep
from threading         import Thread

if getattr(sys, 'frozen', False):
    import pyi_splash

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


IP = ''

@cache
def get_local_ip() -> str :
    global IP
    localhost = socket.gethostname()
    IP = socket.gethostbyname(localhost)
    return IP

@cache
def get_public_ip() -> str :
    global IP
    IP = get('https://api.ipify.org').content.decode('utf8')
    return IP

def test_port(self, ip, port, result = 1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        r = s.connect_ex((ip, port))

        if r == 0: 
            result = r 
        s.close() 

    except Exception as e:
        self.feedback_label.setText(f'An exception has occured!\n{e}')
        pass

    return result

get_public_ip()
get_local_ip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Port Checker")
        self.setFixedSize(QSize(400, 300))
        icon = QIcon(resource_path("./assets/icon.png"))
        self.setWindowIcon(icon)

        self.local_ip_rb = QRadioButton("Use Your Local IPV4")
        self.local_ip_rb.toggle()
        self.local_ip_rb.toggled.connect(self.set_ip_field)
        self.public_ip_rb = QRadioButton("Use Your Public IPV4")
        self.public_ip_rb.toggled.connect(self.set_ip_field)
        self.custom_ip_rb = QRadioButton("Custom IPV4")
        self.custom_ip_rb.toggled.connect(self.set_ip_field)
        self.ip_txt = QLabel("IP Address:")
        self.ip_input = QLineEdit()
        self.ip_input.setText(IP)
        self.ip_input.setInputMask(None)
        self.ip_input.setEnabled(False)
        self.port_txt = QLabel("Port N°:")
        self.port_input = QLineEdit()
        self.port_input.setInputMethodHints(Qt.InputMethodHint.ImhPreferNumbers | Qt.InputMethodHint.ImhDigitsOnly)
        self.port_input.setInputMask('00000;')
        self.port_input.returnPressed.connect(self.check_port)
        self.test_btn = QPushButton("Check")
        self.test_btn.pressed.connect(self.probe_thread)
        self.feedback_label = QLabel()

        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.addWidget(self.local_ip_rb, 0, 0)
        layout.addWidget(self.public_ip_rb, 0, 1)
        layout.addWidget(self.custom_ip_rb, 0, 2)
        layout.addWidget(self.ip_txt, 1, 0)
        layout.addWidget(self.ip_input, 2, 0, 2, 3)
        layout.addWidget(self.port_txt, 4, 0)
        layout.addWidget(self.port_input, 6, 0)
        layout.addWidget(self.test_btn, 8, 0)
        layout.addWidget(self.feedback_label, 10, 0, 10, -1)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
    
    def set_ip_field(self):
        global IP
        if self.custom_ip_rb.isChecked():
            self.ip_input.setText("")
            self.ip_input.setInputMask('000.000.000.000;_')
            self.ip_input.setEnabled(True)
            self.ip_input.returnPressed.connect(self.check_ipAddr)
            # self.ip_input.textEdited.connect(self.check_ipAddr)
            IP = (self.ip_input.displayText()).replace('_', '')
        elif self.local_ip_rb.isChecked():
            IP = get_local_ip()
            self.ip_input.setText(IP)
            self.ip_input.setInputMask(None)
            self.ip_input.setEnabled(False)
        elif self.public_ip_rb.isChecked():
            IP = get_public_ip()
            self.ip_input.setText(IP)
            self.ip_input.setInputMask(None)
            self.ip_input.setEnabled(False)

    def check_ipAddr(self) -> bool:
        global IP
        IP = ((self.ip_input.displayText()).replace('_', ''))
        stack_1, stack_2, stack_3, stack_4 = (IP.split('.'))
        try:
            if 0 < int(stack_1) <= 255:
                if int(stack_2) <= 255 and int(stack_3) <= 255 and int(stack_4) <= 255:
                    self.feedback_label.setText(f'✅ Valid IP ( {IP} )')
                    return True
                else:
                    self.feedback_label.setText('❌ Invalid IP address!')
                    return False
            else:
                self.feedback_label.setText('❌ Invalid IP address!')
        except ValueError:
            self.feedback_label.setText('Please enter an IP address.')

    def check_port(self) -> bool:
        if self.port_input.displayText() != '':
            try:
                port_num = int((self.port_input.displayText()).replace(' ', ''))
                if 0 < port_num <= 65535:
                    return True
                else:
                    return False
            except ValueError:
                self.feedback_label.setText('Please enter a valid port number.')

    def probe_port(self):
        try:
            if self.check_port():
                port_num = int((self.port_input.displayText()).replace(' ', ''))
                self.feedback_label.setText(f'Testing {IP}:{port_num}')
                sleep(1)
                response = test_port(self, IP, port_num)
                if response == 0:
                    self.feedback_label.setText(f'✅ Probe successful. Port {port_num} is open.')
                else:
                    self.feedback_label.setText(f'❌ It seems like port {port_num} is closed.')
            else:
                self.feedback_label.setText('Please enter a port number!')
        except ValueError:
            self.feedback_label.setText('Please enter a port number!')
            pass
    
    def probe_thread(self):
        Thread(target = self.probe_port, daemon = True).start()


app    = QApplication([])
window = MainWindow()
window.show()

if getattr(sys, 'frozen', False):
    pyi_splash.close()


if __name__ == '__main__':
    app.exec()