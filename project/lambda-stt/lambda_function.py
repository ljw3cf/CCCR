import json
import boto3

def transcribe(voice_object):
    transcribe = boto3.client('transcribe')
    job_uri = "https://transcriberecord.s3-ap-northeast-1.amazonaws.com/"+ voice_object
    job_name = "Transcript for" + voice_object
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='ko-KR'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
    data = json.loads(response.read())
    text = data['results']['transcripts'][0]['transcript']
    print(text)
    
def lambda_handler(event, context):
    response = transcribe(event["Records"][0]["s3"]["object"]["key"])
    print(response)