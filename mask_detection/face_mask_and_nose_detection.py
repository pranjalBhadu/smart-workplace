import keras
import tensorflow
# from imutils.video import VideoStream
from tensorflow.keras.models import load_model
import os
dirname = os.path.dirname(__file__)
model = load_model(os.path.join(dirname, 'mask_detector.model'))


import cv2
import os
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

def mask_detect_func():

    faceCascade = cv2.CascadeClassifier('/Users/pranjalbhadu/Documents/smart-workplace/mask_detection/haarcascade_frontalface_alt2.xml')
    nose_cascade = cv2.CascadeClassifier('/Users/pranjalbhadu/Documents/smart-workplace/mask_detection/haarcascade_mcs_nose.xml')

    if nose_cascade.empty():
        raise IOError('Unable to open nose cascade')
    # filename="./mask_v1.mp4"
    video_capture = cv2.VideoCapture(0)
    # vs = VideoStream(src = 0).start()
    ds_factor = 0.5

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        # frame = vs.read()
        # frame = imutils.resize(frame,width=400)
        frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(60, 60),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
        nose_rects = nose_cascade.detectMultiScale(gray, 1.3, 5)
        faces_list=[]
        preds=[]
        for (x, y, w, h) in faces:
            face_frame = frame[y:y+h,x:x+w]
            face_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
            face_frame = cv2.resize(face_frame, (224, 224))
            face_frame = img_to_array(face_frame)
            face_frame = np.expand_dims(face_frame, axis=0)
            face_frame =  preprocess_input(face_frame)
            faces_list.append(face_frame)
            if len(faces_list)>0:
                preds = model.predict(faces_list)
            for pred in preds:
                (mask, withoutMask) = pred
            label = "Mask" if mask > withoutMask else "No Mask"
            print(len(nose_rects))
            if len(nose_rects)>0 :
                color = (0, 255, 255) if label == "Mask" else (0, 0, 255)      
                if label=="Mask":
                    label="WEAR MASK PROPERLY"
                else:
                    label="NOT MASKED"
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
                cv2.putText(frame, label, (x, y- 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                for (x,y,w,h) in nose_rects:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)
                    break
                cv2.rectangle(frame, (x, y), (x + w, y + h),color, 2)
                
                
            else:
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
                cv2.putText(frame, label, (x, y- 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            
                cv2.rectangle(frame, (x, y), (x + w, y + h),color, 2)
                
                
            # Display the resulting frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')