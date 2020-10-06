import cv2
import boto3

S3 = boto3.client("s3")

cap = cv2.VideoCapture(0)   # 0: default camera
#cap = cv2.VideoCapture("test.mp4") #동영상 파일에서 읽기
 
count = 0
while cap.isOpened():
    # 카메라 프레임 읽기
    success, frame = cap.read()
    if success:
        # 프레임 출력
        cv2.imshow('Camera Window', frame)
        if(int(cap.get(1)) % 1 == 0):
            cv2.imwrite("./frame%d.jpg" % count, frame)
            count += 1
        # ESC를 누르면 종료
        key = cv2.waitKey(1) & 0xFF
        if (key == 27): 
            break
 
cap.release()
cv2.destroyAllWindows()

count -= 1
BUCKET_NAME = "transcriberecord"
IMAGE_OUTPUT_FILENAME = "frame%d.jpg" % count

print(IMAGE_OUTPUT_FILENAME)
S3.upload_file(IMAGE_OUTPUT_FILENAME, BUCKET_NAME, IMAGE_OUTPUT_FILENAME)
print("S3 업로드 완료")
