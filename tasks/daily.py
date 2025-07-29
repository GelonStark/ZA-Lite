import cv2
import numpy
import pyautogui
import pydirectinput
import time
import pygetwindow
import easyocr
import threading
import traceback
import os
from ultralytics import YOLO
from loguru import logger
import ctypes
#-------------------------------------------------------
# import utils.logger_init # IDE自动删除
# import utils.excepthook
import utils.logger_init
import utils.excepthook
from shared import status
from modules.attack_detection import AttackDetection
from utils.screenshot import screenshot
from utils.windows_notification import WindowsNotification
from utils.getwin import getwin
from utils.match_template import click,match,press,move,scroll_move,traversal_tpl
from utils.resource_path import ResourcePath
from utils.process_terminator import ProcessTerminator
from config.load_config import wait_speed,action_speed,squad_index,level_index,task_index,check_reward,check_coffee,check_lottery,game_path
#-------------------------------------------------------------------------------------------------------

def menu(action):
    if status.timeout:
        return
    logger.debug('正在返回菜单')
    while True:

        if match(RPAID.file('quit_battle.png')):  #退出战斗 和 退出空洞
            logger.trace("退出战斗返回菜单")
            click(RPAID.file('quit_battle.png'))
            click(RPAID.file('confirm.png'))
            click(RPAID.file('quit.png'), True)
            click(RPAID.path("assets/images/hollow/mission_completed.png"), True)
        if action == "stay" and match(RPAID.file("esc_menu.png")):
            logger.trace("现在处于主菜单")
            time.sleep(wait_speed)
            return
        if action == "leave" and match(RPAID.file("lobby.png")):
            logger.trace("现在处于大厅")
            time.sleep(wait_speed)
            return

        else:
            logger.trace('正在返回菜单,请保持游戏画面处于前台')
            time.sleep(wait_speed)
            pydirectinput.press('esc', )
            time.sleep(1)
def battle():
    if status.timeout:
        return
    logger.trace("------------战斗开始--------------")
    attack_detection.start() # 启动/放行 攻击检测线程
    while True:
        result=match(RPAID.file("battle_end.png"))
        if result :
            logger.trace('---------------------战斗结束-------------------------')
            attack_detection.stop()  # 阻塞 攻击检测
            pyautogui.moveTo(result[1])
            time.sleep(action_speed)
            pyautogui.click()
            break

        else:
            logger.trace('正在战斗中')
            pydirectinput.press('q',_pause=False)
            pydirectinput.keyDown('e')
            time.sleep(0.4)
            pydirectinput.keyUp('e')
            pydirectinput.keyDown('e')
            time.sleep(0.4)
            pydirectinput.keyUp('e')
            pydirectinput.mouseDown(button="middle")
            pydirectinput.mouseUp(button="middle",_pause=False)  #禁用_pause节省0.1秒
            if match_hsv():
                pydirectinput.mouseDown()
                time.sleep(2)
                pydirectinput.mouseUp(_pause=False)
            for _ in range(15):
                pydirectinput.mouseDown()
                pydirectinput.mouseUp()

