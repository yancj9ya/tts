import os
from base import windowControl,kill_process_by_window_title
from tools import imageRec, Click
from time import sleep
from img.imginfo import *
from move import Move
from ocr import OCR

# 启动客户端
class TTS(imageRec, Move, OCR):
    def __init__(self, window_name, uilist):
        imageRec.__init__(self, window_name, uilist)
        Move.__init__(self, window_name)
        OCR.__init__(self)
        self.window_name = window_name
        self.had_flash = False
        self.max_jjk =None
        self.loop_signal = True
        self.next_time=None
        self.max_jjk_num=0
        self.app_path=None
        self.event=None
    @staticmethod
    def split_string_by_length(s, length):
        return [s[i:i+length] for i in range(0, len(s), length)]
        
    def client_start(self):
        if not self.get_hwnd_by_name(self.window_name):
            print('客户端未启动,开始启动客户端')
            
            start_path = 'cd '+self.app_path+'&&start Launch.exe'
            info=os.system(start_path)
            print(info)
            if info!=0:
                print('启动客户端失败')
                self.loop_signal=False
                return
            
            sleep(5)
            print('客户端已经启动,等待登录窗口')
            while not self.knnImage(chose_server):
                if not self.event.is_set():return
                sleep(1)
                if self.get_hwnd_by_name('登录'):
                    login = Click('登录')
                    login.areaClick(52, 314, 385, 358)
                    #print('选择服务器')
                    self.handle = self.get_hwnd_by_name('阴阳师-网易游戏')
                #print('等待登录窗口')
                sleep(1)
            return True
        else:return False

    def refresh_jywz(self):
        self.areaClick(304, 92, 383, 130)  # 点击跨区
        sleep(1)
        self.move(166, 170, 168, 489)  # 滑动到底刷新
        sleep(1)
        self.areaClick(201, 88, 279, 135)  # 点击好友
        sleep(1)
        self.areaClick(305, 87, 388, 134)  # 点击跨区
        # 刷新完成

    def put_in(self):
        print('开始蹲坑')
        while self.knnImage(ui_jjk):
            self.areaClick(716, 487, 850, 521)  # 进入结界
            sleep(2)
            self.areaClick(391, 447, 465, 580)  # 选择红蛋
            sleep(1)
            self.areaClick(605, 461, 696, 505)  # 确认选择
            self.loop_signal = False
            self.next_time=6*3600#6小时之后再次启动

    def find_jjk(self):
        self.areaClick(305, 87, 388, 134)  # 点击跨区
        
        search_area=[(460,157,548,238),(464,261,551,332),(465,355,548,423),(458,440,551,529)]
        for i in range(4):
            print(f'搜索第{i+1}个4个好友')
            for area in search_area:
                if self.duoKnnImage([tg_6x,tg_5x],area,sigleRETURN=True):
                    self.areaClick(*area)
                    sleep(1)
                    img = self.window_part_shot(self.handle, 736, 377, 838, 398)
                    result = self.ocr(img)
                    print(result)
                    if result[1] > 0.6:
                        jjk_type = result[0].split('+')[0]
                        jjk_num = int(result[0].split('+')[1])
                    if jjk_type == '勾玉':
                        #print(f'{jjk_type}:{jjk_num}')
                        if jjk_num ==76:self.put_in();return
                        if jjk_num >= self.max_jjk_num:self.max_jjk_num=jjk_num
                        if self.max_jjk is not None:
                            if jjk_num >= self.max_jjk:self.put_in();return
                    sleep(1)
            self.move(442, 484, 456, 164)
            sleep(1)
        if self.max_jjk is None and self.max_jjk_num>=59:
            self.max_jjk=self.max_jjk_num
            self.areaClick(201, 88, 279, 135)
            return
        else:
            sleep(1)
            #未能找到符合的结界卡
            self.loop_signal=False
            print('未能找到符合的结界卡')
            self.next_time=5*60#5分钟之后再次寻找

    def run(self):
        print('开始运行')
        if self.client_start():
            print('客户端已经启动')
        if not self.event.is_set():return
        while self.loop_signal:
            sleep(1)
            action = self.uiserch()
            #print(action)
            match action:
                case 'chose_server': self.areaClick(503,520,628,543)
                case 'ui_home':
                    if not self.knnImage(ui_yyl):
                        self.areaClick(1065, 538, 1111, 622)
                    else:
                        self.areaClick(*ui_yyl[1:])
                case 'ui_inyyl': self.areaClick(*ui_inyyl[1:])
                case 'ui_jjk':
                    if self.had_flash:
                        self.find_jjk()
                    else:
                        self.refresh_jywz()
                        self.had_flash = True
                case 'ui_jywz': self.areaClick(1022, 55, 1085, 114); sleep(1)
                case 'ui_injj': self.areaClick(536, 290, 572, 377)
                case 'ui_ssyc':
                    if self.knnImage(ui_jywz):self.areaClick(1022, 55, 1085, 114); sleep(1)
                    else:
                        
                        img = self.window_part_shot(self.handle, 1013,109,1070,133)
                        time_to_next = self.ocr(img)
                        print(time_to_next)
                        if time_to_next[0].isdigit() and time_to_next[1]>0.82 and len(time_to_next[0])==4:
                            res=self.split_string_by_length(time_to_next[0], 2)
                            self.next_time=int(res[0])*3600+int(res[1])*60
                            self.loop_signal=False
                        elif ':' in time_to_next[0] and time_to_next[1]>0.9 and len(time_to_next[0])==5:
                            res=time_to_next[0].split(':')
                            self.next_time=int(res[0])*3600+int(res[1])*60
                            self.loop_signal=False
                            
                        
                case None: continue#rint('no action')
                    
def ttu_jh(window,app_path,event):
    
    uilist = [chose_server, ui_home, ui_inyyl, ui_jjk, ui_jywz, ui_injj,ui_ssyc]
    tts = TTS('阴阳师-网易游戏', uilist)
    tts.event=event
    tts.set_variable(img_name_value)
    tts.app_path=app_path
    tts.run()
    print(tts.next_time)
    window['next_t'].update(value=tts.next_time)
    sleep(2)
    if tts.next_time!=None and tts.next_time > 300:
        kill_process_by_window_title('阴阳师-网易游戏')
    
if __name__ == '__main__':
    uilist = [chose_server, ui_home, ui_inyyl, ui_jjk, ui_jywz, ui_injj,ui_ssyc]
    tts = TTS('阴阳师-网易游戏', uilist)
    tts.set_variable(img_name_value)
    tts.run()
    print(tts.next_time)
