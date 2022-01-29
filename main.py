import numpy as np
import cv2 as cv
from keras.models import load_model
from keras.preprocessing.image import img_to_array

aweight = 0.5
num_frames = 0
bg = None

label = ['c_shape','crossing','fist','fist_thumb_out','fist_thumb_up','five','four','hook','l_shape','little_finger',
         'one','three_little_missing','three_middle_missing','three_pointer_missing','three_ring_missing','three_thumb',
         'thumb_little','thumb_up','two','one']

model = load_model('trained_model.h5')

def run_avg(img, aweight):
    global bg
    if bg is None:
        bg = img.copy().astype('float')
        return
    cv.accumulateWeighted(img, bg, aweight)


def segment(img, thres=25):
    global bg
    diff = cv.absdiff(bg.astype('uint8'), img)
    _, thresholded = cv.threshold(diff, thres, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(thresholded.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return
    else:
        segmented = max(contours, key=cv.contourArea)
    return thresholded, segmented

def get_prediction(img):
    for_pred = cv.resize(img,(64,64))
    x = img_to_array(for_pred)
    x = x/255.0
    x = x.reshape((1,) + x.shape)
    pred = str(label[np.argmax(x)])
    return pred

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()

    if ret == True:
        pred = None
        frame = cv.flip(frame, 1)
        clone = frame.copy()
        (height, width) = frame.shape[:2]
        roi = frame[100:300, 300:500]
        gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (7, 7), 0)

        if num_frames < 30:
            run_avg(gray, aweight)
        else:
            hand = segment(gray)

            if hand is not None:
                (thresholded, segmented) = hand
                pred = get_prediction(thresholded)
                cv.drawContours(clone, [segmented + (300, 100)], -1, (0, 0, 255))
                cv.imshow("Thesholded", thresholded)
                contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        cv.rectangle(frame, (300, 100), (500, 300), (0, 255, 0), 2)
        cv.rectangle(clone, (300, 100), (500, 300), (0, 255, 0), 2)
        cv.putText(clone, "Gesture Recognition", (50, 50), cv.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 3)
        if pred is not None:
            cv.putText(clone, pred, (50, 100), cv.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 3)
        num_frames += 1

        cv.imshow('frame', clone)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()