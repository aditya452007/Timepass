// File: routes/users.js | Purpose: User profiles and follows | Exports: router
const express = require('express');
const router = express.Router();
const User = require('../models/User');
const Video = require('../models/Video');
const authMiddleware = require('../middleware/auth');

router.get('/:username', async (req, res) => {
    try {
        const user = await User.findOne({ username: req.params.username }).select('-passwordHash');
        if (!user) return res.status(404).json({ error: 'User not found' });

        const videos = await Video.find({ uploader: user._id })
            .sort({ createdAt: -1 })
            .populate('uploader', 'username');

        res.status(200).json({
            _id: user._id,
            username: user.username,
            avatar: user.avatar,
            followerCount: user.followers.length,
            followingCount: user.following.length,
            videos
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.patch('/:id/follow', authMiddleware, async (req, res) => {
    try {
        if (req.params.id === req.user.id) {
            return res.status(400).json({ error: 'Cannot follow yourself' });
        }

        const targetUser = await User.findById(req.params.id);
        if (!targetUser) return res.status(404).json({ error: 'User not found' });

        const currentUser = await User.findById(req.user.id);
        if (!currentUser) return res.status(404).json({ error: 'Current user not found' });

        const isFollowing = targetUser.followers.includes(req.user.id);

        if (isFollowing) {
            targetUser.followers.pull(req.user.id);
            currentUser.following.pull(req.params.id);
        } else {
            targetUser.followers.addToSet(req.user.id);
            currentUser.following.addToSet(req.params.id);
        }

        await targetUser.save();
        await currentUser.save();

        res.status(200).json({
            following: !isFollowing,
            followerCount: targetUser.followers.length
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
