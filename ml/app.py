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
