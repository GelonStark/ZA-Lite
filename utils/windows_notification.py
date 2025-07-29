import plyer.platforms.win.notification  #plyer是跨平台动态检测需要显式静态导入
from plyer import notification

class WindowsNotification:
    def __init__(self,icon_path):
        self.icon_path=icon_path

    def push(self,title,message):
        notification.notify(
            title=title,
            message=message,
            app_icon=self.icon_path
        )

if __name__=="__main__":
    a=WindowsNotification("../gui/images/icon.ico")
    a.push("123","dsads")
