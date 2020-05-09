#!/usr/bin/env python
# coding: utf-8

# In[8]:


import boto3

def client_rekognition():
    client=boto3.client('rekognition',
                        region_name = 'us-east-1',
                        aws_access_key_id='AKIA4XEVBWGXROYDINWU',
                        aws_secret_access_key='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')
    return client
    

def create_collection(collection_id):

    client=client_rekognition()
    #Create a collection
    print('Creating collection:' + collection_id)
    response=client.create_collection(CollectionId=collection_id)
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done...')
    
    
def add_faces_to_collection(bucket,photo,collection_id):
    
    client=client_rekognition()

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo)
    print('Faces indexed:')
    
    for faceRecord in response['FaceRecords']:
         print('  Face ID: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])

def compare_faces(sourceFile, targetFile,bucket):

    client=client_rekognition()
    s3client = boto3.client('s3',
                            region_name='us-east-1',
                            aws_access_key_id='AKIA4XEVBWGXROYDINWU',
                            aws_secret_access_key='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')
    
    imageSource=s3client.get_object(Bucket=bucket,Key=sourceFile)['Body']
    #imageSource=open(sourceFile,'rb')
    #imageTarget=open(targetFile,'rb')
    imageTarget=s3client.get_object(Bucket=bucket,Key=targetFile)['Body']

    response=client.compare_faces(SimilarityThreshold=98, # security perpose 98%
                                  SourceImage={'Bytes': imageSource.read()},
                                  TargetImage={'Bytes': imageTarget.read()})
    
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at ' +
               str(position['Left']) + ' ' +
               str(position['Top']) +
               ' matches with ' + similarity + '% confidence')

    imageSource.close()
    imageTarget.close()     
    return len(response['FaceMatches'])          



    
def main():
    collection_id='PersonofInterest'
    create_collection(collection_id)
    bucket='parthcloudneu'
    photos=['Parthasarathi_Samantaray.jpg','Xinpeng_Ma.JPG','Sanket_Kandelwal.jpg']
    #photo_path=['https://parthcloudneu.s3.us-east-2.amazonaws.com/Parthasarathi_Samantaray.jpg',
    #'s3://parthcloudneu/Xinpeng_Ma.JPG',
    #            's3://parthcloudneu/Sanket_Kandelwal.jpg']
    
    for i in range(len(photos)):
        indexed_faces_count=add_faces_to_collection(bucket,photo=photos[i],collection_id=collection_id)
        print("Faces indexed count: " + str(indexed_faces_count))
    
    print("Face Match starting ......")
    for i in range(len(photos)):
        source_file = photos[i]
        target_file='PersonofInterest.JPG'
        face_matches=compare_faces(source_file, target_file,bucket)
        if(face_matches >0):
            print("Face matches: " + photos[i])
            print("Person of Interest")
        elif (i==len(photos)):
            print(" Not a Person of Interest")
    
    

if __name__ == "__main__":
    main()    


# In[7]:


client=client_rekognition()
client.delete_collection(CollectionId='PersonofInterest')


# In[ ]:




