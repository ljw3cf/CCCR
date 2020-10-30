import pymysql
import json
from random import *
from datetime import datetime, timedelta

ENDPOINT = "test.cumohhkhvfrn.ap-northeast-1.rds.amazonaws.com"
PORT = 3306
USR = "admin"
REGION = "ap-northeast-1"
DBNAME = "QuickSight"
DBPASS = "dkagh1.."

CONN = pymysql.connect(host = ENDPOINT, user=USR, passwd=DBPASS, port=PORT, database=DBNAME)
CUR = CONN.cursor()

DAY = 1

# StudentID 부분임! 원하는 StudentID로 넣을 것
SID = 5

while True:
    check_in_hour = randint(12, 13)
    if check_in_hour == 12:
        check_in_minute = randint(40, 59)
    elif check_in_hour == 13:
        check_in_minute = randint(00, 20)
    check_in_sec = randint(0, 59) 
    
    cit = "2020-10-%02d %d:%d:%d" % (DAY, check_in_hour, check_in_minute, check_in_sec)
    
    citm = uniform(36.2, 37.1)
    
    check_out_hour = randint(21, 22)
    if check_out_hour == 21:
        check_out_minute = randint(40, 59)
    elif check_out_hour == 22:
        check_out_minute = randint(00, 20)
    check_out_sec = randint(0, 59) 

    cot = "2020-10-%02d %d:%d:%d" % (DAY, check_out_hour, check_out_minute, check_out_sec)
    
    cotm = uniform(36.2, 37.1)
    
    add_ljw = ("INSERT INTO Check_in_out "
                "(check_in_time, check_in_temp, check_out_time, check_out_temp, studentID)"
                "VALUES('%s', %f, '%s', %f, %d)" % (cit, citm, cot, cotm, SID))

    CUR.execute(add_ljw)
    CONN.commit()
    DAY = DAY + 1
    if DAY == 32:
        break
CONN.close()