import os
from PyQt6.QtWidgets import QTableWidget, QToolTip, QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt, QPoint, QEvent
from qfluentwidgets import TableWidget, PushButton

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
                background-color: rgba(255, 255, 255, 240);
                border: 2px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            
            # 设置缩放矩阵
            matrix = fitz.Matrix(1.2, 1.2)
            pix = page.get_pixmap(matrix=matrix)
            
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
            
            # 限制预览图片的最大尺寸
            max_width = 400
            max_height = 500
            if pixmap.width() > max_width or pixmap.height() > max_height:
                pixmap = pixmap.scaled(
                    max_width, 
                    max_height, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
            
            # 显示图片
            self.image_label.setPixmap(pixmap)
            
            # 调整窗口大小和位置
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
        
    def set_file_paths(self, file_paths):
        """设置文件路径列表"""
        self.file_path_list = file_paths
        
    def add_preview_button(self, row):
        """在指定行添加预览按钮"""
        preview_btn = PushButton("预览")
        preview_btn.setFixedSize(60, 25)
        preview_btn.clicked.connect(lambda: self._on_preview_clicked(row, preview_btn))
        self.setCellWidget(row, 2, preview_btn)  # 添加到第三列（索引2）
        
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
