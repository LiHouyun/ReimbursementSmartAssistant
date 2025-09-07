# 通用按钮样式
BUTTON_STYLE = """
QPushButton {
    border: none;
    padding: 5px 10px;
    font-family: 'Seqoe UI', 'Microsoft YaHei';
    font-size: 14px;
    color: white;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.1);
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.2);
}
"""

SEARCH_BUTTON_STYLE = BUTTON_STYLE + """
QPushButton {
    background-color: #0d6efd;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
"""

LOGIN_BUTTON_STYLE = BUTTON_STYLE + """
QPushButton {
    background-color: #0d6efd;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
"""

REGISTER_BUTTON_STYLE = BUTTON_STYLE + """
QPushButton {
    background-color: #0d6efd;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
"""

EXPORT_BUTTON_STYLE = BUTTON_STYLE + """
QPushButton {
    background-color: #4CAF50;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:pressed {
    background-color: #45a080;
}
"""
