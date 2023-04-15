import cv2
import face_recognition
import os
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://automatedcheckinapp-default-rtdb.firebaseio.com/',
    'storageBucket':'automatedcheckinapp.appspot.com'
})

imageFolderPath = 'Images'
listOfImages = os.listdir(imageFolderPath)
# print(listOfImages)
imageArray=[]
imgIdArray=[]
for val in listOfImages:
    imageArray.append(cv2.imread(os.path.join(imageFolderPath,val)))
    imgIdArray.append(os.path.splitext(val)[0])

    filename = f'{imageFolderPath}/{val}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

# print(len(imageArray))
# print(imgIdArray)

def findEncodings(imageArray):
    encodingsArray=[]
    for img in imageArray:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingsArray.append(encode)

    return encodingsArray

print("Encoding started")
encodingsOfKnownImages = findEncodings(imageArray)
encodingsAndIds = [encodingsOfKnownImages,imgIdArray]
print("Encoding Complete")

file = open("EncodeFile.p",'wb')
pickle.dump(encodingsAndIds,file)
file.close()
print("File Saved")