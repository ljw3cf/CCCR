import mysql.connector
import os
import sys
import boto3

def insert_id(FaceID):
    ENDPOINT = "cccr-test.ch2yozg5afqo.ap-southeast-2.rds.amazonaws.com"
    PORT = "3306"
    USR = "admin"
    REGION = "ap-southeast-2"
    DBNAME = "cccr_test"
    DBPASS = "dkaghdkagh1."
    os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN:'] = '1'
    
    client = boto3.client('rds')
    
    conn = mysql.connector.connect(host = ENDPOINT, user=USR, passwd=DBPASS, port=PORT, database=DBNAME)
    cur = conn.cursor()
    emp_id = cur.lastrowid
    add_student = ("INSERT INTO student "
                   "(id, FaceID, Name) "
                   "VALUES (%(id)s,%(FaceID)s, %(Name)s)")
    
    data_student = {
        "id": emp_id,
        "FaceID": FaceID,
        "Name": "Leejaewon",
    }
    cur.execute(add_student, data_student)
    
    conn.commit()
    print ("FaceID와 Name이 RDS로 전송되었습니다!")
    cur.close()
    conn.close()