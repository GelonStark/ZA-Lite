import cv2
import pyautogui
import numpy
from loguru import logger

def screenshot(screenshot_type=None):
    if screenshot_type not in ["rgb","bgr","gray"]:
        logger.error("未填写正确的图片格式类型")
        raise ValueError
    ss = pyautogui.screenshot()  # 屏幕截图
    screenshot_rgb = numpy.array(ss)  # 屏幕截图PIL.Image转Numpy数组 是RGB！但是cv2默认使用BGR，imshow肉眼看到的颜色是反的
    screenshot_bgr = cv2.cvtColor(screenshot_rgb, cv2.COLOR_RGB2BGR) # RGB转BGR
    screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY) # BGR转GRAY
    if screenshot_type == "rgb": # RGB
        return screenshot_rgb
    if screenshot_type == "bgr": # BGR
        return  screenshot_bgr
    if screenshot_type == "gray": # BGR2GRAY
        return screenshot_gray

if __name__=="__main__":

    cv2.imshow("123",screenshot("gray"))
    cv2.waitKey(0)