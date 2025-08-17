# File: ml/utils/video_processor.py
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

class VideoProcessor:
    def __init__(self, model_path):
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Load the emotion detection model
        self.emotion_model = load_model(model_path)
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

    def process_frame(self, frame_bytes):
        try:
            # Decode the frame
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return []

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            emotions_detected = []
            for (x, y, w, h) in faces:
                # Extract the face ROI
                roi_gray = gray[y:y + h, x:x + w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

                if np.sum([roi_gray]) != 0:
                    # Prepare ROI for classification
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    # Predict the emotion
                    preds = self.emotion_model.predict(roi)[0]
                    label = self.emotion_labels[preds.argmax()]
                    emotions_detected.append(label)
            
            return emotions_detected
        except Exception as e:
            print(f"Error processing video frame: {e}")
            return []