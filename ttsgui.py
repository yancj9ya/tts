import PySimpleGUI as sg
from ctypes import windll
from tunts import ttu_jh
from random import randint
import time
import pystray
from PIL import Image
from threading import Event
sg.theme('DarkGreen')
setting=sg.UserSettings(filename='settings.ini',path='.',use_config_file=True,convert_bools_and_none=True, autosave=True)
windll.user32.SetProcessDPIAware()

t_title = sg.Text('Tuntunshu', font=('Arial', 20))
on_off = sg.Button('start',k='on_off',size=(10, 1),p=1)
tprint=sg.Multiline(k='console',size=(30,20),text_color='green',background_color='black',font='consolas',
                    expand_x=True,expand_y=True,border_width=1,
                    no_scrollbar=True,autoscroll=True,
                    reroute_stderr=True,reroute_stdout=True) 
next_t=sg.Input(k='next_t',setting=0)
text_t=sg.Input(k='text_t',setting=0)
sepline=sg.HorizontalSeparator(color='white',p=0)
app_path=sg.FolderBrowse(k='app_path',visible=True,size=(10, 1),p=1,enable_events=True)
app_pathtext=sg.Input(setting['path'].get('input1'),k='path',font=('Arial', 10))
layout=[[t_title],[sepline],[app_path,app_pathtext],[on_off,next_t],[text_t],[tprint]]

btn_name={}
next_time=10000000
start_time=int(time.time())-30
window=sg.Window('Tuntunshu',icon='icon.ico',layout=layout,size =(300,400),auto_save_location=True,enable_close_attempted_event=True)
#sg.SystemTray.notify('Notification Title', 'This is the notification message')
def on_close():
    icon.stop()
    #window.close()
    
menu=(
    pystray.MenuItem('Show', lambda :window.un_hide()),
    pystray.MenuItem('Exit', lambda :on_close()),
)
image=Image.open('icon.ico')
icon=pystray.Icon('tuntunshu',image,'tuntunshu',menu=menu)
window.perform_long_operation(lambda :icon.run(),'stray')
stop_event=Event()
while True:
    event, values = window.read(timeout=1000,timeout_key='timeout')
    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'exit': # if user closes window or clicks cancel
        window.hide()
        setting['path'].set('input1',values['path'])
    if event == 'on_off':
        if window[event].get_text()=='Stop':window[event].update(text=btn_name[event],button_color=('Green','#d5d283'));stop_event.clear()
        else:
            stop_event.set()
            btn_name[event]=window[event].get_text()
            window[event].update(text='Stop',button_color=('white','red'))
            window.perform_long_operation(lambda :ttu_jh(window,values['path'],stop_event),'mission_end')
            #
    elif event=='mission_end':
        start_time=int(time.time())
        next_time=values['next_t']
    elif event=='stray':break
    elif event=='app_path':
        app_pathtext.update(value=values['app_path'])
    elif event == 'timeout':
            if window['on_off'].get_text()=='Stop':
                to_time=int(next_time)-(int(time.time())-start_time)
                window['text_t'](value=f'Count to next mission :{time.strftime("%H:%M:%S", time.gmtime(to_time))} ')
                if int(next_time)-(int(time.time())-start_time)==1:icon.notify(f'将会在30sk后开始自动蹭太鼓','屯屯鼠提示：',)
                if time.time()-start_time-int(next_time)>randint(30,60):
                    window.perform_long_operation(lambda :ttu_jh(window,values['path'],stop_event),'mission_end')
                    next_time=100000000
   
window.close()