// File: routes/upload.js | Purpose: ImageKit auth for client-side upload | Exports: router
const express = require('express');
const router = express.Router();
const imagekit = require('../utils/imagekit');
const authMiddleware = require('../middleware/auth');

/**
 * This endpoint provides auth params so the frontend can upload files
 * DIRECTLY to ImageKit without routing the video through this server.
 * Flow: 1) Frontend calls GET /api/upload/auth
 *       2) Frontend uploads file to ImageKit using returned params
 *       3) Frontend calls POST /api/videos with the resulting metadata
 */
router.get('/auth', authMiddleware, (req, res) => {
    try {
        const result = imagekit.getAuthenticationParameters();
        res.status(200).json({
            token: result.token,
            expire: result.expire,
            signature: result.signature,
            publicKey: process.env.IMAGEKIT_PUBLIC_KEY
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
