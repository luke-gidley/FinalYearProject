import numpy as np
import cv2 as cv
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import serial
import serial.tools.list_ports
import PySimpleGUI as sg
import time

aweight = 0.5
num_frames = 0
background = None
detect = None
password = None

# labels for classification
labels = ['c_shape', 'crossing', 'fist', 'fist_thumb_out', 'fist_thumb_up', 'five', 'four', 'hook', 'l_shape',
          'little_finger',
          'one', 'three_little_missing', 'three_middle_missing', 'three_pointer_missing', 'three_ring_missing',
          'three_thumb',
          'thumb_little', 'thumb_up', 'two', 'zero']

#loads in the trained model.
model = load_model('trained_model.h5')

#function that finds the USB port the arudino is connected to.
def findArduino():
    ports = serial.tools.list_ports.comports()
    commPort = 'None'
    numConnection = len(ports)

    for i in range(0, numConnection):
        port = ports[i]
        strPort = str(port)

        if 'Arduino' in strPort:
            splitPort = strPort.split(' ')
            commPort = (splitPort[0])

    return commPort

#function that cuts the hand out of the image.
def segment(img, thres=25):
    global background
    diff = cv.absdiff(background.astype('uint8'), img)
    _, thresholded = cv.threshold(diff, thres, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    contours, _ = cv.findContours(thresholded.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return
    else:
        segmented = max(contours, key=cv.contourArea)
    return thresholded, segmented

#function that uses the trained model on an image
def get_prediction(img):
    for_pred = cv.resize(img, (64, 64))
    x = img_to_array(for_pred)
    x = x / 255.0
    x = x.reshape((1,) + x.shape)
    confidence = model.predict(x)
    confidence = np.round(confidence, 3) * 100
    prediction = np.argmax(confidence)
    label = str(labels[prediction])
    return label, confidence, prediction


#this is the main loop, it draws everything seen on the screen.
def handRecognition():
    global num_frames
    global background

    arduino.flush()
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()


    firstLoopComplete = False
    label = None
    confidence = None
    while True:
        ret, frame = cap.read()

        if ret:

            frame = cv.flip(frame, 1)
            clone = frame.copy()
            (height, width) = frame.shape[:2]
            roi = frame[100:300, 300:500]
            gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
            gray = cv.GaussianBlur(gray, (7, 7), 0)

            #this gets the background from the first frame once the camera opens. After it has the background
            #it starts to look for the hand to cut out.
            if not firstLoopComplete:
                background = gray.copy().astype('float')
                firstLoopComplete = True
            else:
                hand = segment(gray)

                #if a hand is found, this part listens for a signal from the arduino.
                if hand is not None:
                    (thresholded, segmented) = hand
                    detect = arduino.read()
                    if detect == b'':
                        detect = None
                    label, confidence, prediction = get_prediction(thresholded)
                    #if the arduino sends the detect signal, this section will send the currently shown gesture to it.
                    if detect is not None:
                        prediction = str(prediction) + '\n'
                        arduino.write(prediction.encode('utf-8'))
                        detect = None
                        #print(prediction) testing purposes
                    #drawing of boxes and the screen.
                    cv.drawContours(clone, [segmented + (300, 100)], -1, (0, 0, 255))
                    cv.imshow("Thesholded", thresholded)
                    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            cv.rectangle(frame, (300, 100), (500, 300), (0, 255, 0), 2)
            cv.rectangle(clone, (300, 100), (500, 300), (0, 255, 0), 2)
            cv.putText(clone, "Gesture Recognition", (50, 50), cv.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)
            if label is not None:
                cv.putText(clone, label + " " + str(np.max(confidence)) + "%", (50, 100), cv.FONT_HERSHEY_DUPLEX, 1,
                           (0, 255, 0),
                           3)
            num_frames += 1

            cv.imshow('frame', clone)
        if cv.waitKey(1) == ord('q'):
            arduino.flush()
            break
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()


def changePassword(newPassword):
    # cleaning and splitting data
    newPassword = newPassword.strip()
    newPassword = newPassword.split(" ")

    # checks password is the correct length
    if len(newPassword) != 4:
        return False
    # checks that data is in correct format
    for i in newPassword:
        try:
            if int(i) <= 0 or int(i) >= 19:
                return False
        except:
            return False
    # puts the password into the .txt file
    file = open("password.txt", "w")
    file.truncate(0)
    for i in newPassword:
        file.write(i + "\n")
    return True


def uploadPassword():
    ps = 'password\n'
    arduino.write(ps.encode('utf-8'))
    with open('password.txt', 'r') as file:
        for i in file:
            arduino.write((i + '\n').encode('utf-8'))
            #time.sleep(0.5)


connectPort = findArduino()
arduino = serial.Serial(connectPort, 9600, timeout=0.1)
arduino.flush()

image_col = []
image_col_desc = []
image_col_2 = []
image_col_desc_2 = []
index = 0
# reads in images to be displayed in ui
for i in labels:
    # reads in first 10 images, then the next 10 into a new column for better formatting
    if len(image_col) < 10:
        image_col.append([sg.Image(filename='Images/' + i + '.png')])
        image_col_desc.append([sg.Text(i + " - " + str(index), pad=((0, 0), (18, 18)))])
    else:
        image_col_2.append([sg.Image(filename='Images/' + i + '.png')])
        image_col_desc_2.append([sg.Text(i + " - " + str(index), pad=((0, 0), (18, 18)))])
    index += 1

# layout list to create the ui
layout = [[sg.Text("SmartLock Application\nPlease format password like so: 1 2 3 4")], [sg.Text(key='PASSWORD')],
          [sg.Button("Start")], [sg.Button("Change Password")],
          [sg.InputText(key='password', size=(50, 50))],
          [sg.Column(image_col), sg.Column(image_col_desc), sg.Column(image_col_2), sg.Column(image_col_desc_2)]]

window = sg.Window("SmartLock settings", layout)

# loop to run the application.
while True:
    event, values = window.read()

    # start button event
    if event == "Start":
        uploadPassword()
        start = 'start\n'
        time.sleep(2.5)
        arduino.write(start.encode('utf-8'))
        handRecognition()
    # change password button event
    elif event == "Change Password":
        accepted = changePassword(values['password'])
        if accepted:
            window['PASSWORD'].update("Password Accepted")
        elif not accepted:
            window['PASSWORD'].update("Password is in the wrong format, Please try again")

    elif event == sg.WIN_CLOSED:
        break
