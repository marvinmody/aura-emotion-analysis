# File: ml/utils/audio_processor.py
import speech_recognition as sr
from textblob import TextBlob
import numpy as np

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def process_chunk(self, audio_bytes):
        try:
            # The audio data is received as a buffer of float32, convert it
            audio_data_np = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Assuming sample rate of 44100 (common for web audio) and 16-bit depth
            sample_rate = 44100
            sample_width = 2 

            audio = sr.AudioData(audio_data_np.tobytes(), sample_rate, sample_width)
            
            text = self.recognizer.recognize_google(audio, show_all=False)
            
            if text:
                analysis = TextBlob(text)
                sentiment = {
                    'polarity': analysis.sentiment.polarity,
                    'subjectivity': analysis.sentiment.subjectivity
                }
                return sentiment
            return None
        except sr.UnknownValueError:
            # Speech was unintelligible
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return None

# -----------------------------------------------------------------------------

# File: ml/app.py
from flask import Flask
from flask_socketio import SocketIO
import eventlet
from utils.video_processor import VideoProcessor
from utils.audio_processor import AudioProcessor

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# --- Initialize Processors ---
# IMPORTANT: Replace with the actual path to your trained model
emotion_model_path = './models/emotion_detection_model.h5' 
video_processor = VideoProcessor(emotion_model_path)
audio_processor = AudioProcessor()

# --- Socket.IO Event Handlers ---
@socketio.on('connect')
def handle_connect():
    print('ML Server connected to Backend')

@socketio.on('video_frame_to_ml')
def handle_video_frame(data):
    """Receives a video frame, processes it, and sends results back."""
    emotions = video_processor.process_frame(data)
    if emotions:
        socketio.emit('analysis_results', {'emotions': emotions})

@socketio.on('audio_chunk_to_ml')
def handle_audio_chunk(data):
    """Receives an audio chunk, processes it, and sends results back."""
    sentiment = audio_processor.process_chunk(data)
    if sentiment:
        socketio.emit('analysis_results', {'sentiment': sentiment})

@socketio.on('disconnect')
def handle_disconnect():
    print('ML Server disconnected from Backend')

if __name__ == '__main__':
    print("Starting ML Flask server...")
    socketio.run(app, host='0.0.0.0', port=5001)
