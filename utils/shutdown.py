import time
import subprocess
from loguru import logger

def shutdown(index):
    if index==0:
        pass
    if index==1:
        logger.debug('游戏在30秒后关闭')
        time.sleep(30)
        subprocess.run('taskkill /IM ZenlessZoneZero.exe /F')
    if index==2:
        logger.debug('系统在30秒后关机')
        time.sleep(30)
        subprocess.run('shutdown /s /t 0')