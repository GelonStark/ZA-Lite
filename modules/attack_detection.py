import time
import pydirectinput
from loguru import logger
from shared import status
from utils.screenshot import screenshot
from ultralytics import YOLO
import threading


class AttackDetection:
    def __init__(self,model):
        self.model=model
        self.thread=threading.Thread(target=self.detector,daemon=True)
        self.event=threading.Event()

    def detector(self):
        """攻击检测"""
        logger.trace("【线程启动】攻击检测")
        while True:
            self.event.wait()
            t1 = time.perf_counter()
            result = self.model(source=screenshot("bgr"), imgsz=320, show=False,verbose=False)  #此处错误使用BGR截图进行推理，但实际运行置信度反而比正确使用RGB高
            #print('攻击检测耗时:',time.perf_counter()-t1)

            for box in result[0].boxes:

                if box.conf > 0.95:
                    pydirectinput.press('space')
                    status.under_attack=True # 受到攻击 共享变量
                    break
    def start(self):
        if not self.thread.is_alive():
            self.thread.start()
            self.event.set()
        else:
            self.event.set()
    def stop(self):
        self.event.clear()

if __name__=="__main__":
    yolo_attack = YOLO('../assets/models/ZA_3295.pt').to('cpu')
    AttackDetection(yolo_attack).start()
    input("working")