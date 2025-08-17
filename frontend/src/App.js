// frontend/src/App.js

import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';
import D3Chart from './D3Chart';

const socket = io('http://localhost:5000');

const App = () => {
    const videoRef = useRef(null);
    const [emotions, setEmotions] = useState([]);
    const [sentiments, setSentiments] = useState([]);

    useEffect(() => {
        // Get user media
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(stream => {
                videoRef.current.srcObject = stream;

                // Send video stream to the server
                const mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (event) => {
                    socket.emit('stream', event.data);
                };
                mediaRecorder.start(1000);

                // Send audio stream to the server
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);
                const processor = audioContext.createScriptProcessor(1024, 1, 1);
                source.connect(processor);
                processor.connect(audioContext.destination);
                processor.onaudioprocess = (event) => {
                    socket.emit('audio', event.inputBuffer.getChannelData(0));
                };
            });

        // Receive analysis results from the server
        socket.on('analysis_result', (data) => {
            setEmotions(data.emotions);
            setSentiments(data.sentiments);
        });
    }, []);

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-4xl font-bold text-center mb-4">Aura - Real-time Emotion and Sentiment Analysis</h1>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <video ref={videoRef} autoPlay muted className="w-full h-auto" />
                </div>
                <div>
                    <D3Chart emotions={emotions} sentiments={sentiments} />
                </div>
            </div>
        </div>
    );
};

export default App;
