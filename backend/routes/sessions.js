// File: backend/routes/sessions.js
const express = require('express');
const router = express.Router();
const Session = require('../models/Session');

// @route   GET api/sessions
// @desc    Get all past sessions
// @access  Public
router.get('/', async (req, res) => {
    try {
        const sessions = await Session.find().sort({ createdAt: -1 });
        res.json(sessions);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});

module.exports = router;