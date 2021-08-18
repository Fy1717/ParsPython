import cv2
import numpy as np

cam = cv2.VideoCapture(0)

while True:
    ret,kare = cam.read()
    gri_kare =cv2.cvtColor(kare, cv2.COLOR_BGR2GRAY)
    nesne = cv2.imread("asdf.png", 0)

    w, h = nesne.shape

    res= cv2.matchTemplate(gri_kare, nesne, cv2.TM_CCOEFF_NORMED)
    esik_degeri= 0.55
    loc = np.where(res > esik_degeri)

    if len(res):
        for n in zip(*loc[::-1]):
            cv2.rectangle(kare, n, (n[0]+h, n[1]+w), (0,255,0), 1)
            cv2.putText(kare,"Face", (n[0]+0, n[1]+110), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0) ,1)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    cv2.imshow('image', nesne)

    cv2.imshow("ekran", kare)

    if cv2.waitKey(25) & 0XFF == ord("q"):
        break
cam.release()   