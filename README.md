pyinstaller -F -c app.py --name "报销助手-v1.0" --log-level=DEBUG --add-data "resource/*;resource"

来自网络 pyinstaller -F -w --icon=release.ico page.py -p "F:\Program Files\myProject\venv\Lib\site-packages"

pyinstaller -F -c app.py --name "报销助手-v1.0" --log-level=DEBUG --add-data "resource/*;resource"  -p "F:\Project\ReimbursementSmartAssistant\venv\lib\site-packages\PyQt6\__init__"
pyinstaller -F -c app.py --name "报销助手-v1.0" --log-level=DEBUG --add-data "resource/*;resource"  -p "F:\Project\ReimbursementSmartAssistant\venv\lib\site-packages"

先找到 PyQt6 的确切路径：`python -c "import PyQt6; print(PyQt6.__file__)"`

`F:\Project\ReimbursementSmartAssistant\venv\lib\site-packages\PyQt6\__init__`

rmdir /s /q build
rmdir /s /q dist
del "报销助手-v1.0.spec"

rmdir /s /q build
rmdir /s /q dist
del "报销助手-v1.0.spec"

pyinstaller 报错未解决
改为使用 cx_Freeze
