import threading
from loguru import logger
import traceback

def thread_error(args):
    # logger.error(f"【线程出错】{args.thread.name}")
    # logger.error(f"【错误类型】{args.exc_type}")
    # logger.error(f"【错误信息】{args.exc_value}")
    logger.error(f"【线程错误】{args.thread.name}\n\n{traceback.format_exc()}")

threading.excepthook = thread_error


if __name__=="__main__":
    def worker():
        1/0
    thread=threading.Thread(target=worker)
    thread.start()

