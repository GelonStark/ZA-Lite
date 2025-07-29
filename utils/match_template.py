import pyautogui
import pydirectinput
import time
import cv2
from loguru import logger
import numpy
#------------------------------------------------------
from shared import status
from utils.screenshot import screenshot
from config.load_config import timeout_round,skip_round,action_speed,wait_speed
#---------------------------------------------------------------------------------------------
def match_tpl(tpl,action=None,key=None,skip=None,reverse=None):
    rounds=0 #重置超时计数
    while True:

        template = cv2.imread(tpl)  # 读取模板
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)  #模板BGR转灰度图
        screenshot_gray = cv2.cvtColor(screenshot("rgb"), cv2.COLOR_RGB2GRAY)  # 屏幕截图RGB转灰度图

        result=cv2.matchTemplate(screenshot_gray,template_gray,cv2.TM_CCOEFF_NORMED)     #进行匹配
        min_val, max_val, min_loc, max_loc=cv2.minMaxLoc(result)    #解包minMaxLoc

        if action == "match":
            if max_val > 0.9 :
                return max_val,max_loc   #返回 置信度 坐标
            else:
                return False

        rounds += 1                # 由于行为 match 是单次匹配，超时判断逻辑必须写在match后面
        if rounds > timeout_round:
            status.timeout = True
            logger.error('等待超时,开始重试')
        if status.timeout:
            return # 用于其他模块导入判断超时  #这里原本是return True 我忘了这个True是干什么的，可能有用，可能是BUG，先删了

        if max_val > 0.9 :
            logger.trace(f'【目标出现】{tpl} 置信度：{max_val}')

            if action== 'click' :
                pyautogui.moveTo(max_loc)
                time.sleep(action_speed)
                pyautogui.click()
                time.sleep(wait_speed)
                break

            if action == 'move':
                pyautogui.moveTo(max_loc)
                time.sleep(wait_speed)
                return max_loc

            if action == 'scroll_move':
                pyautogui.moveTo(max_loc)
                time.sleep(wait_speed)
                break

            if action =='press':
                time.sleep(action_speed)
                pydirectinput.press(key)
                time.sleep(wait_speed)
                break
            if action=="check":
                return max_loc

        else:
            if skip :
                if rounds > skip_round :
                    logger.trace(f'【跳过】{tpl}')
                    break

            if action=='scroll_move':
                if reverse:
                    pyautogui.scroll(1)
                else:
                    pyautogui.scroll(-1)

            logger.trace(f'【{rounds}】等待目标中 {tpl}')
            time.sleep(wait_speed)
def click(tpl,skip=None):
    match_tpl(tpl,'click',skip=skip)
def press(tpl,key,skip=None):
    match_tpl(tpl,'press',key,skip=skip)
def move(tpl,skip=None):
    return match_tpl(tpl,'move',skip=skip)
def scroll_move(tpl,skip=None,reverse=None):
    match_tpl(tpl,'scroll_move',skip=skip,reverse=reverse)
def match(tpl):
    return match_tpl(tpl,'match')

def traversal_tpl(tpl,skip=None):
    """用于检测单帧出现多个相同目标，遍历点击"""
    rounds = 0
    while True:
        rounds += 1
        if rounds > 50 :  # 超时
            status.timeout = True
            logger.error('--------等待超时,开始重试--------')
        if status.timeout:
            break
        template = cv2.imread(tpl)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot("rgb"), cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.9 :
            logger.trace(f'【开始遍历】{tpl} 置信度是：{max_val}')        #用于出现多个相同的模板场景，对目标出现的单帧进行遍历获取位置

            array_y,array_x=numpy.where(result > 0.8) #对矩阵进行置信度筛选,矩阵由(y1,y2...)(x1,x2...)组成
            coord=zip(array_x,array_y) #使用zip将可迭代对象打包，zip只有在遍历时会产生数据

            repeat_times=0
            last_x,last_y=None,None

            for target in coord:
                x,y=target

                if (last_x is None) or (not last_x-20 < x < last_x+20 or not last_y-20 < y < last_y+20) :
                    repeat_times += 1
                    pyautogui.moveTo(x, y)
                    time.sleep(action_speed)
                    pydirectinput.click()
                    time.sleep(wait_speed)
                    last_x, last_y = x, y

                else:
                    logger.trace(f'【距离过近】跳过 {x,y}')

            logger.trace(f'【遍历结束】{tpl} 次数:{repeat_times}')
            break
        else:
            if skip :
                if rounds > 40 :  # 跳过轮数
                    logger.trace(f'【跳过】{tpl}')
                    break
            logger.trace(f'【{rounds}】等待目标中 {tpl}')
            time.sleep(0.1)

if __name__=='__main__':
    traversal_tpl(r"C:\Users\gelon\Pictures\Screenshots\33.png")

