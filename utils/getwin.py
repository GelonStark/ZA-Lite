
import pygetwindow
from loguru import logger
import time
import pyautogui
import subprocess

def getwin(zh_title=None,en_title=None,game_path=None,config_path=None):
    if game_path is None: # 如果没有填写游戏路径
        game_path=config_path # 用配置文件路径

    allwin = pygetwindow.getAllTitles()
    if zh_title in allwin or en_title in allwin:  #判断标题窗口是否存在
        if zh_title in allwin:
            title=zh_title
        if en_title in allwin:
            title=en_title
        targetwin = pygetwindow.getWindowsWithTitle(title)
        logger.debug('发现已存在的游戏窗口')
        time.sleep(2)
        try:
            pyautogui.hotkey('win', 'd')
            targetwin[0].activate()
            time.sleep(2)
            pyautogui.click(button='right')

        except pygetwindow.PyGetWindowException :
            pyautogui.hotkey('win', 'd')
            targetwin[0].activate()
            time.sleep(2)
            pyautogui.click(button='right')
    else:
        logger.debug(f'启动游戏：{game_path}')
        time.sleep(1)
        try:
            subprocess.Popen(f'{game_path} -popupwindow -screen-width 1920 -screen-height 1080 -screen-fullscreen 1') #启动参数
        except OSError as e:
            logger.error(e)
            logger.error("启动游戏失败，请检查路径")
            input()
            return
        while True:
            allwin = pygetwindow.getAllTitles()
            if en_title in allwin or zh_title in allwin:
                break
if __name__=="__main__":
    getwin(zh_title="绝区零",en_title="ZenlessZoneZero",game_path=r"D:\Game Files\Wuthering Waves\launcher.exe")