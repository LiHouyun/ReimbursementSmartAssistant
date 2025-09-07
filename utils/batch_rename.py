import os

def batch_rename(src_list, new_name_list):
    """
    批量重命名文件
    :param src_list: 原文件路径列表 (list[str])
    :param new_name_list: 新文件名列表 (list[str])，长度需与 src_list 一致
    """
    if len(src_list) != len(new_name_list):
        raise ValueError("源文件列表和新文件名列表长度不一致！")

    for src, new_name in zip(src_list, new_name_list):
        if not os.path.isfile(src):
            print(f"文件不存在: {src}")
            continue

        folder = os.path.dirname(src)              # 文件所在目录
        dst = os.path.join(folder, new_name)       # 新路径

        os.rename(src, dst)
        print(f"已重命名: {src} -> {dst}")

if __name__ == "__main__":
    src_files = [
        r"/path/to/file1.txt",
        r"/path/to/file2.jpg",
        r"/path/to/file3.pdf"
    ]

    new_names = [
        "new1.txt",
        "new2.jpg",
        "new3.pdf"
    ]

    batch_rename(src_files, new_names)
