// File: routes/auth.js | Purpose: Auth endpoints | Exports: router
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const authMiddleware = require('../middleware/auth');

router.post('/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;
        if (!username || !email || !password) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        const existingEmail = await User.findOne({ email });
        if (existingEmail) return res.status(409).json({ error: 'Email already in use' });

        const existingUser = await User.findOne({ username });
        if (existingUser) return res.status(409).json({ error: 'Username already taken' });

        const passwordHash = await bcrypt.hash(password, 10);
        const user = await User.create({ username, email, passwordHash });

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '7d' });
        res.cookie('token', token, { httpOnly: true, maxAge: 7 * 24 * 60 * 60 * 1000 });

        const userObj = user.toObject();
        delete userObj.passwordHash;

        res.status(201).json({ message: 'Registered', user: userObj });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        const user = await User.findOne({ email });
        if (!user) return res.status(401).json({ error: 'Invalid credentials' });

        const isMatch = await bcrypt.compare(password, user.passwordHash);
        if (!isMatch) return res.status(401).json({ error: 'Invalid credentials' });

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '7d' });
        res.cookie('token', token, { httpOnly: true, maxAge: 7 * 24 * 60 * 60 * 1000 });

        const userObj = user.toObject();
        delete userObj.passwordHash;

        res.status(200).json({ message: 'Logged in', user: userObj });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.post('/logout', (req, res) => {
    res.clearCookie('token');
    res.status(200).json({ message: 'Logged out' });
});

router.get('/me', authMiddleware, async (req, res) => {
    try {
        const user = await User.findById(req.user.id).select('-passwordHash');
        if (!user) return res.status(404).json({ error: 'User not found' });
        res.status(200).json(user);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
