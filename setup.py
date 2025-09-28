import sys
from cx_Freeze import setup, Executable

# 1. 要打包的Python脚本路径
script = "app.py"

# 2. 不在运行程序的时候出现cmd后台框
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

# 3. 创建可执行文件的配置
exe = Executable(
    script=script,
    base=base,
    target_name="报销助手-v1.0", # 自定义
    icon='./resource/icon/1.svg' # 自定义
)

# 4. 打包的参数配置
options = {
    "build_exe": {
        "packages": [],
        "excludes": []
    }
}

setup(
    name="报销助手-v1.0", # 自定义
    version="1.0", # 自定义
    description="报销助手-重命名", # 自定义
    options=options,
    executables=[exe]
)
