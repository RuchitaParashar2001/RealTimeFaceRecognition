
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://automatedcheckinapp-default-rtdb.firebaseio.com/'
})

#this will create a directory 'students' in our real time db
ref = db.reference('students')

data = {
    '205':
        {
            "name":"Bill gates",
            "course":"B-Tech",
            "branch":"CSE",
            "enrollment no":2052018,
            "total_attendance":6,
            "overall_percentage":'95%',
            "last_attendance_time":"2022-12-11 00:54:34",
            "starting_year":2018
        },
    '206':
        {
            "name":"Jimmy Fallon",
            "course":"BCom",
            "branch":"Eco honors",
            "enrollment no":2062018,
            "total_attendance":8,
            "overall_percentage":'85%',
            "last_attendance_time":"2022-12-11 00:54:34",
            "starting_year":2019
        },
    '207':
        {
            "name":"Ruchita Parashar",
            "course":"B-Tech",
            "branch":"IT",
            "enrollment no":2072018,
            "total_attendance":10,
            "overall_percentage":'90%',
            "last_attendance_time":"2022-12-11 00:54:34",
            "starting_year":2019
        },
    '208':
        {
            "name": "Tulsi Thakur",
            "course": "B-Tech",
            "branch": "IT",
            "enrollment no": 2082018,
            "total_attendance": 10,
            "overall_percentage": '90%',
            "last_attendance_time": "2022-12-11 00:54:34",
            "starting_year": 2019
        },
    '210':
        {
            "name": "Priyanshu Kumar",
            "course": "B-Tech",
            "branch": "IT",
            "enrollment no": 2102018,
            "total_attendance": 0,
            "overall_percentage": '90%',
            "last_attendance_time": "2022-12-11 00:54:34",
            "starting_year": 2019
        }
}
for key,val in data.items():
    ref.child(key).set(val)
