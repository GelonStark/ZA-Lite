import sys
from json import JSONDecodeError
from PySide6.QtCore import QSize, Qt, QTimer, QUrl,QPropertyAnimation,QRect,QEasingCurve
from PySide6.QtGui import QPixmap, QIcon, QFont, QFontDatabase, QDesktopServices
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QStackedWidget, QFileDialog, \
    QCheckBox,QGraphicsOpacityEffect
import json
import subprocess
import os
import pygetwindow
import time
import pygame
#-------------------------------------
from utils.resource_path import ResourcePath
#-------------------------------------------初始化------------------------------------------------------------

pygame.init() # 初始化pygame

allwin=pygetwindow.getAllTitles()
targetwin=pygetwindow.getWindowsWithTitle('ZA - Lite')    #不要存在与这个标题重名的进程
if 'ZA - Lite' in allwin:
    targetwin[0].minimize()
    targetwin[0].restore()
    os._exit(0)

def config_path():
    """当在IDE项目结构时 config文件夹在上一级,
      在打包后的结构，config文件夹位于同一级"""
    if hasattr(sys,"_MEIPASS"):
        return "config"      #打包后在同一级
    else:
        print("【当前还未打包】")
        return "../config" #打包前在上一级

os.makedirs(config_path(), exist_ok=True) #预先创建config文件夹，用于生成config.json

RP=ResourcePath('使用完整路径，此参数无用', "config")  #实例化要在makedirs之后，不然找不到config标记文件夹

