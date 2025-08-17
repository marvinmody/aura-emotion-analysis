// File: backend/server.js
const express = require('express');
const http = require('http');
const mongoose = require('mongoose');
const { Server } = require("socket.io");
const cors = require('cors');
const { instrument } = require('@socket.io/admin-ui');
require('dotenv').config();

const Session = require('./models/Session');
const sessionRoutes = require('./routes/sessions');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);

const io = new Server(server, {
    cors: {
        origin: ["http://localhost:3000", "https://admin.socket.io"],
        credentials: true
    }
});

// --- MongoDB Connection ---
mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
}).then(() => console.log('MongoDB Connected...'))
  .catch(err => console.error(err));

// --- API Routes ---
app.use('/api/sessions', sessionRoutes);

// --- Socket.IO Connection Handling ---
io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);

    // Forward video frames to ML server
    socket.on('video_frame', (data) => {
        socket.broadcast.emit('video_frame_to_ml', data);
    });

    // Forward audio chunks to ML server
    socket.on('audio_chunk', (data) => {
        socket.broadcast.emit('audio_chunk_to_ml', data);
    });

    // Receive analysis results from ML server and forward to frontend
    socket.on('analysis_results', (data) => {
        io.emit('results_for_frontend', data);
    });
    
    // Handle saving session data
    socket.on('save_session', async (data) => {
        try {
            const newSession = new Session({
                emotionData: data.emotionData,
                sentimentData: data.sentimentData
            });
            await newSession.save();
            socket.emit('session_saved', { message: 'Session saved successfully!' });
        } catch (err) {
            console.error('Error saving session:', err);
            socket.emit('save_error', { message: 'Failed to save session.' });
        }
    });

    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
    });
});

// For the Socket.IO Admin UI
instrument(io, { auth: false });

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Backend server running on port ${PORT}`));
