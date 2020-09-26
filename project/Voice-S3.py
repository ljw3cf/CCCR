#강길씨를 위한 프레젠트
import pyaudio
import wave
import time
import boto3
import os

#녹음에 필요한 변수
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

#WAVE로 녹음파일 생성 시, 날짜를 파일명으로 지정하기 위한 변수
RECORD_TIME = time.ctime()
MODIFIED_WAVE_OUTPUTNAME = RECORD_TIME.replace(" ", "-")
WAVE_OUTPUT_FILENAME =  MODIFIED_WAVE_OUTPUTNAME.replace(":", "-") + ".wav"

#S3 사용하기 위한 변수들
S3 = boto3.client("s3")
BUCKET_NAME = "transcriberecord"

#pyaudio 라이브러리로 녹음데이터를 frames에 떄려박는 함수들
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print(str(RECORD_SECONDS) + "초 동안 녹음이 시작됩니다...")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("녹음이 종료되었습니다.")

stream.stop_stream()
stream.close()
p.terminate()

#저장된 프레임을 기반으로 wav파일 생성
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

#생성한 wav파일을 S3로 업로드
S3.upload_file(WAVE_OUTPUT_FILENAME, BUCKET_NAME, WAVE_OUTPUT_FILENAME)
print("S3 업로드 완료")

#S3 업로드 후 wav파일 삭제 
os.remove(WAVE_OUTPUT_FILENAME)
