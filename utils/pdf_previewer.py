import os
from PySide6.QtWidgets import QToolTip, QWidget, QLabel, QVBoxLayout, QApplication, QTableWidget, QPushButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QPoint, QEvent
from qfluentwidgets import TableWidget, PushButton

from utils.custom_style import PREVIEW_BUTTON_STYLE, DELETE_BUTTON_STYLE

# 尝试导入PyMuPDF，如果失败则禁用预览功能
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("警告: PyMuPDF未安装，PDF预览功能将被禁用。请运行 'pip install PyMuPDF' 来启用此功能。")

class PdfPreviewWindow(QWidget):
    """PDF预览悬浮窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 250);
                border: 2px solid #666;
                border-radius: 10px;
            }
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 2px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 设置标签属性以优化图像显示
        self.image_label.setScaledContents(False)  # 不自动缩放内容
        self.image_label.setMinimumSize(100, 100)
        layout.addWidget(self.image_label)
        
        # 安装事件过滤器以监听鼠标点击
        QApplication.instance().installEventFilter(self)
        
    def show_pdf_preview(self, pdf_path, button_pos):
        """显示PDF预览"""
        if not PYMUPDF_AVAILABLE:
            self.image_label.setText("PDF预览功能需要安装PyMuPDF\n请运行: pip install PyMuPDF")
            self.resize(300, 100)
            self.move(button_pos)
            self.show()
            return
            
        try:
            # 打开PDF文档
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                self.image_label.setText("PDF文件为空")
                self.resize(200, 100)
                self.move(button_pos)
                self.show()
                return
            
            # 获取第一页
            page = doc[0]
            
            # 设置更高的缩放矩阵以提高清晰度
            # 2.5 表示2.5倍放大，可以显著提高清晰度
            matrix = fitz.Matrix(2.5, 2.5)
            # 使用高质量渲染参数
            pix = page.get_pixmap(
                matrix=matrix, 
                alpha=False,  # 不需要透明通道，提高性能
                annots=True,  # 包含注释
                clip=None     # 不裁剪
            )
            
            # 转换为QImage
            img = QImage(
                pix.samples, 
                pix.width, 
                pix.height, 
                pix.stride, 
                QImage.Format.Format_RGB888
            )
            
            # 转换为QPixmap
            pixmap = QPixmap.fromImage(img)
            
            # 限制预览图片的最大尺寸，增加最大尺寸以显示更多细节
            max_width = 600
            max_height = 700
            if pixmap.width() > max_width or pixmap.height() > max_height:
                # 使用高质量的平滑变换算法
                pixmap = pixmap.scaled(
                    max_width, 
                    max_height, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
            
            # 为高DPI显示器优化
            device_pixel_ratio = QApplication.primaryScreen().devicePixelRatio()
            if device_pixel_ratio > 1.0:
                pixmap.setDevicePixelRatio(device_pixel_ratio)
            
            # 显示图片
            self.image_label.setPixmap(pixmap)
            
            # 调整窗口大小和位置，考虑设备像素比
            if device_pixel_ratio > 1.0:
                actual_width = int(pixmap.width() / device_pixel_ratio)
                actual_height = int(pixmap.height() / device_pixel_ratio)
                self.resize(actual_width, actual_height)
            else:
                self.resize(pixmap.size())
            
            # 计算窗口位置，确保不超出屏幕边界
            screen = QApplication.primaryScreen().geometry()
            x = button_pos.x()
            y = button_pos.y()
            
            # 如果窗口会超出屏幕右边界，向左调整
            if x + self.width() > screen.right():
                x = screen.right() - self.width() - 10
            
            # 如果窗口会超出屏幕下边界，向上调整
            if y + self.height() > screen.bottom():
                y = button_pos.y() - self.height() - 10
            
            self.move(x, y)
            self.show()
            
            # 关闭文档
            doc.close()
            
        except Exception as e:
            self.image_label.setText(f"预览失败: {str(e)}")
            self.resize(300, 100)
            self.move(button_pos)
            self.show()
    
    def eventFilter(self, obj, event):
        """事件过滤器，监听全局鼠标点击"""
        if event.type() == QEvent.Type.MouseButtonPress:
            # 如果点击的不是预览窗口内部，则隐藏窗口
            if self.isVisible() and not self.geometry().contains(event.globalPosition().toPoint()):
                self.hide()
        return super().eventFilter(obj, event)

class PdfPreviewerTableWidget(TableWidget):
    """带PDF预览功能的表格组件"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path_list = []  # 存储文件路径列表
        self.preview_window = PdfPreviewWindow()  # 预览窗口
        self.delete_callback = None  # 删除回调函数
        
    def set_file_paths(self, file_paths):
        """设置文件路径列表"""
        self.file_path_list = file_paths
        
    def set_delete_callback(self, callback):
        """设置删除回调函数"""
        self.delete_callback = callback
        
    def add_preview_button(self, row):
        """在指定行添加预览按钮"""
        preview_btn = PushButton("预览")
        preview_btn.setFixedSize(60, 25)
        preview_btn.setStyleSheet(PREVIEW_BUTTON_STYLE)  # 应用自定义样式
        preview_btn.clicked.connect(lambda: self._on_preview_clicked(row, preview_btn))
        self.setCellWidget(row, 2, preview_btn)  # 添加到第三列（索引2）
        
    def add_delete_button(self, row):
        """在指定行添加删除按钮"""
        delete_btn = PushButton("删除")
        delete_btn.setFixedSize(60, 25)
        delete_btn.setStyleSheet(DELETE_BUTTON_STYLE)  # 应用自定义样式
        delete_btn.clicked.connect(lambda: self._on_delete_clicked(row))
        self.setCellWidget(row, 3, delete_btn)  # 添加到第四列（索引3）
        
    def _on_preview_clicked(self, row, button):
        """预览按钮点击事件"""
        try:
            if row < len(self.file_path_list):
                pdf_path = self.file_path_list[row]
                
                # 检查文件是否存在
                if not os.path.exists(pdf_path):
                    QToolTip.showText(button.mapToGlobal(QPoint(0, 0)), "文件不存在", self)
                    return
                
                # 获取按钮的全局位置
                button_global_pos = button.mapToGlobal(QPoint(button.width(), 0))
                
                # 显示预览窗口
                self.preview_window.show_pdf_preview(pdf_path, button_global_pos)
                
        except Exception as e:
            QToolTip.showText(button.mapToGlobal(QPoint(0, 0)), f"无法预览: {e}", self)
            
    def _on_delete_clicked(self, row):
        """删除按钮点击事件"""
        if self.delete_callback:
            self.delete_callback(row) 
