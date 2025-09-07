import shutil
import os

def copy_file(src_list, dst_folder):
    """
    批量复制文件到目标文件夹
    若已经存在则覆盖
    :param src_list: 源文件路径列表 (list[str])
    :param dst_folder: 目标文件夹路径 (str)
    """
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    for src in src_list:
        if os.path.isfile(src):
            try:
                filename = os.path.basename(src)
                dst_path = os.path.join(dst_folder, filename)
                shutil.copy2(src, dst_path)
                print(f"已复制: {src} -> {dst_path}")
            except Exception as e:
                print(f"复制失败: {src} -> {dst_path} {e}")
        else:
            print(f"文件不存在: {src}")

if __name__ == "__main__":
    src_files = [
        r"D:\code\python\报销助手\导出的文件\办公用品 100.00 20250907.pdf",
        r"D:\code\python\报销助手\导出的文件\办公用品 100.00 20250907.pdf"
    ]
    dst_dir = r"D:\code\python\报销助手\导出的文件\test"

    copy_file(src_files, dst_dir)
