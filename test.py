from tools import imageRec
import cv2
class test(imageRec):
    def __init__(self,gamename,game_ui):
        super(imageRec,self).__init__(gamename,game_ui)
        
    def knnImage(self, img, accuracy=0.4):
        try:
            shot_img = self.window_part_shot(self.handle, *img[1:5])
            #queryImage = cv2.cvtColor(shot_img, cv2.COLOR_BGRA2GRAY)
            sift = cv2.SIFT_create()
            kp1, des1 = sift.detectAndCompute(shot_img, None)
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

if __name__ == '__main__':
    test = test("阴阳师-网易游戏",None)
    test_img=('img/test.bmp',466,161,546,529)
    img = test.allImgMatch([test_img,],[158,161,275,540],accuracy=0.9)
    print(img)