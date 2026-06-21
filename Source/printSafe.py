import datetime
import threading
from colorama import Fore , Style

class Printer:
    def __init__(self) -> None:
        self.Lock = threading.Lock()
    
    def CurrTime(self):
        data = datetime.datetime.now().strftime("%H:%M:%S")
        return data

    def success(self , title: str , desc: str):
        self.Lock.acquire()
        time = Printer.CurrTime(self)
        print(
            f"""{Fore.LIGHTBLACK_EX}[{time}] {Fore.LIGHTBLUE_EX}{title}{Fore.LIGHTWHITE_EX} : {Fore.LIGHTGREEN_EX}{desc}{Style.RESET_ALL}"""
        )
        self.Lock.release()

    def denied(self , title: str , desc: str):
        self.Lock.acquire()
        time = Printer.CurrTime(self)
        print(
            f"""{Fore.LIGHTBLACK_EX}[{time}] {Fore.LIGHTYELLOW_EX}{title}{Fore.LIGHTWHITE_EX} : {Fore.LIGHTRED_EX}{desc}{Style.RESET_ALL}"""
        )
        self.Lock.release()
