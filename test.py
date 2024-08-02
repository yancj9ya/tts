from tools import imageRec,Click
from img.imginfo import ui_home,ui_injj,entry_game,chose_server

uilist=[ui_home]
img=imageRec('阴阳师-网易游戏',uilist)

res=img.knnImage(ui_injj)
print(res)
'''click=Click('登录')
handle=click.get_hwnd_by_name('登录')
print(handle)
click.areaClick(52,314,385,358)'''