def match_hsv():
    """临时用于检测星见雅技能"""
    tpl=cv2.imread(RPAID.file("battle_miyabi.png"))  #判断角色是否处于前场
    ss=screenshot("rgb")
    hsv=cv2.cvtColor(ss,cv2.COLOR_RGB2HSV)
    bgr=cv2.cvtColor(ss,cv2.COLOR_RGB2BGR)
    result=cv2.matchTemplate(bgr,tpl,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc=cv2.minMaxLoc(result)
    if max_val >0.9:
        min_target=numpy.array([90,255,255])
        max_target=numpy.array([90,255,255])
        result=cv2.inRange(hsv,min_target,max_target)
        if result.any():
            return True
def battery_check():
    """获取体力"""
    menu('stay')
    x,y=match(RPAID.file("battery.png"))[1] #获取坐标
    screenshot=pyautogui.screenshot(region=(x-135,y+8,55,35))    #根据电池位置计算区域
    screenshot_numpy=numpy.array(screenshot)  #屏幕截图PIL Image转Numpy数组

    result=reader.readtext(screenshot_numpy,detail=0)   #识别并赋值结果 detail=0仅文本
    result=int(result[0])
    return result

def global_listener():
    """全局模板监听，非通用函数"""
    logger.trace("【线程启动】全局监听")
    while True:
        if not event_global.is_set():
            time.sleep(1)
            templates = [RPAID.file('reconnect.png'), RPAID.file('login.png'), RPAID.file("monthly_membership.png"), RPAID.file("astra_yao.png"), RPAID.file('connect_retry.png')]
            for tpl in templates:
                result = match(tpl)
                if result :
                    if tpl==RPAID.file('astra_yao.png'): #检测耀佳音前场
                        time.sleep(2)
                        pydirectinput.press("space")

                    pyautogui.moveTo(result[1])  #点击出现的模板(max_loc)
                    time.sleep(action_speed)
                    pyautogui.click()


def object_search(model,clsid,tpl=None):
    """单目标搜索，无法对应多目标场景"""
    sw,sh=pyautogui.size()  #显示器分辨率
    scw,sch=sw/2,sh/2 #屏幕中心 screen_center_w
    no_target=0  #无目标计数
    while True:
        result=model(source=screenshot("bgr"),imgsz=640,verbose=False)

        if result[0].boxes.conf.numel() == 0:   #判断置信度张量内元素的数量,没有目标即 0
            pydirectinput.moveRel(-100,0,relative=True)
            logger.trace("【目标检测】屏幕内没有目标")
            pydirectinput.press("w")
            no_target+=1
            if no_target > 6:
                pydirectinput.moveRel(0,-999,relative=True)  #重置Y轴
                no_target=0 # 重置计数

        else:
            try:
                for target in result[0]: # 支持多源输入，result是列表
                    if target.boxes.conf >0.6:
                        cls=int(target.boxes.cls.tolist()[0]) #张量转列表 转整数
                        if not cls==clsid:
                            pydirectinput.moveRel(-100, 0, relative=True) #出现目标 但非指定类型，继续搜索
                            break

                        x,y,w,h=target.boxes.xywh.tolist()[0]
                        x_scale = 0.12  # 视角相对移动倍率
                        y_scale = 0.24
                        if x > scw:  # 当目标在屏幕中心右边
                            pydirectinput.moveRel(int((x - scw) * x_scale), 0, relative=True)
                        if y > sch:  # 当目标在屏幕中心下边
                            pydirectinput.moveRel(0, int((y - (sch - 300)) * y_scale), relative=True)
                        if x < scw:
                            pydirectinput.moveRel(-int((scw - x) * x_scale), 0, relative=True)
                        if y < sch:
                            pydirectinput.moveRel(0, -int(((sch - 300) - y) * y_scale), relative=True)

                        if scw - 40 < x < scw + 40 and sch - 300 - 120 < y < sch - 300 + 120:  # 当目标对齐屏幕中间偏上方
                            logger.trace(f'【目标检测】TRAPPED！类型：{cls}')
                            pydirectinput.keyDown('w')
                            pydirectinput.press('f',presses=15,interval=0.1)
                            pydirectinput.keyUp('w')
                            if tpl is not None:
                                click(tpl)
                                if status.timeout:
                                    logger.trace(f'【目标检测】未出现{tpl}')
                                    status.timeout=False
                                    pydirectinput.press('esc')
                                    click(RPAID.file('quit_battle.png'))
                                    click(RPAID.file('confirm.png'))
                                    click(RPAID.file('quit.png'))
                                    status.timeout=True

                            return
            except ValueError:
                logger.trace(f'【目标检测】类型错误:{result[0].boxes.cls}')
                pydirectinput.moveRel(-100, 0, relative=True)

def cprint(text,color):
    print(f"\033[{color}m{text}\033[0m")  #ANSI转义码 标准30-37 高亮90-97

def admin_check():
    if ctypes.windll.shell32.IsUserAnAdmin():
        logger.debug("权限检查通过")
        time.sleep(1)
    else:
        logger.error("管理员权限缺失，需要提升权限")  #pyinstaller --uac-admin
        raise OSError

#-------------------------------------------------任务---------------------------------------------------------------
def coffee():
    if not status.timeout:
        menu('leave')
        logger.info("正在喝咖啡..")
        map_select(RPAID.file("map_sixcent.png"))
        click(RPAID.file('loc_cafe.png'))
        click(RPAID.file('confirm.png'))
        menu('leave')
        press(RPAID.file('lobby.png'), 'f')
        time.sleep(2)
        click(RPAID.file('order.png'))
def reward():
    if not status.timeout:
        menu('leave')    #每日奖励
        logger.info("领取奖励中")
        press(RPAID.file('lobby.png'), 'f2')
        click(RPAID.file('tactics.png'))
        click(RPAID.file('daily.png'))
        click(RPAID.file('daily_reward.png'), True)
        click(RPAID.file('confirm.png'), True)

        click(RPAID.file('weekly_reward.png'))   #每周奖励
        traversal_tpl(RPAID.file('weekly_reward_2.png'), skip=True)
        click(RPAID.file('weekly_reward_3.png'), True)
        pydirectinput.click()

        menu('leave')   #月卡
        press(RPAID.file('lobby.png'), 'f3')
        press(RPAID.file('monthly_ads.png'), 'esc', True)
        click(RPAID.file('monthly_task.png'), True)
        click(RPAID.file('monthly_claim.png'), True)
        click(RPAID.file('monthly_battlepass.png'), True)
        click(RPAID.file('monthly_claim.png'), True)

        menu("stay")   #邮件
        click(RPAID.file("mail.png"))
        click(RPAID.file("mail_claim.png"))
def events():
    if not status.timeout:
        menu('stay')
        click(RPAID.file('events.png'))
        move(RPAID.file('bait_event.png'))
        pydirectinput.moveRel(50, 100)
        time.sleep(1)
        for _ in range(10):
            pyautogui.scroll(-1)
        scroll_move(RPAID.file('event_gift.png'), reverse=True, skip=True) #全新放送
        pydirectinput.click()
        click(RPAID.file('event_claim.png'), True)
        click(RPAID.file('event_claim_2.png'), True)
        click(RPAID.file('confirm.png'), True)

        move(RPAID.file('bait_event.png'))
        pydirectinput.moveRel(50, 100)
        time.sleep(1)
        for _ in range(10):
            pyautogui.scroll(-1)
        scroll_move(RPAID.file('event_gift_2.png'), reverse=True, skip=True)  #嗯呢大惊喜
        pydirectinput.click()
        click(RPAID.file('event_claim.png'), True)
        click(RPAID.file('event_claim_2.png'), True)
        click(RPAID.file("confirm.png"), True)
def lottery():
    if not status.timeout:
        menu('leave')
        logger.info("前往刮刮卡报刊亭")
        map_select(RPAID.file('map_sixcent.png'))
        click(RPAID.file('loc_newsstand.png'))
        click(RPAID.file('confirm.png'))
        menu('leave')
        pydirectinput.press('w',presses=10)
        pydirectinput.press('f',presses=5)
        click(RPAID.file('dog_sleep.png'), True)
        click(RPAID.file('dog_wake.png'), True)
        click(RPAID.file('dog_wake_2.png'), True)
        click(RPAID.file('lottery.png'))
        move(RPAID.file('lottery_2.png'))
        pyautogui.moveRel(0,-140)
        pyautogui.dragRel(400, duration=1)
        pyautogui.moveRel(-400,40)
        pyautogui.dragRel(400, duration=1)
        pyautogui.moveRel(-400,40)
        pyautogui.dragRel(400, duration=1)
        time.sleep(1)
def disc(task_name):
    if not status.timeout:
        menu('leave')
        logger.info("执行驱动盘任务")
        press(RPAID.file('lobby.png'), 'f2')
        click(RPAID.file('tactics.png'))
        click(RPAID.file('train.png'))
        click(RPAID.file('sidebar_disc.png'))
        click(RPAID.file('go.png'))
        click(RPAID.file('confirm.png'))
        move(RPAID.file('bait_disc.png'))
        scroll_move(task_name)
        pydirectinput.click()
        select_level()
        click(RPAID.file('next_step.png'))
        select_squad()
        click(RPAID.file('start_battle.png'))
        battle()
def core(task_name):
    if not status.timeout:
        menu('leave')
        logger.info("执行核心技任务")
        press(RPAID.file('lobby.png'), 'f2')
        click(RPAID.file('tactics.png'))
        click(RPAID.file('train.png'))
        click(RPAID.file('sidebar_core.png'))
        move(RPAID.file('go.png'))
        scroll_move(task_name)
        pydirectinput.moveRel(920,100)
        pydirectinput.click()
        click(RPAID.file('confirm.png'))
        click(RPAID.file('double_on.png'), True)
        click(RPAID.file('confirm.png'), True)
        select_level()
        click(RPAID.file('next_step.png'))
        select_squad()
        click(RPAID.file('start_battle.png'))
    battle()
def hunt(task_name):
    if not status.timeout:
        menu('leave')
        logger.info("执行恶名狩猎任务")
        press(RPAID.file('lobby.png'), 'f2')
        click(RPAID.file('tactics.png'))
        click(RPAID.file('combat.png'))
        move(RPAID.file('go.png'))
        scroll_move(task_name)
        pydirectinput.moveRel(920, 100)
        pydirectinput.click()
        click(RPAID.file('confirm.png'))
        click(RPAID.file('hunt_off.png'), True)
        click(RPAID.file('confirm.png'), True)
        select_level()
        click(RPAID.file('next_step.png'))
        select_squad()
        click(RPAID.file('start_battle.png'))
        if not status.timeout:
            object_search(yolo_object, clsid=1, tpl=RPAID.file('select.png'))
            object_search(yolo_hollow,clsid=0)
            battle()
def upgrade(task_name):
    if not status.timeout:
        menu('leave')
        logger.info("执行养成材料任务")
        press(RPAID.file('lobby.png'), 'f2')
        click(RPAID.file('tactics.png'))
        click(RPAID.file('train.png'))
        click(RPAID.file('go.png'))
        click(RPAID.file('confirm.png'))
        click(RPAID.file('return.png'))
        if 'basic_' in task_list[task_index]:
            click(RPAID.file('upgrade_basic.png'))
        if 'promotion_' in task_list[task_index]:
            click(RPAID.file('upgrade_promotion.png'))
        if 'weapon_' in task_list[task_index]:
            click(RPAID.file('upgrade_weapon.png'))
        if 'skill_' in task_list[task_index]:
            click(RPAID.file('upgrade_skill.png'))
        if 'custom_' in task_list[task_index]:
            click(RPAID.file('upgrade_custom.png'))
        move(RPAID.file('bait_edit.png'))
        scroll_move(task_name)
        pydirectinput.moveRel(0,50)
        pydirectinput.click()
        select_level()
        click(RPAID.file('next_step.png'))
        select_squad()
        click(RPAID.file('start_battle.png'))
        battle()
def daily_task():
    if not status.timeout:

        task,cost=None,None

        if 'basic_' in task_list[task_index] or 'promotion_' in task_list[task_index] or 'weapon_' in task_list[task_index] \
                or 'skill_' in task_list[task_index] or 'custom_' in task_list[task_index] :
            task=lambda :upgrade(task_list[task_index])
            cost=100
        if 'disc_' in task_list[task_index]:
            task=lambda :disc(task_list[task_index])
            cost=60
        if 'core_' in task_list[task_index]:
            task=lambda :core(task_list[task_index])
            cost=40
        if 'hunt_' in task_list[task_index]:
            task=lambda :hunt(task_list[task_index])
            cost=60
        if task is not None:
            try:
                battery = battery_check()  # 获取体力信息
                cycle = int(battery / cost)
                if cycle == 0 :
                    logger.info(f"当前电量为：{battery}，停止消耗体力")
                else:
                    logger.info(f"当前电量为：{battery}，执行 {cycle} 次循环")
                count = 0
                for _ in range(cycle):
                    task()
                    if not status.timeout:
                        count = count + 1
                        logger.info(f"已完成 {count} 次")
            except Exception as e:
                logger.error(e)
                logger.error("无法获取电量信息")
                status.timeout=True #超时

def select_squad():
    if not status.timeout:
        if squad_index!=0:
            click(RPAID.file('squad_preset.png'))
            squad_list = ['None', RPAID.file('squad_1.png'), RPAID.file('squad_2.png'), RPAID.file('squad_3.png'), RPAID.file('squad_4.png'), RPAID.file('squad_5.png'), RPAID.file('squad_6.png')]
            move(squad_list[squad_index])
            pyautogui.moveRel(300,0)
            pyautogui.click()
            click(RPAID.file('select_squad.png'))
def select_level():
    if not status.timeout:
        if level_index!=0:
            click(RPAID.file('level.png'))
            pyautogui.moveRel(0,300)
            pyautogui.click()
            click(RPAID.file('level.png'))
            pyautogui.moveRel(0,360)
            pyautogui.click()
def map_select(tpl):
    if not status.timeout:
        press(RPAID.file('lobby.png'), 'm')
        click(RPAID.file('old_guide.png'))
        pydirectinput.moveRel(0, 100)
        time.sleep(1)
        for _ in range(20):
            pyautogui.scroll(-1)
        scroll_move(tpl, reverse=True)
        pydirectinput.click()

#----------------------------------------------------------------------------------------------------------------
RPAID=ResourcePath('assets/images/daily',"config") # 实例化资源路径管理

task_list=[
'None',                     #此列表与GUI的ComboBox对应，和游戏内列表顺序无关！
RPAID.file('basic_character.png'),
RPAID.file('basic_weapon.png'),
RPAID.file('basic_credit.png'),
RPAID.file('basic_disc.png'),
RPAID.file('promotion_rupture.png'),
RPAID.file('promotion_attack.png'),
RPAID.file('promotion_stun.png'),
RPAID.file('promotion_anomaly.png'),
RPAID.file('promotion_assist.png'),
RPAID.file('promotion_defense.png'),
RPAID.file('weapon_rupture.png'),
RPAID.file('weapon_attack.png'),
RPAID.file('weapon_stun.png'),
RPAID.file('weapon_anomaly.png)'),
RPAID.file('weapon_assist.png'),
RPAID.file('weapon_defense.png'),
RPAID.file('skill_physical.png'),
RPAID.file('skill_pyro.png'),
RPAID.file('skill_freeze.png'),
RPAID.file('skill_shock.png'),
RPAID.file('skill_ether.png'),

RPAID.file('disc_10.png'), #云岿如我
RPAID.file('disc_9.png'),
RPAID.file('disc_8.png'),
RPAID.file('disc_7.png'),
RPAID.file('disc_6.png'),
RPAID.file('disc_5.png'),
RPAID.file('disc_4.png'),
RPAID.file('disc_3.png'),
RPAID.file('disc_2.png'),
RPAID.file('disc_1.png'),

RPAID.file('core_11.png'),
RPAID.file('core_10.png'),
RPAID.file('core_9.png'),
RPAID.file('core_8.png'),
RPAID.file('core_7.png'),
RPAID.file('core_6.png'),
RPAID.file('core_5.png'),
RPAID.file('core_4.png'),
RPAID.file('core_3.png'),
RPAID.file('core_2.png'),
RPAID.file('core_1.png'),

RPAID.file('hunt_6.png'),
RPAID.file('hunt_5.png'),
RPAID.file('hunt_4.png'),
RPAID.file('hunt_3.png'),
RPAID.file('hunt_2.png'),
RPAID.file('hunt_1.png'),

RPAID.file('custom_1.png'),
RPAID.file('custom_2.png'),
RPAID.file('custom_3.png'),
RPAID.file('custom_4.png'),
RPAID.file('custom_5.png'),
]

#______________________________________________初始化______________________________________________________________
try:
    reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=RPAID.path("assets/models"), verbose=False)  # 载入easyocr模型
    yolo_attack = YOLO(RPAID.path("assets/models/ZA_3295.pt")).to('cpu')
    yolo_hollow= YOLO(RPAID.path("assets/models/ZH_64.pt")).to('cpu')
    yolo_object=YOLO(RPAID.path('assets/models/ZO_64.pt')).to('cpu')

    event_global = threading.Event()  # 全局监听 事件
    thread_global=threading.Thread(target=global_listener,daemon=True) #全局监听 线程
    if not thread_global.is_alive():
        thread_global.start()  # 启动 全局监听

    process_terminator=ProcessTerminator()# 实例化 终止监听
    process_terminator.start() #启动 终止监听

    attack_detection=AttackDetection(yolo_attack) # 实例化 攻击检测

    pydirectinput.FAILSAFE=False
    pyautogui.FAILSAFE=False

