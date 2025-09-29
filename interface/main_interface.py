import os
import sys

from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem, QFileDialog, QComboBox, QDialog
from qfluentwidgets import InfoBarPosition, InfoBarIcon, PushButton, SearchLineEdit, CardWidget, TableWidget, setCustomStyleSheet, InfoBar, LineEdit, StrongBodyLabel, ComboBox, Dialog

# 引入文件夹路径
relative_path = '..\\'
current_file_path = os.path.dirname(__file__)
utils_folder_path = os.path.abspath(os.path.join(current_file_path, relative_path))
sys.path.append(utils_folder_path)

from layout.main_layout import MainLayout
from config.cfg import *
from utils.pdf import extract_invoice_info
from utils.batch_rename import batch_rename, format_rename_message
from utils.copy_file import copy_file

class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_layout = MainLayout()
        self.setCentralWidget(self.main_layout)
        self.setWindowTitle(UI['WINDOWS_NAME'])
        self.setWindowIcon(QIcon('./resource/icon/1.svg'))

        self.import_file_path_list = [] # 导入的文件路径 list
        self.import_file_name_list = [] # 导入的文件名 list
        self.invoice_num_list = []
        self.output_folder_path = '' # 输出文件夹路径
        self.output_file_path_list = [] # 输出文件路径 list
        self.output_file_name_list = [] # 输出文件名 list

        self.main_layout.import_file_signal.connect(self.import_file)
        self.main_layout.extract_name_signal.connect(self.extract_name)
        self.main_layout.rename_signal.connect(self.rename)

    def import_file(self):
        # 打开系统文件资源管理器
        self.import_file_path_list, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "PDF 文件 (*.pdf)"
        )
        self.import_file_name_list = [file_path.split('/')[-1] for file_path in self.import_file_path_list]

        if self.import_file_path_list:
            self.main_layout.import_file_table.setRowCount(0)
            self.main_layout.import_file_table.setRowCount(len(self.import_file_path_list))
            # 设置文件路径列表以启用PDF预览功能
            self.main_layout.import_file_table.set_file_paths(self.import_file_path_list)
            # 设置删除回调函数
            self.main_layout.import_file_table.set_delete_callback(self.delete_file_row)
            for row, file_name in enumerate(self.import_file_path_list):
                self.set_table_row(self.main_layout.import_file_table, row, 'class', file_name.split('/')[-1])

    def set_table_row(self, table, row, value1, value2):
        """填充单元格"""

        if table == self.main_layout.import_file_table:
            table_header_labels_zh = ['类别', '文件名', '预览', '删除']
            table.setHorizontalHeaderLabels(table_header_labels_zh)
            table.setColumnCount(len(table_header_labels_zh))

            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 固定宽度
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 自动拉伸
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 固定宽度
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 固定宽度

            # 设置列宽
            table.setColumnWidth(0, 100)  # 类别列
            table.setColumnWidth(2, 80)   # 预览按钮列
            table.setColumnWidth(3, 80)   # 删除按钮列
            
            font = QFont()
            font.setPointSize(10)      # 也可以用 .setPixelSize(18)
            class_comboBox = ComboBox()
            class_comboBox.addItems(CLASS_LIST)
            class_comboBox.setFont(font)
            table.setCellWidget(row, 0, class_comboBox)
        
            item = QTableWidgetItem(str(value2))
            table.setItem(row, 1, item)   # 把 Item 填充进单元格
            
            # 添加预览按钮
            table.add_preview_button(row)
            
            # 添加删除按钮
            table.add_delete_button(row)

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
        self.output_file_name_list = []
        for i, file_path in enumerate(self.import_file_path_list):
            print(file_path)
            try:
                info_all = extract_invoice_info(file_path)
                class_comboBox = self.main_layout.import_file_table.cellWidget(i, 0)
                class_text = class_comboBox.currentText()
                self.invoice_num_list.append(info_all['发票号码'])
                self.output_file_name_list.append(class_text + ' ' + info_all['价税合计']['小写'] + ' ' + info_all['开票日期'].replace('-', '')[4:8] + '.pdf')
            except Exception as e:
                print(f'[main_interface] extract name error: {e}')
                self.output_file_name_list.append(file_path.split('/')[-1].split('.')[0] + '-提取失败' + '.pdf')

        self.main_layout.rename_file_table.setRowCount(0)
        self.main_layout.rename_file_table.setRowCount(len(self.output_file_name_list))
        for row, new_name in enumerate(self.output_file_name_list):
            self.set_table_row(self.main_layout.rename_file_table, row, self.output_file_name_list[row], value2=None)

    def rename(self, is_save_as):
        print(f'[main_interface] rename: {is_save_as}')

        if not self.check_info():
            return

        if not self.import_file_path_list:
            return

        # 清空从 self.rename_file_table 第一列重新获取文件名
        self.output_file_name_list = []
        for i in range(self.main_layout.rename_file_table.rowCount()):
            self.output_file_name_list.append(self.main_layout.rename_file_table.item(i, 0).text())

        if is_save_as:
            self.output_folder_path = self.import_file_path_list[0].rsplit('/', 1)[0] + '/' + OUTPUT_FOLDER
            print(self.output_folder_path)
            copy_file(self.import_file_path_list, self.output_folder_path)

            self.output_file_path_list = [self.output_folder_path + '/' + file_name for file_name in self.import_file_name_list]

            rename_result_json = batch_rename(self.output_file_path_list, self.output_file_name_list)
            rename_result = format_rename_message(rename_result_json)
            InfoBar.info(
                title='提示',
                content=rename_result,
                orient=Qt.Orientation.Vertical,  # 内容太长时可使用垂直布局
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self.main_layout,
            )

            print(f'InfoBar - 提示 {rename_result}')

        else:
            self.output_file_path_list = self.import_file_path_list
            print(f'self.output_file_name_list, {self.output_file_name_list}')
            print(f'self.output_file_path_list, {self.output_file_path_list}')
            rename_result_json = batch_rename(self.output_file_path_list, self.output_file_name_list)
            rename_result = format_rename_message(rename_result_json)

            InfoBar.info(
                title='提示',
                content=rename_result,
                orient=Qt.Orientation.Vertical,  # 内容太长时可使用垂直布局
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self.main_layout,
            )
            print(f'InfoBar - 提示 {rename_result}')


    def check_info(self):
        # 是否含相同的发票号码
        # 因为有提取失败的

        from collections import defaultdict

        lst = self.invoice_num_list
        print(lst)
        idx_map = defaultdict(list)          # 值 → [索引列表]
        for i, v in enumerate(lst):
            idx_map[v].append(i)

        dup_idx = {v: idx for v, idx in idx_map.items() if len(idx) > 1}
        print(dup_idx)
        # → {'a': [0, 2, 5], 'b': [1, 4]}

        if dup_idx:

            dialog_info = ''
            for key, value in dup_idx.items():
                dialog_info += f'{key}: \n'
                for i in value:
                    dialog_info += f'{self.import_file_name_list[i]}\n'
            dialog_info += '\n'
            repeated_dialog = Dialog("有相同发票", dialog_info, self.main_layout)
            repeated_dialog.yesButton.setText("OK")
            repeated_dialog.cancelButton.setText("取消")

            if repeated_dialog.exec():
                print('OK')
            else:
                print('取消')

            return False
        else:
            return True

    def delete_file_row(self, row):
        """删除指定行的文件"""
        if 0 <= row < len(self.import_file_path_list):
            # 从文件路径列表中删除
            del self.import_file_path_list[row]
            del self.import_file_name_list[row]
            del self.invoice_num_list[row]
            if self.output_file_name_list:
                del self.output_file_name_list[row]
                self.main_layout.rename_file_table.setRowCount(0)
                self.main_layout.rename_file_table.setRowCount(len(self.output_file_name_list))
                for row, new_name in enumerate(self.output_file_name_list):
                    self.set_table_row(self.main_layout.rename_file_table, row, self.output_file_name_list[row], value2=None)
            
            # 更新表格显示
            self.main_layout.import_file_table.setRowCount(0)
            if self.import_file_path_list:
                self.main_layout.import_file_table.setRowCount(len(self.import_file_path_list))
                # 重新设置文件路径列表
                self.main_layout.import_file_table.set_file_paths(self.import_file_path_list)
                self.main_layout.import_file_table.set_delete_callback(self.delete_file_row)
                
                # 重新填充表格
                for i, file_name in enumerate(self.import_file_path_list):
                    self.set_table_row(self.main_layout.import_file_table, i, 'class', file_name.split('/')[-1])
