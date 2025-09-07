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

from config.cfg import CLASS_LIST, UI
from layout.main_layout import MainLayout
from utils.pdf import extract_invoice_info

class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_layout = MainLayout()
        self.setCentralWidget(self.main_layout)
        self.setWindowTitle(UI['WINDOWS_NAME'])
        self.setWindowIcon(QIcon('./resource/icon/1.svg'))

        self.file_path_list = []

        self.main_layout.import_file_signal.connect(self.import_file)
        self.main_layout.extract_name_signal.connect(self.extract_name)

    def import_file(self):
        # 打开系统文件资源管理器
        self.file_path_list, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "PDF 文件 (*.pdf)"
        )

        if self.file_path_list:
            self.main_layout.import_file_table.setRowCount(0)
            self.main_layout.import_file_table.setRowCount(len(self.file_path_list))
            for row, file_name in enumerate(self.file_path_list):
                self.set_table_row(self.main_layout.import_file_table, row, 'class', file_name.split('/')[-1])
    
    def set_table_row(self, table, row, value1, value2):
        """填充单元格"""

        if table == self.main_layout.import_file_table:
            table_header_labels_zh = ['类别', '文件名']
            table.setHorizontalHeaderLabels(table_header_labels_zh)
            table.setColumnCount(len(table_header_labels_zh))

            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # 自动拉伸
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # 根据内容自动调整列宽

            # 固定第一列的宽度
            table.setColumnWidth(0, 100)

            class_comboBox = ComboBox()
            class_comboBox.addItems(CLASS_LIST)
            table.setCellWidget(row, 0, class_comboBox)
        
            item = QTableWidgetItem(str(value2))
            table.setItem(row, 1, item)   # 把 Item 填充进单元格

        elif table == self.main_layout.rename_file_table:
            table_header_labels_zh = ['文件名']
            table.setHorizontalHeaderLabels(table_header_labels_zh)
            table.setColumnCount(len(table_header_labels_zh))

            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 根据内容自动调整列宽
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 自动拉伸

            item = QTableWidgetItem(str(value1))
            table.setItem(row, 0, item)   # 把 Item 填充进单元格

    def extract_name(self):
        print('[main_interface] extract name')
        new_name_list = []
        for i, file_path in enumerate(self.file_path_list):
            print(file_path)
            try:
                info_all = extract_invoice_info(file_path)
                class_comboBox = self.main_layout.import_file_table.cellWidget(i, 0)
                class_text = class_comboBox.currentText()
                new_name_list.append(class_text + ' ' + info_all['价税合计']['小写'] + ' ' + info_all['开票日期'].replace('-', '')[4:8] + '.pdf')
            except Exception as e:
                print(f'[main_interface] extract name error: {e}')
                new_name_list.append(file_path.split('/')[-1].split('.')[0] + '-提取失败' + '.pdf')

        self.main_layout.rename_file_table.setRowCount(0)
        self.main_layout.rename_file_table.setRowCount(len(new_name_list))
        for row, new_name in enumerate(new_name_list):
            self.set_table_row(self.main_layout.rename_file_table, row, new_name, value2=None)
