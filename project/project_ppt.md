1. Thing 단의 카메라에서 얼굴이 인식되면 음성 녹음이 시작됩니다. 마이크에 원하는 기능을 말하면 wav형태로 녹음됩니다.
   녹음된 음성파일은 S3 voice bucket으로 업로드 됩니다.

2. S3 voice bucket에 파일이 업로드 되는 이벤트가 트리거가 되어, Lambda STT function을 활성화 합니다. 
여기서 Lambda는 AWS의 서버리스 컴퓨팅 서비스이며, 서버를 프로비저닝하거나 관리할 필요 없이 코드를 실행시켜주는 서비스입니다.
Lambda는 크게 트리거와 코드로 구성되어 있습니다. 트리거는 코드를 실행시키는 firestarter이며, DynamoDB, SNS, S3 등
다른 AWS 서비스와 연동시킬 수 있습니다. 트리거로 설정된 AWS 서비스에서 이벤트가 발생하면, 관련 정보는 코드에 event와 context라는 변수에 json 형태로 선언됩니다.

3. Lambda STT function에서 AWS api를 통해 STT를 요청하는 코드가 실행됩니다. 
STT를 위해 사용한 서비스는 AWS Transcribe 입니다. Transcribejob의 강점은 API를 통해 다른 AWS 서비스와 연동이 쉽고, 사용자 지정 어휘를 생성하여 인식이 잘 되지 않은 어휘를 수정할 수 있다는 점 입니다.
STT 요청 시 Transcribe는 TranscribeJob이라는 작업 목록을 생성합니다. 처음 요청시 Status는 In process로 표기되고,STT가 완료되면 Complete로 변경됩니다. STT 완료 시 json파일 url이 생성되며, 해당 파일에서 음성내용을 문자열로 확인할 수 있습니다.

4. Lambda 코드실행이 완료되면, 해당 로그를 CloudWatch에 전송합니다. 
CloudWatch는 AWS 서비스에 대한 알람 및 로그관리 서비스 입니다. Lambda 코드를 처음 생성하면, CloudWatch에 Lambda 코드명에 해당하는 로그 그룹이 생성됩니다. Lambda 코드에 대한 로그는 해당 로그 그룹에서 관리할 수 있습니다.

5. 한편 Thing 단에선 음성파일을 업로드 후 TranscribeJob의 Status 상태를 지속적으로 확인하고 있습니다. 
Status가 Complete로 변경되면 온도센서가 수강생 체온을 측정하고, 체온정보를 json형태로 저장합니다. 그리고 S3 textbucket에 해당 파일을 업로드합니다.

6. 다음엔 수강생의 얼굴을 스트리밍하고 있는 frame을 추출하고 jpg형태로 저장합니다. 
출결관리 담당 Lambda 출결관리 fuctnion에서 등록/출석/퇴실에 따라 다른 절차를 진행하기 위해 jpg파일명의 접두사에 기능에 대한 식별자를 부여합니다. 생성된 jpg파일은 S3 image bucket에 업로드합니다.

7. S3 image bucket은 Lambda 출결관리 function에 트리거로 설정되어 있습니다. 해당 bucket에 이미지가 업로드되는 이벤트가 트리거가 되어 Lambda 출결관리 function을 활성화 합니다. 

8. Lambda 출결관리 function은 S3 image bucket에 업로드된 오브젝트 파일명의 접두사를 식별합니다. 그리고 AWS api를 이용하여 얼굴인식에 필요한 코드를 실행시킵니다. 얼굴인식을 위해 사용한 서비스는 AWS Rekognition 입니다. 
Rekogntion은 학습모델을 이용하여 이미지 혹은 영상에서 인물의 특징을 식별할 수 있는 서비스 입니다. 수강생 등록시에는 Rekognition의 IndexFaces 기능을 사용합니다. IndexFaces는 이미지에서 인물의 특징을 확인하고 고유한 FaceID를 발급해주는 기능입니다. 발급된 FaceID는 Rekognition Collection이라 불리우는 저장공간에 등록됩니다.
출석 / 퇴실 시에는 DetectFacesbyImages 기능을 사용합니다. DetectFacesbyImages는 이미지에서 인물의 특징을 확인하고, Collection에서 해당 인물의 FaceID를 검색 후 출력합니다.

9. Lambda 출결관리 function은 Rekognition으로 얼굴인식 후 수강생 및 출결정보를 MariaDB에 저장합니다. 
MariaDB는 AWS RDS서비스를 사용하여 구축하였습니다. 이 Database는 수강생 정보를 관리하는 Student 테이블과 출결 정보를 관리하는 Check_in_out 테이블로 구성되어 있습니다. 
수강생 등록 시 Transcribe에서 학생 이름과 분반을 호출하고 Rekognition에서 FaceID를 호출한 뒤 Student 테이블에 해당 정보들을 Insert합니다. 출결 시 Rekognition에서 FaceID를 호출한 뒤 Student table에 쿼리를 날려 해당 FaceID의 학생이 누구인지 확인합니다. 이후 S3 message bucket에서 온도정보를 호출하고 time 라이브러리에서 시스템 시간을 호출합니다. 이렇게 호출된 정보들을 Check_in_out 테이블에 Insert 합니다.

10. 데이터베이스의 변경사항은 AWS QuickSight에 반영됩니다. AWS QuickSight는 AWS에서 제공하는 BI(Business Intelligence) 도구입니다. QuickSight의 강점은 온 프레미즈 환경에서 별도의 ELK 스택을 구성할 필요 없으며, 콘솔에서 클릭 몇 번 만으로 BI를 구축할 수 있다는 점 입니다. [QuickSight에서 우리가 설정한 대시보드에 대한 설명]

11. 마지막으로 Lambda는 TTS하기 위해 학생정보와 온도정보를 텍스트로 변환하고 S3 message bucket으로 업로드 합니다.

12. Lambda 출결관리 function의 모든 로그는 CloudWatch로 전달됩니다.

13. S3 message bucket에 업로드된 텍스트를 음성파일로 TTS 합니다. 저희가 TTS를 위해 사용한 도구는 AWS Polly입니다. Polly는 텍스트 혹은 문서파일을 음성으로 변경해주는 TTS 도구입니다. 음성은 음성파일로 저장하거나 스트리밍할 수 있습니다. 스트리밍의 경우 한글을 지원하지 않기 떄문에 저희는 음성파일을 저장하여 RaspberryPi에서 재생하는 방법을 채택하였습니다. Polly의 강점은 API를 통해 S3와 연동이 쉽고, 빠르게 TTS를 수행할 수 있다는 점 입니다. 또한 음성을 effect 조건을 통해 속삭임, 빠르게 말하기, 크게 말하기 등으로 변조할 수 있습니다. 

14. 마지막으로 RaspberryPi에서 음성파일을 재생하여 수강생 이름과 분반 그리고 온도를 알려줍니다.