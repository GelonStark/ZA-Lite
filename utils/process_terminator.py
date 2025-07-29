from loguru import logger
import time
import keyboard
import os
import threading

class ProcessTerminator:
    def __init__(self):
        self.thread=threading.Thread(target=self.handler,daemon=True)

    def handler(self):
        """终止按键监听"""
        logger.trace("【线程启动】终止监听")
        t1=time.perf_counter()
        while True:
            time.sleep(0.01)
            t2=time.perf_counter()
            if keyboard.is_pressed('alt') or t2-t1 > 86400 : #24小时
                os._exit(0)
    def start(self):
        if not self.thread.is_alive():
            self.thread.start()

if __name__=="__main__":
    a=ProcessTerminator()
    a.start()
    input()