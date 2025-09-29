import os
import sys
from PySide6.QtWidgets import QApplication

# 引入文件夹路径
relative_path = '..\\'
current_file_path = os.path.dirname(__file__)
utils_folder_path = os.path.abspath(os.path.join(current_file_path, relative_path))
sys.path.append(utils_folder_path)

from interface.main_interface import MainInterface

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainInterface()
    window.setStyleSheet("MainInterface {background: white}")
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())
