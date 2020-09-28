import pyaudio
import wave
import time
import boto3
import os
import json
import urllib
import cv2
import pymysql

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
print("원하는 기능을 말씀해주세요. (등록/출석/퇴실)")
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

#transcribe용 변수 지정
transcribe = boto3.client('transcribe')
job_uri = "https://transcriberecord.s3-ap-northeast-1.amazonaws.com/"+ WAVE_OUTPUT_FILENAME
job_name = WAVE_OUTPUT_FILENAME

#transcribe 호출    
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='ko-KR'
)
#transcribe 완료될 동안 메세지 표시...
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("STT 진행 중... 끄지 마숑..")
    time.sleep(5)

#transcribe 결과 표시
open_json = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
data = json.loads(open_json.read())
text = data['results']['transcripts'][0]['transcript']
print("Transcribe 결과 " + "\"" + text + "\"")

#기능구분용 변수들
등록 = "등"
출석 = "출"
퇴실 = "퇴"

#cv2 변수지정
cap = cv2.VideoCapture(0)
count = 0

#rekongnition용 변수지정
rekognition = boto3.client('rekognition')
collection_id = "cccr_collection"
threshold = 90
IMAGE_BUCKET = "cccr-image"

#mariadb용 변수지정
ENDPOINT = "test.cumohhkhvfrn.ap-northeast-1.rds.amazonaws.com"
PORT = 3306
USR = "admin"
REGION = "ap-northeast-1"
DBNAME = "ljw_test"
DBPASS = "dkagh1.."
rds = boto3.client('rds')
conn = pymysql.connect(host = ENDPOINT, user=USR, passwd=DBPASS, port=PORT, database=DBNAME)
cur = conn.cursor()

#transcribe 결과에 따른 별도절차 진행
if text[0:1] == 등록:
    print("등록절차 진행...")
    time.sleep(2)
    print("사진촬영을 시작합니다.")
    while cap.isOpened():
    # 카메라 프레임 읽기
        success, frame = cap.read()
        if success:
            # 프레임 출력
            cv2.imshow('Camera Window', frame)
            if(int(cap.get(1)) % 1 == 0):
                cv2.imwrite("./%s%d.jpg" % (MODIFIED_WAVE_OUTPUTNAME.replace(":", "-"), count), frame)
                count += 1
            # ESC를 누르면 종료
            if (count == 100): 
                break
    cap.release()
    cv2.destroyAllWindows()    

    # 이미지를 s3에 업로드
    count -= 1
    IMAGE_OUTPUT_FILENAME = "%s%d.jpg" % (MODIFIED_WAVE_OUTPUTNAME.replace(":", "-"), count)

    print(IMAGE_OUTPUT_FILENAME)
    S3.upload_file(IMAGE_OUTPUT_FILENAME, IMAGE_BUCKET, IMAGE_OUTPUT_FILENAME)
    print("이미지 S3 업로드 완료")

    indexing = rekognition.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
	#index_face 결과 표시
    print('Faces indexed:')						
    for faceRecord in indexing['FaceRecords']:
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
         FaceID = faceRecord['Face']['FaceId']
    print('Faces not indexed:')
    for unindexedFace in indexing['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    print('  당신의 Face ID는?: ' + faceRecord['Face']['FaceId'])
        
    #학생정보 inserts
    print('학생정보 DB Insert 시작')
    add_student = ("INSERT INTO student "
                   "(Name, FaceID, Class) "
                   "VALUES (%(Name)s,%(FaceID)s,%(Class)s)")
    Class = text[3:5]
    Student_Name = text[6:]

    data_student = {
        "FaceID": FaceID,
        "Name": Student_Name,
        "Class": Class
    }

    cur.execute(add_student, data_student)
    conn.commit()
    cur.close()
    conn.close()
    print('학생정보 DB 등록 완료')   

elif text[0:1] == 출석: 
    print("출석절차 진행...")
    print("사진촬영을 시작합니다.")
    while cap.isOpened():
    # 카메라 프레임 읽기
        success, frame = cap.read()
        if success:
            # 프레임 출력
            cv2.imshow('Camera Window', frame)
            if(int(cap.get(1)) % 1 == 0):
                cv2.imwrite("./%s%d.jpg" % (MODIFIED_WAVE_OUTPUTNAME.replace(":", "-"), count), frame)
                count += 1
            # ESC를 누르면 종료
            if (count == 100): 
                break
    cap.release()
    cv2.destroyAllWindows()    

    # 이미지를 s3에 업로드
    count -= 1  
    IMAGE_OUTPUT_FILENAME = "%s%d.jpg" % (MODIFIED_WAVE_OUTPUTNAME.replace(":", "-"), count)

    print(IMAGE_OUTPUT_FILENAME)
    S3.upload_file(IMAGE_OUTPUT_FILENAME, IMAGE_BUCKET, IMAGE_OUTPUT_FILENAME)
    print("이미지 S3 업로드 완료")

    search_faces = rekognition.search_faces_by_image(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=1)
                                
    print ('Matching faces')
    for match in search_faces['FaceMatches']:
            face_id = match['Face']['FaceId']
            print ('당신의 FaceId: %s' % face_id)
            print ('원본 사진과 유사도: ' + "{:.2f}".format(match['Similarity']) + "%")
    
    # DB에서 해당하는 학생 검색
    select_student = ("SELECT id,Name,Class from student where FaceID='%s'" % face_id) 
    cur.execute(select_student)
    table = cur.fetchall()     
    for student_data in table:
        print(student_data)
    cur.close
    conn.close

elif text[0:1] == 퇴실:
    print("퇴실절차 진행...")
    search_faces = rekognition.search_faces_by_image(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=1)
                                
    print ('Matching faces')
    for match in search_faces['FaceMatches']:
            print ('당신의 FaceId:' + match['Face']['FaceId'])
            print ('원본 사진과 유사도: ' + "{:.2f}".format(match['Similarity']) + "%")

else:
    print("먼가... 먼가... 메세지가 이상해!!")