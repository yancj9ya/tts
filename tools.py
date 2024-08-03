from base import windowControl
import os
import numpy as np
import cv2
import time  # type: ignore
from random import randint
from ppocronnx.predict_system import TextSystem

class Click(windowControl):
    def __init__(self, window_name, clickdelay=0.2):
        windowControl.__init__(self)
        self.window_name = window_name
        self.handle = self.get_hwnd_by_name(window_name)    
        self.clickdelay = clickdelay
    
    def click(self, coordinate):
        try:
            self.left_down(self.handle, *coordinate[:2])
            time.sleep(self.clickdelay)
            self.left_up(self.handle, *coordinate[:2])
        except Exception as e:
            print(f"点击操作失败: {e}")

    def areaClick(self, sx,sy,ex,ey):
        try:
            point_s_x, point_s_y,point_e_x , point_e_y = sx,sy,ex,ey
            rand_x = randint(point_s_x, point_e_x)
            rand_y = randint(point_s_y, point_e_y)
            self.left_down(self.handle, rand_x, rand_y)
            time.sleep(self.clickdelay)
            self.left_up(self.handle, rand_x, rand_y)
        except Exception as e:
            print(f"区域点击操作失败: {e}")

class imageRec(Click,TextSystem):
    def __init__(self, window_name,uiList):
        Click.__init__(self,window_name)
        TextSystem.__init__(self)
        self.uilist = uiList
        self.ui_delay = 0.8

    def ocr(self, area):
        try:
            return self.ocr_single_line(self.window_part_shot(self.handle, *area))
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None


    def getSIFT(self, imgsrc: str):
        imgsrc_dir = os.path.dirname(imgsrc)
        imgName = os.path.basename(imgsrc)
        npypath = os.path.join(imgsrc_dir, 'sift', f'{imgName}.npy')

        try:
            if os.path.exists(npypath):
                return np.load(npypath)
            else:
                print('不存在sift_npy文件，创建sift_npy文件')
                sift_dir = os.path.join(imgsrc_dir, 'sift')
                os.makedirs(sift_dir, exist_ok=True)
                print(f"文件夹 '{sift_dir}' 成功创建")

                trainingImage = cv2.imread(imgsrc, cv2.IMREAD_GRAYSCALE)
                sift = cv2.SIFT_create()
                kp2, des2 = sift.detectAndCompute(trainingImage, None)

                np.save(npypath, des2)
                print(f'成功保存sift文件:\n{npypath}')
                return des2
        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def knnImage(self, img, accuracy=0.4):
        try:
            shot_img = self.window_part_shot(self.handle, *img[1:5])
            queryImage = cv2.cvtColor(shot_img, cv2.COLOR_BGRA2GRAY)
            sift = cv2.SIFT_create()
            kp1, des1 = sift.detectAndCompute(queryImage, None)
            des2 = self.getSIFT(img[0])

            if des2 is None:
                return None

            flann = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 5}, {'checks': 50})
            matches = flann.knnMatch(des1, des2, k=2)

            good = [m for m, n in matches if m.distance < accuracy * n.distance]

            if good:
                s = sorted(good, key=lambda x: x.distance)
                loc = len(s) // 2
                maxLoc = kp1[s[loc].queryIdx].pt
                return [int(maxLoc[0]) + img[1], int(maxLoc[1]) + img[2], img[0]]
            return None
        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def duoKnnImage(self, imgList, area, accuracy=0.4, sigleRETURN=False):
        try:
            shot_img = self.window_part_shot(self.handle, *area)
            queryImage = cv2.cvtColor(shot_img, cv2.COLOR_BGRA2GRAY)
            sift = cv2.SIFT_create()
            kp1, des1 = sift.detectAndCompute(queryImage, None)

            flann = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 5}, {'checks': 50})
            matchList = []

            for img in imgList:
                des2 = self.getSIFT(img[0])
                if des2 is None:
                    continue

                matches = flann.knnMatch(des1, des2, k=2)
                good = [m for m, n in matches if m.distance < accuracy * n.distance]

                if good:
                    if sigleRETURN:
                        return img[0].split('/')[-1].split('.')[0]
                    matchList.append(img[0].split('/')[-1].split('.')[0])
            return matchList
        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def templateMatchImage(self, img, accuracy=0.8):
        try:
            ShotImage = cv2.cvtColor(self.window_part_shot(self.handle, *img[1:5]), cv2.COLOR_BGRA2GRAY)
            template = cv2.imread(img[0], cv2.IMREAD_GRAYSCALE)
            Res = cv2.matchTemplate(ShotImage, template, cv2.TM_CCOEFF_NORMED)

            if cv2.minMaxLoc(Res)[1] > accuracy:
                matchCor = cv2.minMaxLoc(Res)[3]
                h, w = template.shape
                s_X = img[1] + matchCor[0]
                s_Y = img[2] + matchCor[1]
                e_X = w + s_X
                e_Y = h + s_Y
                return [s_X, s_Y, e_X, e_Y]
            return None
        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def DuoImgMatch(self, dir, imgL, area, acc=0.99):
        for imgN in imgL:
            imgpath = os.path.join(dir, imgN)
            res = self.templateMatchImage([imgpath, *area], accuracy=acc)
            if res:
                print(f"匹配到{imgN}，\n坐标为{res}")
                return (imgpath, res[0] - 5, res[1] - 5, res[2] + 5, res[3] + 5)
        return None
    def set_variable(self,varible):
        self.local_img_var = varible
    def get_img_name(self, variable, variable_name=None):
        try:
            if variable_name is not None:
                return variable_name
            for name, value in self.local_img_var.items():
                #print(name, value)
                if value is variable:
                    return name
            return None  # 如果没有找到变量名，返回None
        except Exception as e:
            print(f"获取变量名时发生错误: {e}")
            return None

    def uiserch(self):
        for curr_img in self.uilist:
            #print(f"正在搜索{curr_img[0]}")
            res = self.knnImage(curr_img,accuracy=0.4)
            if res is not None:
                return self.get_img_name(curr_img)
        return None


class Counter:
    def __init__(self):
        try:
            self.count = 0
            self.count1 = 0
            self.start_time = time.time()
            self.start_time1 = time.time()
        except Exception as e:
            print(f"Initialization Error: {e}")

    def increment(self, interval=4):
        try:
            current_time = time.time()
            if current_time - self.start_time > interval:
                self.count += 1
                self.start_time = current_time
                return True
            else:
                return False
        except Exception as e:
            print(f"Increment Error: {e}")

    def increment1(self, interval=5):
        try:
            current_time = time.time()
            if current_time - self.start_time1 > interval:
                self.count1 += 1
                self.start_time1 = current_time
                return True
            else:
                return False    
        except Exception as e:
            print(f"Increment1 Error: {e}")

    def reset(self):
        try:
            self.count = 0
            self.count1 = 0
        except Exception as e:
            print(f"Reset Error: {e}")