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

# 预览按钮样式 - 无边框，文字有下划线
PREVIEW_BUTTON_STYLE = """
QPushButton {
    border: none;
    background-color: transparent;
    color: #007acc;
    text-decoration: underline;
    font-size: 14px;
    padding: 5px;
}
QPushButton:hover {
    color: #005a9a;
    background-color: rgba(0, 122, 204, 0.1);
    border-radius: 3px;
}
QPushButton:pressed {
    color: #003d66;
    background-color: rgba(0, 122, 204, 0.2);
}
"""

# 删除按钮样式 - 与预览按钮相同，但使用红色
DELETE_BUTTON_STYLE = """
QPushButton {
    border: none;
    background-color: transparent;
    color: #dc3545;
    text-decoration: underline;
    font-size: 14px;
    padding: 5px;
}
QPushButton:hover {
    color: #c82333;
    background-color: rgba(220, 53, 69, 0.1);
    border-radius: 3px;
}
QPushButton:pressed {
    color: #a71e2a;
    background-color: rgba(220, 53, 69, 0.2);
}
"""
