import time
import win32gui
import win32con
import subprocess
from loguru import logger
import threading
from utils import logger_init

def window_check(title_cn,title_en="0",arg_path=None,config_path=None):
    """检查目标窗口是否存在，若存在便激活，若不存在则启动游戏"""
    if arg_path is None: # 如果没有填写游戏路径
        path=config_path # 用配置文件路径
        if config_path is None:  # 当两个路径都没有时，跳过启动环节
            path = None
    else:
        path=arg_path

    exist = False

    foreground=win32gui.GetForegroundWindow()  #当前处于焦点的窗口
    if not foreground:
        logger.error("无法获取HWND")
        return
    target_cn=win32gui.FindWindow(None,title_cn)  # HWND不存在时为0
    target_en=win32gui.FindWindow(None,title_en)


    if target_cn != 0: # 如果目标HWND存在
        target=target_cn
        exist=True
    if target_en != 0:
        target=target_en
        exist=True
    if exist:
        #logger.trace(f'发现已存在的游戏窗口:{title_cn}')
        if foreground == target :
            #logger.trace("窗口处于前台")
            pass
        else:
            #win32con.SW_HIDE        # 隐藏窗口
            #win32con.SW_SHOW        # 显示窗口
            #win32con.SW_MINIMIZE    # 最小化
            #win32con.SW_RESTORE     # 从最小化恢复
            #win32con.SW_MAXIMIZE    # 最大化

            # logger.trace("窗口未激活，尝试恢复窗口")
            win32gui.ShowWindow(target, win32con.SW_MINIMIZE)
            win32gui.ShowWindow(target, win32con.SW_RESTORE)
            #win32gui.SetForegroundWindow(target)

    else:
        logger.debug(f"目标窗口“{title_cn}”不存在")
        if path is not None:
            logger.debug(f"启动游戏：{path}")
            try:
                subprocess.Popen(
                    f'{path} -popupwindow -screen-width 1920 -screen-height 1080 -screen-fullscreen 0')  # 启动参数 无边框 窗口化
                return
            except OSError as e:
                logger.error(e)
                logger.error("启动游戏失败，请检查路径")
                input()
                return

class WindowKeeper:
    def __init__(self,title_cn,title_en="0"):
        self.title_cn=title_cn
        self.title_en=title_en
        self.thread=threading.Thread(target=self.keeper)
        self.event = threading.Event()
    def keeper(self):
        """保持窗口处于前端"""
        logger.trace("【线程启动】窗口保持")
        while True:
            time.sleep(10)
            window_check(self.title_cn,self.title_en)
    def start(self):
        if not self.thread.is_alive():
            self.thread.start()
            self.event.set()
        else:
            self.event.set()
    def stop(self):
        self.event.clear()

if __name__ == "__main__":

    WindowKeeper("绝区零","zenlesszonezero").start()
