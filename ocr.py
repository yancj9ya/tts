from ppocronnx.predict_system import TextSystem
from base import windowControl
from tools import Click
from time import sleep
class OCR(TextSystem):
    def __init__(self):
        TextSystem.__init__(self)
    
    
    def ocr(self,s_img):
        return self.ocr_single_line(s_img)
    
if __name__ == '__main__':
    ocr=OCR()
    Click=Click('阴阳师-网易游戏')
    img=Click.window_part_shot(Click.handle,1024,12,1082,43)
    sleep(0.5)
    print(ocr.ocr(img))
