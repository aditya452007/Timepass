// File: routes/videos.js | Purpose: Video endpoints | Exports: router
const express = require('express');
const router = express.Router();
const Video = require('../models/Video');
const authMiddleware = require('../middleware/auth');

router.get('/', async (req, res) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 12;

        const videos = await Video.find()
            .sort({ createdAt: -1 })
            .skip((page - 1) * limit)
            .limit(limit)
            .populate('uploader', 'username');

        const total = await Video.countDocuments();

        res.status(200).json({
            videos,
            totalPages: Math.ceil(total / limit),
            currentPage: page
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.get('/search', async (req, res) => {
    try {
        const q = req.query.q || '';
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 12;

        const query = { title: { $regex: q, $options: 'i' } };
        const videos = await Video.find(query)
            .sort({ createdAt: -1 })
            .skip((page - 1) * limit)
            .limit(limit)
            .populate('uploader', 'username');

        const total = await Video.countDocuments(query);

        res.status(200).json({
            videos,
            totalPages: Math.ceil(total / limit),
            currentPage: page
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.get('/:id', async (req, res) => {
    try {
        const video = await Video.findById(req.params.id)
            .populate('uploader', 'username avatar');
        if (!video) return res.status(404).json({ error: 'Video not found' });

        res.status(200).json(video);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.post('/', authMiddleware, async (req, res) => {
    try {
        const { title, description, tags, imagekitFileId, imagekitUrl, thumbnailUrl } = req.body;

        if (!title) {
            return res.status(400).json({ error: 'Title is required' });
        }

        const video = await Video.create({
            title,
            description,
            tags,
            imagekitFileId,
            imagekitUrl,
            thumbnailUrl,
            uploader: req.user.id
        });

        res.status(201).json(video);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.patch('/:id/view', async (req, res) => {
    try {
        const video = await Video.findByIdAndUpdate(
            req.params.id,
            { $inc: { viewCount: 1 } },
            { new: true }
        );

        if (!video) return res.status(404).json({ error: 'Video not found' });
        res.status(200).json({ viewCount: video.viewCount });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.patch('/:id/like', authMiddleware, async (req, res) => {
    try {
        const video = await Video.findById(req.params.id);
        if (!video) return res.status(404).json({ error: 'Video not found' });

        const userId = req.user.id;
        const hasLiked = video.likes.includes(userId);

        if (hasLiked) {
            video.likes.pull(userId);
        } else {
            video.likes.addToSet(userId);
        }

        await video.save();

        res.status(200).json({
            liked: !hasLiked,
            likeCount: video.likes.length
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
