import boto3
import pyaudio
import subprocess
from botocore.exceptions import BotoCoreError, ClientError
from tempfile import gettempdir

def speech(pollytext):
    polly = boto3.client("polly")
    try:
        response = polly.synthesize_speech(Text=pollytext, OutputFormat="mp3", VoiceId="Seoyeon")
    except (BotoCoreError, ClientError) as error:
       print(error)
       sys.exit(-1)
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            #mp3 파일 저장위치 지정
            output = os.path.join(gettempdir(), "speech.mp3")
            try:
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)
                sys.exit(-1)
    else:
        print("응답에 오디오 데이터가 포함되지않아 오디오를 스트리밍 할 수 없습니다.")
        sys.exit(-1)
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, output])

def recording(wave_output_filename):
    #녹음에 필요한 변수들
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5

    #pyaudio 라이브러리로 녹음데이터를 frames에 떄려박는 함수들
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
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

def S3(file_direction, bucket_name, file_name):
    S3 = boto3.client("s3")
    S3.upload_file(file_direction, bucket_name, file_name)
    return print("S3 업로드 완료")    