import pymysql
import boto3
import json

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

#기능구분용 변수들
INDEX = "IN"
CHECK_IN = "CI"
CHECK_OUT = "CO"


def index(IMAGE_OUTPUT_FILENAME):
# 얼굴 인덱싱
    INDEXING = rekognition.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
    for FACERECORD in INDEXING['FaceRecords']:
        FACEID = FACERECORD['Face']['FaceId']
    print('Indexed FaceID : ' + FACEID)
    print('학생정보 DB Insert 시작')

# 
    add_student = ("INSERT INTO student "
                   "(Name, FaceID, Class) "
                   "VALUES (%(Name)s,%(FaceID)s,%(Class)s)")
    TEXT = IMAGE_OUTPUT_FILENAME[2:-7]
    CLASS = TEXT[3:5]
    STUDENT_NAME = TEXT[6:]

    data_student = {
        "FaceID": FACEID,
        "Name": STUDENT_NAME,
        "Class": CLASS
    }

    cur.execute(add_student, data_student)
    conn.commit()
    cur.close()
    conn.close()
    print('학생정보 DB 등록 완료')       
    return STUDENT_NAME

def check_in(IMAGE_OUTPUT_FILENAME):
    SEARCHING = rekognition.search_faces_by_image(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=1)
                                
    print ('Matching faces')
    for match in SEARCHING['FaceMatches']:
        face_id = match['Face']['FaceId']
        print ('당신의 FaceId: %s' % face_id)
        print ('원본 사진과 유사도: ' + "{:.2f}".format(match['Similarity']) + "%")
    
    # DB에서 해당하는 학생정보 변수처리
    select_student = ("SELECT id,Name,Class from student where FaceID='%s'" % face_id) 
    cur.execute(select_student)
    student_table = cur.fetchall()     
    for student_data in student_table:
        Student_Id = student_data[0]
        Student_Name = student_data[1]
        Student_Class = student_data[2]
        print("학생명은 " + Student_Name)

    # 출석 온도(라즈베리파이 온도측정기능 확인시 변경할 것)
    Check_In_Temp = 36.5

    # 오늘 출석기록이 이미 존재하는가 확인
    select_check_in = ("SELECT * FROM check_in_out WHERE studentID=%s " 
                 "AND check_in_time LIKE '%s%%'" %(Student_Id,System_Time[:10]))
    check_in_result = cur.execute(select_check_in)
    # 출석기록 없을 떄 insert 처리
    if check_in_result == 0:
        add_check = ("INSERT INTO check_in_out  "
                       "(check_in_time, check_in_temp, studentID) "
                       "VALUES ('%s', '%f', '%s')" %(System_Time, Check_In_Temp, Student_Id))
        cur.execute(add_check)
        conn.commit()
        print("출석기록이 db에 저장되었습니다.")
        cur.close
        conn.close
    else:
        print("출석기록이 이미 존재합니다.")
        cur.close
        conn.close
    return Student_Name
def check_out():
    SEARCHING = rekognition.search_faces_by_image(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':IMAGE_BUCKET,'Name':IMAGE_OUTPUT_FILENAME}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=1)
                                
    print ('Matching faces')
    for match in SEARCHING['FaceMatches']:
            face_id = match['Face']['FaceId']
            print ('당신의 FaceId: %s' % face_id)
            print ('원본 사진과 유사도: ' + "{:.2f}".format(match['Similarity']) + "%")
    
    # DB에서 해당하는 학생정보 변수처리
    select_student = ("SELECT id,Name,Class from student where FaceID='%s'" % face_id) 
    cur.execute(select_student)
    student_table = cur.fetchall()     
    for student_data in student_table:
        Student_Id = student_data[0]
        Student_Name = student_data[1]
        Student_Class = student_data[2]
        print("학생명은 " + Student_Name)

    # 출석 온도(라즈베리파이 온도측정기능 확인시 변경할 것)
    Check_In_Temp = 36.5

    # 여러 용도로 사용할 시스템타임의 변수처리 (형식: 년-월-일)
    System_Time = time.strftime("%Y-%m-%d %H:%M:%S")

    # 오늘 출석기록이 이미 존재하는가 확인
    select_check_in = ("SELECT * FROM check_in_out WHERE studentID='%s' "
                 "AND check_in_time LIKE '%s%%'" % (Student_Id, System_Time[:10]))
    check_in_result = cur.execute(select_check_in)
    # 출석기록이 없는 경우
    if check_in_result == 0:
        print("출석기록이 없습니다. 출석부터 해주세용")
        cur.close()
        conn.close()
    # 출석기록이 존재하는 경우
    else:
        select_check_out = ("SELECT id FROM check_in_out WHERE studentID='%s' "
                            "AND check_in_time LIKE '%s%%'"
                            "AND check_out_time IS NULL" % (Student_Id, System_Time[:10]))
        check_out_result = cur.execute(select_check_out)
        # 출퇴기록이 존재하는 경우
        if check_out_result == 0:
            print("퇴실기록이 이미 존재합니다.")
        # 출석기록 존재하나, 퇴실기록 없는 경우
        else:
            select_id = cur.fetchall()
            Check_Id = select_id[-1][0]
            Check_Out_Temp = 37.5
            update_check = ("UPDATE check_in_out "
                            "SET check_out_time = '%s',"
                            "check_out_temp = '%f' "
                            "WHERE id = '%d'" % (System_Time, Check_Out_Temp, Check_Id))
            cur.execute(update_check)
            conn.commit()
            print("퇴실기록 등록이 완료되었습니다.")
            cur.close
            conn.close

def lambda_handler(event, context):
    IMAGE_OUTPUT_FILENAME = event['Records'][0]['s3']['object']['key']
    if IMAGE_OUTPUT_FILENAME[:2] == INDEX:
        print(index(IMAGE_OUTPUT_FILENAME) + " 님의 등록이 완료되었습니다.")
    elif IMAGE_OUTPUT_FILENAME[:2] == CHECK_IN:
        print(check_in(IMAGE_OUTPUT_FILENAME) + " 님의 출석이 완료되었습니다.")
    elif IMAGE_OUTPUT_FILENAME[:2] == CHECK_OUT:
        print(check_out(IMAGE_OUTPUT_FILENAME) + " 님의 퇴실이 완료되었습니다.")