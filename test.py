from tools import imageRec
if __name__ == '__main__':
    ocrtest = imageRec('阴阳师-网易游戏',[])
    result = ocrtest.ocr([1016,109,1092,134])
    print(result)