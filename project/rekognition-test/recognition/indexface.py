#Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

#import mysql.connector
import os
import sys
import boto3
#import insert_faceid

def add_faces_to_collection(bucket,photo,collection_id):    
    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])


    print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         print('  당신의 Face ID는?: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
         FaceID = faceRecord['Face']['FaceId']
    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
            
#    name = 'LeeJaewon'

#    insert_faceid.insert_id(faceRecord['Face']['FaceId'])    
    return len(response['FaceRecords'])

def main():
    bucket='function-text'
    collection_id='cccr_collection'
    photo='testimg.jpg'
    
    indexed_faces_count = add_faces_to_collection(bucket, photo, collection_id)
    print("Faces indexed count: " + str(indexed_faces_count))

if __name__ == "__main__":
    main()
