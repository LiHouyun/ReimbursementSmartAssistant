import os
import sys

from PyQt6.QtGui import QDoubleValidator, QIcon
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QHeaderView, QCheckBox, QTableWidgetItem, QGridLayout, QFileDialog, QLabel
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
        # 打开系统文件资源管理器
        file_path, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "所有文件 (*.*);;文本文件 (*.txt);;图像文件 (*.png *.jpg)"
        )
        if file_path:
            self.main_layout.import_file_table.setRowCount(0)
            self.main_layout.import_file_table.setRowCount(len(file_path))
            for row, file_name in enumerate(file_path):
                self.set_table_row(row, file_name.split('/')[-1])
    
    def set_table_row(self, row, file_name):
        """填充单元格"""
        table_header_labels_zh = ['文件名']

        self.main_layout.import_file_table.setHorizontalHeaderLabels(table_header_labels_zh)
        self.main_layout.import_file_table.setColumnCount(len(table_header_labels_zh))
        
        self.main_layout.import_file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents) # 根据内容自动调整列宽
        self.main_layout.import_file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 第二列自动拉伸
        
        item = QTableWidgetItem(str(file_name))
        self.main_layout.import_file_table.setItem(row, 0, item)   # 把 Item 填充进单元格