#-------------------------------------------------------------------------------------------
class ZA(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(300, 400)
        self.setWindowTitle('ZA - Lite')
        self.setWindowIcon(QPixmap(RP.path("gui/images/icon.png")))
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明

        # self.setWindowFlag(Qt.WindowStaysOnTopHint) #置顶

        def load_config():
            try:
                with open(os.path.join(config_path(),"config.json"), 'r') as f:  # config是外置资源 gui用onefile打包不要用RP
                    config = json.load(f)
                    self.check_coffee.setChecked(config.get('check_coffee', False))  # 此处字典的默认值在格式非法时无用！
                    self.combo_task.setCurrentIndex(config.get('combo_task', 0))
                    self.label_show_path.setText(config.get('game_path', '用户未指定'))
                    self.combo_server.setCurrentIndex(config.get('server', 0))
                    self.combo_shutdown.setCurrentIndex(config.get('shutdown', 0))
                    self.combo_speed.setCurrentIndex(config.get('speed', 0))
                    self.check_reward.setChecked(config.get('check_reward', False))
                    self.check_lottery.setChecked(config.get('check_lottery', False))
                    self.combo_squad.setCurrentIndex(config.get('combo_squad', 0))
                    self.combo_level.setCurrentIndex(config.get('combo_level', 0))
                    self.combo_date.setCurrentIndex(config.get("combo_hollow_date", 0))
                    self.combo_round.setCurrentIndex(config.get("combo_hollow_round", 0))
                    self.combo_type.setCurrentIndex(config.get("combo_hollow_type", 0))
                    self.developer_mode=config.get("developer_mode", False)
            except FileNotFoundError:     #在读取配置失败的情况下，组件会使用初始化状态的index，然后被save_config()保存，变成合法json
                print("没有找到配置文件！")
                self.label_show_path.setText("用户未指定")
                self.developer_mode = False
            except JSONDecodeError :
                self.developer_mode=False
                self.label_show_path.setText("用户未指定")
                print("读取配置失败：JSON格式非法")  #跳过读取异常的json文件

        def popup_tone_1():
            sound=pygame.mixer.Sound(RP.path("gui/audio/popup_tone_1.mp3"))
            sound.set_volume(0.1)
            sound.play()
        def popup_tone_2():
            sound=pygame.mixer.Sound(RP.path("gui/audio/popup_tone_2.mp3"))
            sound.set_volume(0.1)
            sound.play()
        def popup_tone_3():
            sound=pygame.mixer.Sound(RP.path("gui/audio/popup_tone_3.mp3"))
            sound.set_volume(0.1)
            sound.play()
        def popup_tone_4():
            sound=pygame.mixer.Sound(RP.path("gui/audio/popup_tone_4.mp3"))
            sound.set_volume(0.1)
            sound.play()
        def click_sound():
            sound=pygame.mixer.Sound(RP.path("gui/audio/click.mp3"))
            sound.set_volume(0.1)
            sound.play()
        def intro_sound():
            sound = pygame.mixer.Sound(RP.path("gui/audio/intro.mp3"))
            sound.set_volume(0.16)
            sound.play()
        def close_gui():
            popup_tone_3()
            self.showMinimized()
            time.sleep(0.5)
            self.close()

        intro_sound() # 开机音效
#-------------------------------------------------------------------------------------------
        stack_1 = QStackedWidget(self)
        stack_1.setFixedSize(270, 380)

        page_home = QWidget(stack_1)
        page_home.setFixedSize(270, 380)
        stack_1.addWidget(page_home)
        page_home.setStyleSheet('background:transparent')

        page_setting = QWidget(stack_1)
        page_setting.setFixedSize(270, 380)
        page_setting.setStyleSheet('background:transparent')
        stack_1.addWidget(page_setting)

        page_battle = QWidget(stack_1)
        page_battle.setFixedSize(270, 380)
        page_battle.setStyleSheet('background:transparent')
        stack_1.addWidget(page_battle)

        page_hollow = QWidget(stack_1)
        page_hollow.setFixedSize(270, 380)
        page_hollow.setStyleSheet('background:transparent')
        stack_1.addWidget(page_hollow)

        img_miya = QPixmap(RP.path('gui/images/miyabi.png'))
        img_background = QPixmap(RP.path('gui/images/miyabi_2.png'))
        label_setting_background = QLabel(page_setting)
        label_setting_background.setPixmap(img_background.scaled(270, 380, Qt.AspectRatioMode.KeepAspectRatio,
                                                                 Qt.TransformationMode.SmoothTransformation))
        label_battle_background = QLabel(page_battle)
        label_battle_background.setPixmap(img_background.scaled(270, 380, Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation))
        label_home_background = QLabel(page_home)
        label_home_background.setPixmap(
            img_miya.scaled(270, 380, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        label_hollow_background = QLabel(page_hollow)
        label_hollow_background.setPixmap(
            img_background.scaled(270, 380, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        label_title = QLabel('选择任务', label_home_background)
        label_title.setStyleSheet('font-size:20px')
        label_title.setGeometry(22, 40, 100, 20)

        self.combo_task = QComboBox(page_home)
        self.combo_task.addItems([' 无',
                                  ' 基础材料：角色经验',
                                  ' 基础材料：音擎经验',
                                  ' 基础材料：丁尼',
                                  ' 基础材料：驱动盘经验',
                                  ' 代理人晋升：命破',
                                  ' 代理人晋升：强攻',
                                  ' 代理人晋升：击破',
                                  ' 代理人晋升：异常',
                                  ' 代理人晋升：支援',
                                  ' 代理人晋升：防护',
                                  ' 音擎改装： 命破',
                                  ' 音擎改装： 强攻',
                                  ' 音擎改装： 击破',
                                  ' 音擎改装： 异常',
                                  ' 音擎改装： 支援',
                                  ' 音擎改装： 防护',
                                  ' 代理人技能：物理',
                                  ' 代理人技能：火',
                                  ' 代理人技能：冰',
                                  ' 代理人技能：电',
                                  ' 代理人技能：以太',
                                  ' 驱动盘： 云岿如我/山大王',
                                  ' 驱动盘：如影相随/法厄同之歌',
                                  ' 驱动盘：折枝剑歌/静听嘉音',
                                  ' 驱动盘：混沌爵士/原始朋克',
                                  ' 驱动盘：极地重金属/自由蓝调',
                                  ' 驱动盘：炎狱重金属/河豚电音',
                                  ' 驱动盘：啄木鸟电音/灵魂摇滚',
                                  ' 驱动盘：震星迪斯科/雷暴重金属',
                                  ' 驱动盘：獠牙重金属/激素朋克',
                                  ' 驱动盘：混沌重金属/摇摆爵士',
                                  ' 核心技：凶魁愚者',
                                  ' 核心技：阿瓦鲁斯',
                                  ' 核心技：雷色斯人',
                                  ' 核心技：伐木机',
                                  ' 核心技：简',
                                  ' 核心技：蛮横力士',
                                  ' 核心技：提丰',
                                  ' 核心技：汉斯',
                                  ' 核心技：装甲哈提',
                                  ' 核心技：通缉打手',
                                  ' 核心技：杜拉罕',
                                  ' 恶名狩猎：秽息司祭',
                                  ' 恶名狩猎：牲鬼布林格',
                                  ' 恶名狩猎：霸主庞培',
                                  ' 恶名狩猎：冥宁芙双子',
                                  ' 恶名狩猎：未知复合侵蚀体',
                                  ' 恶名狩猎：死路屠夫',
                                  ' 自定义模板：卡组 1',
                                  ' 自定义模板：卡组 2',
                                  ' 自定义模板：卡组 3',
                                  ' 自定义模板：卡组 4',
                                  ' 自定义模板：卡组 5',
                                  ])
        self.combo_task.setGeometry(20, 65, 220, 30)
        self.combo_task.setStyleSheet('background:rgb(206,206,206)')
        self.combo_task.activated.connect(popup_tone_2) #音效
#----------------------------------------------------------------------------------
        #咖啡 Checkbox
        self.check_coffee = QCheckBox('喝咖啡', page_home)  #Checkbox
        self.check_coffee.setGeometry(22, 105, 500, 20)
        self.check_coffee.setStyleSheet('font-size:15px')
        self.check_coffee.clicked.connect(popup_tone_2)

        self.anime_pos_coffee=QPropertyAnimation(self.check_coffee,b"geometry")  #创建动画属性 位移动画
        self.anime_pos_coffee.setStartValue(QRect(0,105,500,20)) #开始位置
        self.anime_pos_coffee.setEndValue(QRect(22,105,500,20))  #结束位置
        self.anime_pos_coffee.setDuration(333)  # 持续时间 调这里！
        self.anime_pos_coffee.setEasingCurve(QEasingCurve.OutQuad) #动画曲线
        self.anime_pos_coffee.start()
        #QTimer.singleShot(444,self.anime_pos_coffee.start) #延时启动

        self.effect_coffee=QGraphicsOpacityEffect()  #安装透明度效果，不自带这个属性
        self.check_coffee.setGraphicsEffect(self.effect_coffee)
        self.effect_coffee.setOpacity(0)

        self.anime_opacity_coffee=QPropertyAnimation(self.effect_coffee,b"opacity")  #透明度动画
        self.anime_opacity_coffee.setStartValue(0.0)
        self.anime_opacity_coffee.setEndValue(1.0)
        self.anime_opacity_coffee.setDuration(555)
        self.anime_opacity_coffee.start()
        #QTimer.singleShot(444, self.anime_opacity_coffee.start)
#-------------------------------------------------------------------
        #领奖励 Checkbox
        self.check_reward = QCheckBox('领奖励', page_home)
        self.check_reward.setGeometry(22, 135, 500, 20)
        self.check_reward.setStyleSheet('font-size:15px')
        self.check_reward.clicked.connect(popup_tone_2)

        self.anime_pos_reward = QPropertyAnimation(self.check_reward, b"geometry")  # 创建动画属性 位移动画
        self.anime_pos_reward.setStartValue(QRect(0, 135, 500, 20))  # 开始位置
        self.anime_pos_reward.setEndValue(QRect(22, 135, 500, 20))  # 结束位置
        self.anime_pos_reward.setDuration(222)  # 持续时间
        self.anime_pos_reward.setEasingCurve(QEasingCurve.OutQuad)  # 动画曲线
        self.anime_pos_reward.start()
        #QTimer.singleShot(333, self.anime_pos_reward.start)  # 延时启动

        self.effect_reward = QGraphicsOpacityEffect()  # 安装透明度效果，不自带这个属性
        self.check_reward.setGraphicsEffect(self.effect_reward)
        self.effect_reward.setOpacity(0)

        self.anime_opacity_reward = QPropertyAnimation(self.effect_reward, b"opacity")  # 透明度动画
        self.anime_opacity_reward.setStartValue(0.0)
        self.anime_opacity_reward.setEndValue(1.0)
        self.anime_opacity_reward.setDuration(555)
        self.anime_opacity_reward.start()
        #QTimer.singleShot(333, self.anime_opacity_reward.start)
#----------------------------------------------------------------------------
        #刮刮卡 Checkbox
        self.check_lottery = QCheckBox('刮刮卡', page_home)
        self.check_lottery.setGeometry(22, 165, 500, 20)
        self.check_lottery.setStyleSheet('font-size:15px')
        self.check_lottery.clicked.connect(popup_tone_2)

        self.anime_pos_lottery = QPropertyAnimation(self.check_lottery, b"geometry")  # 创建动画属性 位移动画
        self.anime_pos_lottery.setStartValue(QRect(0, 165, 500, 20))  # 开始位置
        self.anime_pos_lottery.setEndValue(QRect(22, 165, 500, 20))  # 结束位置
        self.anime_pos_lottery.setDuration(333) # 持续时间
        self.anime_pos_lottery.setEasingCurve(QEasingCurve.OutQuad)  # 动画曲线
        self.anime_pos_lottery.start()
        #QTimer.singleShot(0, self.anime_pos_lottery.start)  # 延时启动

        self.effect_lottery = QGraphicsOpacityEffect()  # 安装透明度效果，不自带这个属性
        self.check_lottery.setGraphicsEffect(self.effect_lottery)
        self.effect_lottery.setOpacity(0)

        self.anime_opacity_lottery = QPropertyAnimation(self.effect_lottery, b"opacity")  # 透明度动画
        self.anime_opacity_lottery.setStartValue(0.0)
        self.anime_opacity_lottery.setEndValue(1.0)
        self.anime_opacity_lottery.setDuration(555)
        self.anime_opacity_lottery.start()
        #QTimer.singleShot(0, self.anime_opacity_lottery.start)

        def launch():
            subprocess.run('taskkill /IM "ZA Main.exe" /F')  #cmd tasklist查询
            subprocess.Popen('ZA Main.exe')
            time.sleep(0)
            self.showMinimized()

        button_launch = QPushButton('开始', page_home)
        button_launch.setGeometry(25, 220, 90, 40)
        button_launch.setStyleSheet('QPushButton{background:rgb(22,140,148);'
                                    'border-radius:20px;font-size:25px;'
                                    'color:rgb(22,22,22);'
                                    'font-family:SDK_ID_WEB}'

                                    'QPushButton:hover{background:rgb(33,33,33);'
                                    'color:rgb(22,140,148)}'

                                    'QPushButton:pressed{background:rgb(0,0,0)}')
        button_launch.clicked.connect(click_sound) # 音效
        button_launch.clicked.connect(launch) # 启动文件

#----------------------------------------------------------------------------------------
        button_hollow=QPushButton("",page_home)
        button_hollow.setGeometry(144,180,80,40)
        button_hollow.setStyleSheet("QPushButton{background:transparent;border:none}")
        button_hollow.setCursor(Qt.PointingHandCursor)  # 手指箭头
        button_hollow.clicked.connect(lambda :stack_1.setCurrentIndex(3))
        button_hollow.clicked.connect(popup_tone_2) #音效

        button_setting = QPushButton(page_home)
        button_setting.setIcon(QIcon(RP.path("gui/images/setting_fill.png")))
        button_setting.setStyleSheet('QPushButton:hover{background:rgb(133,133,133)}')  # cdcdcd
        button_setting.setIconSize(QSize(25, 25))
        button_setting.setGeometry(18, 270, 30, 30)
        button_setting.setFlat(True)
        button_setting.clicked.connect(lambda : stack_1.setCurrentIndex(1))
        button_setting.clicked.connect(popup_tone_2) #音效

        button_game = QPushButton(page_home)
        button_game.setIcon(QIcon(RP.path("gui/images/game_fill.png")))
        button_game.setStyleSheet('QPushButton:hover{background:rgb(133,133,133)}')
        button_game.setIconSize(QSize(25, 25))
        button_game.setGeometry(48, 270, 30, 30)
        button_game.setFlat(True)
        button_game.clicked.connect(lambda : stack_1.setCurrentIndex(2))
        button_game.clicked.connect(popup_tone_2) # 音效

        button_question = QPushButton(page_home)
        button_question.setIcon(QIcon(RP.path("gui/images/question_fill.png")))
        button_question.setStyleSheet('QPushButton:hover{background:rgb(133,133,133)}')
        button_question.setIconSize(QSize(25, 25))
        button_question.setGeometry(78, 270, 30, 30)
        button_question.setFlat(True)
        button_question.clicked.connect(popup_tone_2) # 音效
        button_question.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl('https://www.yuque.com/gelonstark/kb/za')))
#---------------------------------------------------
        button_return = QPushButton(page_setting)
        button_return.setIcon(QIcon(RP.path("gui/images/return.png")))
        button_return.setIconSize(QSize(25, 25))
        button_return.setGeometry(20, 260, 40, 40)
        button_return.setFlat(True)
        button_return.clicked.connect(popup_tone_2) # 音效
        button_return.clicked.connect(lambda: stack_1.setCurrentIndex(0))
        button_return.clicked.connect(lambda: self.anime_pos_coffee.start())  # 绑定动画 咖啡
        button_return.clicked.connect(lambda: self.anime_opacity_coffee.start())
        button_return.clicked.connect(lambda: self.effect_coffee.setOpacity(0))


        button_return.clicked.connect(lambda: self.anime_pos_reward.start())  # 绑定动画 奖励
        button_return.clicked.connect(lambda: self.anime_opacity_reward.start())
        button_return.clicked.connect(lambda: self.effect_reward.setOpacity(0))

        button_return.clicked.connect(lambda: self.anime_pos_lottery.start())  # 绑定动画 刮卡
        button_return.clicked.connect(lambda: self.anime_opacity_lottery.start())
        button_return.clicked.connect(lambda: self.effect_lottery.setOpacity(0))

#----------------------------------------------------------
        button_return = QPushButton(page_battle)
        button_return.setIcon(QIcon(RP.path("gui/images/return.png")))
        button_return.setIconSize(QSize(25, 25))
        button_return.setGeometry(20, 260, 40, 40)
        button_return.setFlat(True)
        button_return.clicked.connect(lambda : popup_tone_2()) # 音效
        button_return.clicked.connect(lambda: stack_1.setCurrentIndex(0))
        button_return.clicked.connect(lambda: self.anime_pos_coffee.start())  # 绑定动画 咖啡
        button_return.clicked.connect(lambda: self.anime_opacity_coffee.start())
        button_return.clicked.connect(lambda: self.effect_coffee.setOpacity(0)) #动画开始前透明度设置为0 避免看到残留

        button_return.clicked.connect(lambda: self.anime_pos_reward.start())  # 绑定动画 奖励
        button_return.clicked.connect(lambda: self.anime_opacity_reward.start())
        button_return.clicked.connect(lambda: self.effect_reward.setOpacity(0))

        button_return.clicked.connect(lambda: self.anime_pos_lottery.start())  # 绑定动画 刮卡
        button_return.clicked.connect(lambda: self.anime_opacity_lottery.start())
        button_return.clicked.connect(lambda: self.effect_lottery.setOpacity(0))
#------------------------------------------------------
        button_return = QPushButton(page_hollow)
        button_return.setIcon(QIcon(RP.path("gui/images/return.png")))
        button_return.setIconSize(QSize(25, 25))
        button_return.setGeometry(20, 260, 40, 40)
        button_return.setFlat(True)
        button_return.clicked.connect(lambda : popup_tone_2()) # 音效
        button_return.clicked.connect(lambda: stack_1.setCurrentIndex(0))
        button_return.clicked.connect(lambda: self.anime_pos_coffee.start())  # 绑定动画 咖啡
        button_return.clicked.connect(lambda: self.anime_opacity_coffee.start())
        button_return.clicked.connect(lambda: self.effect_coffee.setOpacity(0))

        button_return.clicked.connect(lambda: self.anime_pos_reward.start())  # 绑定动画 奖励
        button_return.clicked.connect(lambda: self.anime_opacity_reward.start())
        button_return.clicked.connect(lambda: self.effect_reward.setOpacity(0))

        button_return.clicked.connect(lambda: self.anime_pos_lottery.start())  # 绑定动画 刮卡
        button_return.clicked.connect(lambda: self.anime_opacity_lottery.start())
        button_return.clicked.connect(lambda: self.effect_lottery.setOpacity(0))
#-----------------------------------------------------------
        button_close = QPushButton(page_home)
        button_close.setIcon(QIcon(RP.path('gui/images/close.png')))
        button_close.setIconSize(QSize(20, 20))
        button_close.setGeometry(210, 32, 30, 30)
        button_close.setFlat(True)
        button_close.clicked.connect(lambda : close_gui())


        button_minimize = QPushButton(page_home)
        button_minimize.setIcon(QIcon(RP.path('gui/images/minimize.png')))
        button_minimize.setIconSize(QSize(20, 20))
        button_minimize.setGeometry(180, 32, 30, 30)
        button_minimize.setFlat(True)
        button_minimize.clicked.connect(self.showMinimized)
        button_minimize.clicked.connect(popup_tone_3)

#----------------------------------------------------------------------------------

        self.label_show_path = QLabel(page_setting)
        self.label_show_path.setGeometry(20, 65, 220, 50)
        self.label_show_path.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')
        self.label_show_path.setWordWrap(True)

        # label_show_path.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        def select_path():
            path = QFileDialog.getOpenFileName()[0]
            if path:      #空的str将会是False
                print(path)
                self.label_show_path.setText(path)

        button_select_path = QPushButton('选择游戏路径', page_setting)
        button_select_path.clicked.connect(select_path)
        button_select_path.setGeometry(20, 33, 110, 30)
        button_select_path.setStyleSheet('font-size:15px;background-color:rgb(206,206,206)')

        background_speed = QLabel(page_setting)
        background_speed.setGeometry(20, 120, 220, 30)
        background_speed.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_speed = QLabel('运行速度', page_setting)
        label_speed.setGeometry(25, 115, 100, 40)
        label_speed.setStyleSheet('font-size:15px')

        self.combo_speed = QComboBox(page_setting)
        self.combo_speed.setGeometry(138, 122, 90, 25)
        self.combo_speed.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_speed.addItems([' 默认', ' 快', ' 慢'])
        self.combo_speed.activated.connect(popup_tone_2) #音效

        background_server = QLabel(page_setting)
        background_server.setGeometry(20, 155, 220, 30)
        background_server.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_server = QLabel('服务器', page_setting)
        label_server.setGeometry(25, 150, 100, 40)
        label_server.setStyleSheet('font-size:15px')

        self.combo_server = QComboBox(page_setting)
        self.combo_server.setGeometry(138, 157, 90, 25)  # 对齐右边坐标:x1+w1-w2
        self.combo_server.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_server.addItems([' 国服', ' 国际服'])
        self.combo_server.activated.connect(popup_tone_2) #音效

        background_shutdown = QLabel(page_setting)
        background_shutdown.setGeometry(20, 190, 220, 30)
        background_shutdown.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_shutdown = QLabel('任务完成', page_setting)
        label_shutdown.setGeometry(25, 185, 100, 40)
        label_shutdown.setStyleSheet('font-size:15px')

        self.combo_shutdown = QComboBox(page_setting)
        self.combo_shutdown.setGeometry(138, 192, 90, 25)  # 对齐右边坐标:x2=x1+w1-w2
        self.combo_shutdown.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_shutdown.addItems([' 无操作', ' 退出游戏', ' 关机'])
        self.combo_shutdown.activated.connect(popup_tone_2) #音效

        # -----------------------------------battle---------------------------------------
        label_battle = QLabel('游戏设置', page_battle)
        label_battle.setStyleSheet('font-size:20px')
        label_battle.setGeometry(22, 40, 100, 20)

        label_hollow = QLabel('零号空洞', page_hollow)
        label_hollow.setStyleSheet('font-size:20px')
        label_hollow.setGeometry(22, 40, 100, 20)
#---------------------------------------------------------
        background_date= QLabel(page_hollow)  #任务时间
        background_date.setGeometry(20, 65, 220, 30)
        background_date.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_date = QLabel('任务时间', page_hollow)
        label_date.setGeometry(25, 60, 100, 40)
        label_date.setStyleSheet('font-size:15px')

        self.combo_date = QComboBox(page_hollow)
        self.combo_date.setGeometry(138, 67, 90, 25)
        self.combo_date.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_date.addItems([' 每次', ' 星期 1', ' 星期 2', ' 星期 3', ' 星期 4', ' 星期 5', ' 星期 6',' 星期 7'])
        self.combo_date.activated.connect(popup_tone_2) #音效
#-----------------------------------------------------------
        background_round = QLabel(page_hollow)  #执行次数
        background_round.setGeometry(20, 100, 220, 30)
        background_round.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        self.combo_round = QComboBox(page_hollow)
        self.combo_round.setGeometry(138, 102, 90, 25)
        self.combo_round.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_round.addItems([' 不执行',' 无限次',' 1 次', ' 2 次', ' 3 次', ' 9 次'])
        self.combo_round.activated.connect(popup_tone_2) #音效

        label_round = QLabel('执行次数', page_hollow)
        label_round.setGeometry(25, 95, 100, 40)
        label_round.setStyleSheet('font-size:15px')
#---------------------------------------------------------------
        background_type = QLabel(page_hollow)
        background_type.setGeometry(20, 135, 220, 30)
        background_type.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        self.combo_type = QComboBox(page_hollow)
        self.combo_type.setGeometry(138, 137, 90, 25)
        self.combo_type.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_type.addItems([' 特遣调查', ' 战线肃清'])
        self.combo_type.activated.connect(popup_tone_2) #音效

        label_type = QLabel('副本类型', page_hollow)
        label_type.setGeometry(25, 130, 100, 40)
        label_type.setStyleSheet('font-size:15px')
#-------------------------------------------------------------------------------------------------------------------
        # button_start_hollow = QPushButton("START HOLLOW",page_hollow)
        # button_start_hollow.setGeometry(35,180,190,30)
        # button_start_hollow.setFlat(True)
        # button_start_hollow.setStyleSheet('QPushButton{background:rgb(216,216,216);'
        #                             'font-size:15px;'
        #                             'color:rgb(22,140,148);'
        #                             'font-family:SDK_ID_WEB}'
        #
        #                             'QPushButton:hover{background:rgb(20,20,20);'
        #                             'color:rgb(22,140,148)}'
        #
        #                             'QPushButton:pressed{background:rgb(0,0,0)}')
#-------------------------------------------------------------------------------------------

        background_squad = QLabel(page_battle)
        background_squad.setGeometry(20, 100, 220, 30)
        background_squad.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_squad = QLabel('预备编队', page_battle)
        label_squad.setGeometry(25, 95, 100, 40)
        label_squad.setStyleSheet('font-size:15px')

        self.combo_squad = QComboBox(page_battle)
        self.combo_squad.setGeometry(138, 102, 90, 25)
        self.combo_squad.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_squad.addItems([' 默认', ' 编队 1', ' 编队 2', ' 编队 3', ' 编队 4', ' 编队 5', ' 编队 6'])
        self.combo_squad.activated.connect(popup_tone_2) #音效
#------------------------------------------------------
        background_level = QLabel(page_battle)
        background_level.setGeometry(20, 65, 220, 30)
        background_level.setStyleSheet(
            'font-size:10px;background-color:rgb(206,206,206);border-radius:10px;padding:3px')

        label_level = QLabel('挑战等级', page_battle)
        label_level.setGeometry(25, 60, 100, 40)
        label_level.setStyleSheet('font-size:15px')

        self.combo_level = QComboBox(page_battle)
        self.combo_level.setGeometry(138, 67, 90, 25)
        self.combo_level.setStyleSheet('font-size:15px;background-color:rgb(216,216,216)')
        self.combo_level.addItems([' 默认', ' 满级', ])
        self.combo_level.activated.connect(popup_tone_2) #音效

        # ---------------------------------------------------------------------------------------------------------------
        self.label_drag = QLabel(self)
        self.label_drag.setGeometry(2, 3, 255, 28)
        self.label_drag.setStyleSheet('background:transparent')

        self.timer_save_config = QTimer()
        self.timer_save_config.timeout.connect(self.save_config)
        self.timer_save_config.start(100)  # 启动并设置间隔毫秒

        self.is_dragging = False

        load_config() # 在UI组件初始化后再load

    # ---------------------------------------------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.pos()
            self.is_dragging = True

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.label_drag.geometry().contains(event.position().toPoint()):
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def save_config(self):
        settings = {"check_coffee": self.check_coffee.isChecked(),
                    "combo_task": self.combo_task.currentIndex(),
                    "game_path": self.label_show_path.text(),
                    "server": self.combo_server.currentIndex(),
                    "shutdown": self.combo_shutdown.currentIndex(),
                    "speed": self.combo_speed.currentIndex(),
                    "check_reward": self.check_reward.isChecked(),
                    "check_lottery": self.check_lottery.isChecked(),
                    "combo_squad": self.combo_squad.currentIndex(),
                    "combo_level": self.combo_level.currentIndex(),
                    "combo_hollow_date":self.combo_date.currentIndex(),
                    "combo_hollow_round":self.combo_round.currentIndex(),
                    "combo_hollow_type":self.combo_type.currentIndex(),
                    "developer_mode":self.developer_mode} # json中True写作true,非法格式会导致属性错误

        with open(os.path.join(config_path(),"config.json"), 'w') as f:
            json.dump(settings, f,indent=4)


if __name__ == '__main__':
    app = QApplication()

    QFontDatabase.addApplicationFont(RP.path('gui/fonts/zh-cn.ttf'))
    QFontDatabase.addApplicationFont(RP.path('fonts/id-id.ttf'))
    global_font = QFont()
    global_font.setFamily('SDK_SC_WEB')
    global_font.setPointSize(10)
    app.setFont(global_font)

    window = ZA()
    window.show()
    app.exec()