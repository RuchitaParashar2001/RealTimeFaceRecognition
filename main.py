import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://automatedcheckinapp-default-rtdb.firebaseio.com/',
    'storageBucket':'automatedcheckinapp.appspot.com'
})
bucket = storage.bucket()


cap = cv2.VideoCapture(0)
# this is for setting the width and height of the graphics respectively
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#importing mode Images into A list
modeFolderKaPath = 'Resources/Modes'
namesOfImagesInModeFolder = os.listdir(modeFolderKaPath)
ImagesModeFolderArray = []
for val in namesOfImagesInModeFolder:
    ImagesModeFolderArray.append(cv2.imread(os.path.join(modeFolderKaPath,val)))

# print(len(ImagesModeFolderArray))

file = open('EncodeFile.p','rb')
encodingsAndIds = pickle.load(file)
file.close()
encodingsOfKnownImages,imgIdArray = encodingsAndIds
# print(imgIdArray)
print("Encoded file loaded")

mode = 0
counter = 0
id = -1
imgStudent=[]

while True:
    success, img = cap.read()
    imgSmall = cv2.resize(img,(0,0), None, 0.25, 0.25)
    # imp step color cvt
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    facesCurrFrame = face_recognition.face_locations(imgSmall)
    encodeCurrFrame = face_recognition.face_encodings(imgSmall,facesCurrFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = ImagesModeFolderArray[mode]

    if facesCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame,facesCurrFrame):
            matches = face_recognition.compare_faces(encodingsOfKnownImages,encodeFace)
            faceDist = face_recognition.face_distance(encodingsOfKnownImages,encodeFace)
            # print("matches",matches)
            # print("faceDist",faceDist)
            matchIndex = np.argmin(faceDist)
            # print(imgIdArray[matchIndex])

            if matches[matchIndex]:
                # print("Known face detected")
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                imgBackground= cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = imgIdArray[matchIndex]
    # fetching the data of the matched student from db
                if counter==0:
                    counter=1
                    mode =1

        if counter!=0:

            #first frame
            if counter == 1:
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)
                #get image from storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                #converting to an array
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #update the data
                datetimeobject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  '%Y-%m-%d %H:%M:%S')
                secondsElapsed = (datetime.now()-datetimeobject).total_seconds()
                print(secondsElapsed)
                if(secondsElapsed>30):
                    ref = db.reference(f'students/{id}')
                    studentInfo['total_attendance']+=1
                    # this is used to send the data to db
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    mode=3
                    counter=0
                    imgBackground[44:44 + 633, 808:808 + 414] = ImagesModeFolderArray[mode]

            if mode!=3:
                if 10<counter<20:
                    mode=2
                imgBackground[44:44 + 633, 808:808 + 414] = ImagesModeFolderArray[mode]

                if counter<=10:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)

                    cv2.putText(imgBackground, str(studentInfo['course']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['enrollment no']), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['overall_percentage']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['branch']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)

                    # to align the name field to the centre
                    (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 1)

                    imgBackground[175:175+216,909:909+216]=imgStudent


                counter+=1

                if counter>=20:
                    counter = 0
                    mode=0
                    studentInfo=[]
                    imgStudent=[]
                    imgBackground[44:44 + 633, 808:808 + 414] = ImagesModeFolderArray[mode]
    else:
        mode=0
        counter=0



    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)

# the above code is the basic code to show an image on the screen using webcam
