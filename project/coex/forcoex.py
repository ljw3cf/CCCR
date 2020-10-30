import time
import os
import cv2
import rasp_function
import Seeed_AMG8833
from thermal_cam import thermal_cam
from threading import Thread

#cv2 변수리스트
cap = cv2.VideoCapture(0)

# Cascades 디렉토리의 haarcascade_frontalface_default.xml 파일을 Classifier로 사용
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#온도센서 기능 호출을 위한 변수
sensor = Seeed_AMG8833.AMG8833

#cv2 스트리밍 함수
def streaming():
    time.sleep(2)
    while True:
        success, image = cap.read()
        ''' 
        cascade에서는 얼굴을 찾기 위해 원본 이미지를 꼭 gray색상으로 변환해야 한다고 한다.
        cv2의 cvtColor모듈을 사용하여 프레임을 gray로 변환한 변수를 지정한다.
        '''
        frame = cv2.flip(image, 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray변수에서 얼굴 데이터를 추출
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize=(20, 20)
        )
        for (x,y,w,h) in faces:
            # 추출된 데이터에서 Topleft, Bottomright 값을 받아서 사각형을 그리기
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            # 얼굴에 그려진 사각형 안쪽의 범위를 지정
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            # 얼굴에 그려진 사각형 안쪽 범위에서 눈 데이터를 추출
            eyes = eyeCascade.detectMultiScale(roi_color)
            # 추출된 데이터에서 Topleft, Bottomright 값을 받아서 사각형 그리기
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh),
                (0,255,0), 2)
        if success:
            cv2.imshow("Help_Me_Hongs", image)
            key = cv2.waitKey(1) 
            if key == ord("q"):
                cv2.destroyAllWindows
                break

#메인함수
def main_function():
    temp = '%0.2f' % Seeed_AMG8833.cal_temp
    rasp_function.speech("안녕하세요! 측정된 체온은 %s 도 입니다!" % temp) 
    time.sleep(6)

def judge():
    while True:
        success, img = cap.read()
        if success:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor = 1.2,
                minNeighbors = 5,
                minSize=(20, 20)
            )
            for (x,y,w,h) in faces:
                if 180 < w and 180 < h:
                    print("인식 성공")
                    main_function()

if __name__ == "__main__":
    t1 = Thread(target=streaming)
    t2 = Thread(target=thermal_cam)
    t3 = Thread(target=judge)
    t1.start()
    t2.start()
    t3.start()
