// File: backend/models/Session.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const sessionSchema = new Schema({
    emotionData: {
        type: Map,
        of: Number,
        required: true
    },
    sentimentData: {
        polarity: { type: Number, required: true },
        subjectivity: { type: Number, required: true }
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Session', sessionSchema);