import os
import sys

from PyQt6.QtCore import pyqtSignal, QRegularExpression, Qt
from PyQt6.QtGui import QDoubleValidator, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout,  QWidget, QHeaderView, QCheckBox, QTableWidgetItem, QGridLayout, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout, QButtonGroup, QTableWidget
from qfluentwidgets import PushButton, SearchLineEdit, CardWidget, TableWidget, setCustomStyleSheet, InfoBar, LineEdit, StrongBodyLabel, ComboBox, RadioButton

# 引入文件夹路径
relative_path = '..\\'
current_file_path = os.path.dirname(__file__)
utils_folder_path = os.path.abspath(os.path.join(current_file_path, relative_path))
sys.path.append(utils_folder_path)

from config.cfg import CLASS_LIST
from utils.custom_style import EXPORT_BUTTON_STYLE
from utils.pdf_previewer import PdfPreviewerTableWidget

class MainLayout(QWidget):

    import_file_signal = pyqtSignal()
    extract_name_signal = pyqtSignal()
    rename_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.set_rename_layout()
        self.set_export_layout()

    def set_rename_layout(self):
        self.rename_layout = QHBoxLayout()
        self.rename_layout.setContentsMargins(0, 0, 0, 0)
        self.rename_layout.setSpacing(0)
        self.main_layout.addLayout(self.rename_layout)

        self.set_origin_file_layout()
        self.set_rename_file_layout()

    def set_origin_file_layout(self):
        origin_file_layout = QVBoxLayout()
        origin_file_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        origin_file_layout.setContentsMargins(0, 0, 0, 0)
        origin_file_layout.setSpacing(10)
        self.rename_layout.addLayout(origin_file_layout)

        import_file_ctrl_layout = QHBoxLayout()
        import_file_ctrl_layout.setContentsMargins(0, 0, 0, 0)
        import_file_ctrl_layout.setSpacing(5)
        # 左对齐
        import_file_ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        origin_file_layout.addLayout(import_file_ctrl_layout)

        import_file_btn = PushButton(text='导入文件')
        import_file_btn.setFixedSize(100, 30)
        import_file_ctrl_layout.addWidget(import_file_btn)
        import_file_btn.clicked.connect(self.emit_import_file_signal)
        
        extract_name_btn = PushButton(text='提取文件名')
        extract_name_btn.setFixedSize(100, 30)
        import_file_ctrl_layout.addWidget(extract_name_btn)
        extract_name_btn.clicked.connect(self.emit_extract_name_signal)

        self.import_file_table = PdfPreviewerTableWidget()
        # 禁用 第二列的编辑功能
        self.import_file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        origin_file_layout.addWidget(self.import_file_table)

    def set_rename_file_layout(self):
        rename_file_layout = QVBoxLayout()
        rename_file_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        rename_file_layout.setContentsMargins(0, 0, 0, 0)
        rename_file_layout.setSpacing(10)
        self.rename_layout.addLayout(rename_file_layout)

        rename_file_ctrl_layout = QHBoxLayout()
        rename_file_ctrl_layout.setContentsMargins(0, 0, 0, 0)
        rename_file_ctrl_layout.setSpacing(5)
        # 左对齐
        rename_file_ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        rename_file_layout.addLayout(rename_file_ctrl_layout)

        rename_btn = PushButton(text='重命名')
        rename_btn.setFixedSize(100, 30)
        rename_file_ctrl_layout.addWidget(rename_btn)
        rename_btn.clicked.connect(self.emit_rename_signal)

        rename_rd_btn1 = RadioButton('直接重命名')
        rename_rd_btn2 = RadioButton('另存后重命名')
        # 将单选按钮添加到互斥的按钮组
        self.button_group = QButtonGroup()
        self.button_group.addButton(rename_rd_btn1)
        self.button_group.addButton(rename_rd_btn2)
        rename_rd_btn1.setChecked(True)
        rename_rd_btn_layout = QHBoxLayout()
        rename_rd_btn_layout.addWidget(rename_rd_btn1)
        rename_rd_btn_layout.addWidget(rename_rd_btn2)
        rename_file_ctrl_layout.addLayout(rename_rd_btn_layout)

        self.rename_file_table = TableWidget()
        rename_file_layout.addWidget(self.rename_file_table)

    def set_export_layout(self):
        self.export_layout = QHBoxLayout()
        self.export_layout.setContentsMargins(0, 0, 0, 0)
        self.export_layout.setSpacing(0)
        self.main_layout.addLayout(self.export_layout)

        export_file_btn = PushButton(text='导出文件')
        export_file_btn.setStyleSheet(EXPORT_BUTTON_STYLE)
        export_file_btn.setFixedSize(100, 30)
        self.export_layout.addWidget(export_file_btn)

    def emit_import_file_signal(self):
        self.import_file_signal.emit()

    def emit_extract_name_signal(self):
        self.extract_name_signal.emit()

    def emit_rename_signal(self):
        is_save_as = (self.button_group.checkedButton().text() == '另存后重命名')
        self.rename_signal.emit(is_save_as)
