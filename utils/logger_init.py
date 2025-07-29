from loguru import logger
from datetime import datetime
import sys
#---------------------------------------------
from config.load_config import developer_mode
from utils.resource_path import ResourcePath
#-------------------------------------------------

RPL=ResourcePath("logs", "config")
#-----------------------------------------------------
if developer_mode:
    logger_level="TRACE"
else:
    logger_level="DEBUG"

logger.remove()  # 移除默认版本logger输出
timestamp = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
logger.add(sink=sys.stdout,
           format="<light-black>{time:YYYY-MM-DD HH:mm:ss}</light-black> [<level>{level}</level>] <level>{message}</level>",
           colorize=True, level=logger_level)  # 格式化logger
logger.add(sink=RPL.file(f"{timestamp}.log"),
           format="<light-black>{time:YYYY-MM-DD HH:mm:ss}</light-black> [<level>{level}</level>] <level>{message}</level>",
           level="TRACE")
logger.level("INFO", color="<white>")  # 修改level默认颜色
logger.level("WARNING", color="<light-yellow>")
logger.level("DEBUG", color="<light-black>")
logger.level("SUCCESS", color="<light-green>")
logger.level("ERROR", color="<light-red>")

if __name__=="__main__":
    pass
