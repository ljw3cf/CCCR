import pyaudio
import wave
import time
import boto3
import os
import json
import urllib
import cv2
import sys
import subprocess
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from tempfile import gettempdir

# 여러 용도로 사용할 시스템타임의 변수처리 (형식: 년-월-일-시-분-초)
System_Time = time.strftime("%Y-%m-%d-%H-%M-%S")
WAVE_OUTPUT_FILENAME =  System_Time + ".wav"

#S3 사용하기 위한 변수들
BUCKET_NAME = "transcriberecord"

#transcribe용 변수 지정
transcribe = boto3.client('transcribe')
job_uri = "https://transcriberecord.s3-ap-northeast-1.amazonaws.com/"+ WAVE_OUTPUT_FILENAME
job_name = WAVE_OUTPUT_FILENAME

speech("원하는 기능을 말씀해주세요. %d 초 동안 녹음이 시작됩니다." % RECORD_SECONDS) 
time.sleep(5)
os.system('play -nq -t alsa synth {} sine {}'.format(0.5, 440))

speech("녹음이 종료되었습니다. 음성인식이 완료될 떄 까지 잠시만 기다려주세요.") 


#생성한 wav파일을 S3로 업로드 및 wav파일 삭제
S3.upload_file(WAVE_OUTPUT_FILENAME, BUCKET_NAME, WAVE_OUTPUT_FILENAME)
print("S3 업로드 완료")
time.sleep(3)

#S3 업로드 후 wav파일 삭제 
os.remove(WAVE_OUTPUT_FILENAME)

while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("STT 진행 중... 끄지 마숑..")
    time.sleep(5)

open_json = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
data = json.loads(open_json.read())
text = data['results']['transcripts'][0]['transcript']
print("Transcribe 결과 " + "\"" + text + "\"")

##기능구분용 변수들
등록 = "등"
출석 = "출"
퇴실 = "퇴"

#cv2 변수지정
cap = cv2.VideoCapture(0)
count = 0
IMAGE_BUCKET = "cccr-image"
TEXT_BUCKET = "cccr-message"

#transcribe 결과에 따른 별도절차 진행
if text[0:1] == 등록:
    speech("등록절차를 진행합니다. 카메라 위치에 얼굴을 맞춰주세요.")
#    print("등록절차 진행...")
    time.sleep(2)
    print("사진촬영을 시작합니다.")
    while cap.isOpened():
    # 카메라 프레임 읽기
        success, frame = cap.read()
        if success:
            # 프레임 출력
            cv2.imshow('Camera Window', frame)
            if(int(cap.get(1)) % 1 == 0):
                cv2.imwrite("./IN-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count), frame)
                count += 1
            # ESC를 누르면 종료
            if (count == 101): 
                break
    cap.release()
    cv2.destroyAllWindows()    

    # 이미지를 s3에 업로드
    count -= 1
    IMAGE_OUTPUT_FILENAME = "IN-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count)
    
    print(IMAGE_OUTPUT_FILENAME)
    S3.upload_file(IMAGE_OUTPUT_FILENAME, IMAGE_BUCKET, IMAGE_OUTPUT_FILENAME)
    print("이미지 S3 업로드 완료")
    time.sleep(5)

    JSON_DATA = S3.get_object(Bucket=TEXT_BUCKET, Key="%s.json" % IMAGE_OUTPUT_FILENAME)
    JSON_TEXT = json.loads(JSON_DATA['Body'].read())
    RESULTS = JSON_TEXT["Text"]
    speech(RESULTS)
elif text[0:1] == 출석: 
    speech("출석절차를 진행합니다. 카메라 위치에 얼굴을 맞춰주세요.")
    print("사진촬영을 시작합니다.")
    while cap.isOpened():
    # 카메라 프레임 읽기
        success, frame = cap.read()
        if success:
            # 프레임 출력
            cv2.imshow('Camera Window', frame)
            if(int(cap.get(1)) % 1 == 0):
                cv2.imwrite("./CI-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count), frame)
                count += 1
            # ESC를 누르면 종료
            if (count == 100): 
                break
    cap.release()
    cv2.destroyAllWindows()    

    # 이미지를 s3에 업로드
    count -= 1  
    IMAGE_OUTPUT_FILENAME = "CI-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count)

    print(IMAGE_OUTPUT_FILENAME)
    S3.upload_file(IMAGE_OUTPUT_FILENAME, IMAGE_BUCKET, IMAGE_OUTPUT_FILENAME)
    print("이미지 S3 업로드 완료")
    time.sleep(5)

    JSON_DATA = S3.get_object(Bucket=TEXT_BUCKET, Key="%s.json" % IMAGE_OUTPUT_FILENAME)
    JSON_TEXT = json.loads(JSON_DATA['Body'].read())
    RESULTS = JSON_TEXT["Text"]
    speech(RESULTS)
elif text[0:1] == 퇴실:
    speech("퇴실절차를 진행합니다. 카메라 위치에 얼굴을 맞춰주세요.")
    print("퇴실절차 진행...")
    print("사진촬영을 시작합니다.")
    while cap.isOpened():
    # 카메라 프레임 읽기
        success, frame = cap.read()
        if success:
            # 프레임 출력
            cv2.imshow('Camera Window', frame)
            if(int(cap.get(1)) % 1 == 0):
                cv2.imwrite("./CO-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count), frame)
                count += 1
            # ESC를 누르면 종료
            if (count == 100): 
                break
    cap.release()
    cv2.destroyAllWindows()    

    # 이미지를 s3에 업로드
    count -= 1  
    IMAGE_OUTPUT_FILENAME = "CO-%s%d.jpg" % (WAVE_OUTPUT_FILENAME, count)

    print(IMAGE_OUTPUT_FILENAME)
    S3.upload_file(IMAGE_OUTPUT_FILENAME, IMAGE_BUCKET, IMAGE_OUTPUT_FILENAME)
    print("이미지 S3 업로드 완료")    
    time.sleep(5)

    JSON_DATA = S3.get_object(Bucket=TEXT_BUCKET, Key="%s.json" % IMAGE_OUTPUT_FILENAME)
    JSON_TEXT = json.loads(JSON_DATA['Body'].read())
    RESULTS = JSON_TEXT["Text"]
    speech(RESULTS)
else:
    speech("음성을 인식하지 못했습니다. 다시 한번 시도해주세요.")