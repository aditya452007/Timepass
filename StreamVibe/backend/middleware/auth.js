// File: middleware/auth.js | Purpose: Verifies JWT token and sets req.user | Exports: authMiddleware
const jwt = require('jsonwebtoken');

/**
 * Express middleware to authenticate a user via JWT.
 * It reads the token from 'req.cookies.token' or 'req.headers.authorization'.
 * Sets 'req.user = { id: decoded.id }' if valid, or returns 401.
 * 
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
const authMiddleware = (req, res, next) => {
    let token = req.cookies?.token;
    if (!token && req.headers.authorization?.startsWith('Bearer ')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = { id: decoded.id };
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
};

module.exports = authMiddleware;
