import os
import sys

from PyQt6.QtGui import QDoubleValidator, QIcon
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QHeaderView, QCheckBox, QTableWidgetItem, QGridLayout
from qfluentwidgets import InfoBarPosition, InfoBarIcon, PushButton, SearchLineEdit, CardWidget, TableWidget, setCustomStyleSheet, InfoBar, LineEdit, StrongBodyLabel, ComboBox

# 引入文件夹路径
relative_path = '..\\'
current_file_path = os.path.dirname(__file__)
utils_folder_path = os.path.abspath(os.path.join(current_file_path, relative_path))
sys.path.append(utils_folder_path)

from layout.main_layout import MainLayout
from config import cfg

class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_layout = MainLayout()
        self.setCentralWidget(self.main_layout)
        self.setWindowTitle(cfg.UI['WINDOWS_NAME'])
        self.setWindowIcon(QIcon('./resource/icon/1.svg'))

        self.main_layout.import_file_signal.connect(self.import_file)

    def import_file(self):
        print('[main_interface] import file')
