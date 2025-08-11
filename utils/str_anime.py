import time

class StrAnime:
    def __init__(self,delay):
        self.delay=delay   #间隔

    def play(self,str):
        for character in str:
            time.sleep(self.delay)
            print(character,end="",flush=True)
        print()

def cprint(text, color):
    print(f"\033[{color}m{text}\033[0m")  # ANSI转义码 标准30-37 高亮90-97


if __name__=="__main__":
    pass