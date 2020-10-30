import boto3
import json
S3 = boto3.client("s3")
BUCKET_NAME = "cccr-message"
IMAGE_OBJECT_KEY = "CI-2020-10-21-18-01-38.wav.jpg"
json_data = S3.get_object(Bucket=BUCKET_NAME, Key="TEMP-CI-2020-10-21-18-01-38.wav.jpg.json") 
json_text = json.loads(json_data['Body'].read()) 
Check_In_Temp = json_text["Temp"]
print(Check_In_Temp)