import cv2
import numpy as np
import os
import face_recognition
# import requests
from gpiozero import MotionSensor
p = MotionSensor(12)


def sand_request_enter(w):
    print(w)
    # res = requests.get('http://localhost:3000/accessToGym/' + str(w))
    # a = res.text
    # res = requests.get('http://localhost:3000/accessToGym/' + a)
    # aa = requests.get('http://localhost:3000/enterF/' + a)
    # ww = res.r
    # print(a)
    # if res.status_code == 200:
    print("you can enter to gym")
    # if a.r == "yes":
    #     print("Time enter registerd")
    # res2 = requests.get('http://localhost:3000/saveTimeEnter/' + a)
    # print(res2)
    # else:
    # print("you can't enter to gym")

    #    print(res)
    # print(aa.text)


def findEncodeing1(img):
    encodeList = []
    for i in img:
        i = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(i)[0]
        encodeList.append(encode)
    return encodeList


def toWork():
    # i get an inssue that this code work with only jpg picture probleme i cv2.cvtColor()
    path = "Images"
    imageList = os.listdir(path)
    image = []
    imageName = []

    for i in imageList:
        image.append(cv2.imread(f'{path}/{i}'))
        imageName.append(os.path.splitext(i)[0])
    # print(image)

    encodeListKnown = findEncodeing1(image)
    # print(encodeListKnown)
    # print('hello')

    cap = cv2.VideoCapture(0)
    yes = 0
    nn = 0
    # to count the number of trail and send request to the server
    while 1:
        ret, frame = cap.read()
        fr = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        faceCurentFrame = face_recognition.face_locations(fr)
        encodeCurentFrame = face_recognition.face_encodings(fr, faceCurentFrame)
        # print(len(encodeCurentFrame))
        # print(len(faceCurentFrame))
        matches = [0]
        matchesIndex = 0
        for encodeface, faceLoc in zip(encodeCurentFrame, faceCurentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeface)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeface)
            print(faceDis)
            # print('heloo')
            matchesIndex = np.argmin(faceDis)
            # test=True
        print(matches)
        # faceDis is a list of the percentage of faces to compare. the low value is the close person
        # matches is a list of booleans contains true in the column of the person closest to the frame
        if (matches[matchesIndex]):
            # face is allow to  the gym
            # name = imageName[matchesIndex].upper()
            name = imageName[matchesIndex]
            # print(name)
            # print(faceLoc)
            indexx = name[name.index('{') + 1: name.index('}')]
            y1 = faceLoc[0] * 4
            x2 = faceLoc[1] * 4
            y2 = faceLoc[2] * 4
            x1 = faceLoc[3] * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            name = name[0:name.index('(')]
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            yes = yes + 1
        nn = nn + 1
        print(nn)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if yes == 5:
            print('sand request')
            print(indexx)
            sand_request_enter(indexx)
            # and here we sand the request
            break
        elif nn - yes == 300:
            print('unknown face')
            break
        if key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows


while True:
    print("Movement scan!!")
    p.wait_for_motion()
    print("Movement detected!!")
    toWork()
    p.wait_for_no_motion()
    print('The area is clear')
