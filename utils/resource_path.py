import os
import sys
import time

# 由于 ResourcePath 会在 OneFile 模式使用内置资源路径，所以外置资源请用 OneDir 模式打包！

class ResourcePath:
    def __init__(self, dir_path, marker_dir):
        self.dir_path = dir_path
        self.marker_dir = marker_dir
        self.onefile_mode=False

        if hasattr(sys, "_MEIPASS"):    # 打包后 以exe文件位置为起点
            self.BASE_DIR = sys.executable
            if os.path.dirname(sys.executable) != os.path.dirname(sys._MEIPASS): #exe位置和_MEIPASS文件夹(onedir模式为_internal)的上一层文件夹不同 则不是文件夹模式
                self.onefile_mode=True      #是onefile模式
        else:
            self.BASE_DIR = __file__  # 打包前 以py文件位置为起点
        self.root_path = self.top_dir()

    def top_dir(self):
        current_dir = self.BASE_DIR
        while True:
            marker_path = os.path.join(current_dir, self.marker_dir)
            if os.path.exists(marker_path):
                #print('【根目录】',current_dir)
                return current_dir
            else:
                current_dir = os.path.dirname(current_dir)
                if current_dir == os.path.dirname(current_dir):
                    print("找不到顶层目录")
                    raise FileNotFoundError

    def file(self, file_name):
        """拼接 文件名"""
        if self.onefile_mode:
            #print("【单文件模式】",os.path.join(sys._MEIPASS,self.dir_path,file_name))
            return os.path.join(sys._MEIPASS,self.dir_path,file_name)
        if self.root_path is not None:
            res_path = os.path.join(self.root_path, self.dir_path, file_name)
            #print('【资源路径】',res_path)
            return res_path

    def path(self, full_path):
        """拼接 完整路径"""
        if self.onefile_mode:
            return os.path.join(sys._MEIPASS,full_path)
        if self.root_path is not None:
            res_path = os.path.join(self.root_path, full_path)
            return res_path


if __name__ == "__main__":
    rpih = ResourcePath("images/hollow", "config")
    rpih.file("123.png")
    input()

