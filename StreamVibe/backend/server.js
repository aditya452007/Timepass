// File: server.js | Purpose: Entry point for the backend API | Exports: None
require('dotenv').config({ path: '../.env' });
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const connectDB = require('./config/db');

connectDB();

const app = express();

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(express.json());
app.use(cookieParser());

app.use('/api/auth', require('./routes/auth'));
app.use('/api/upload', require('./routes/upload'));
app.use('/api/videos', require('./routes/videos'));
app.use('/api/users', require('./routes/users'));

app.get('/api/health', (req, res) => res.json({ ok: true, timestamp: new Date().toISOString() }));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