except:
    logger.error('-----------------初始化错误---------------------')
    logger.error(traceback.format_exc())

#-------------------------------------------------------------------------------------------------------------
def start_daily():
    timeout_count = 0
    try:
        logger.debug("初始化完毕..启动{日常任务}模块")
        time.sleep(3)
        getwin(zh_title="绝区零",en_title="ZenlessZoneZero",config_path=game_path)  #启动游戏或激活窗口
        print()
        logger.success("程序开始接管操作，请保持游戏画面处于前台，终止按下Alt键")

        while True:
            status.timeout=False            #重置超时状态
            if check_coffee:
                coffee()
            daily_task()
            daily_task()
            if check_reward:
                reward()
                events()
            if check_lottery:
                lottery()
            if status.timeout:
                timeout_count+=1
                if timeout_count >= 3 :
                    logger.warning("任务在某一步无法继续，请检查运行日志或降低速度挡位")
                    return
            if not status.timeout:
                battery_remaining=battery_check()
                if battery_remaining >= 240 :
                    battery_report=f"电量剩余：{battery_remaining}，已达到上限"
                else:
                    battery_report=f"电量剩余：{battery_remaining}，距离回满还有 {int((240*5-battery_remaining*5)/60)} 小时"
                try:
                    win = pygetwindow.getWindowsWithTitle("ZA")  #Windows全屏程序自动打开免打扰，需要借用ZA窗口的允许通知状态
                    win[0].activate()  #激活ZA窗口
                except Exception as e:
                    logger.error(e)
                WindowsNotification(RPAID.path("assets/images/daily/icon.ico")).push("任务完成✅", f"程序已经结束，电量剩余：{battery_remaining}")
                logger.info(battery_report)
                logger.success('<--------每日任务结束-------->')
                event_global.clear()  # 阻塞模板监听线程
                return

    # except OSError as e:
    #     logger.error(e)
    #     logger.error("路径错误或管理员权限缺失")
    except Exception:
        logger.error(traceback.format_exc())
        logger.error('<--------每日任务发生未知错误-------->')


if __name__=="__main__":
    start_daily()  #启动日常
    logger.warning("程序已经结束，按回车键退出(Enter)")
    input()
    os._exit(0)






