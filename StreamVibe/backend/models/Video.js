// File: models/Video.js | Purpose: Defines the Video schema and model | Exports: Video model
const mongoose = require('mongoose');

/**
 * @typedef {Object} IVideo
 * @property {string} title - Required, max 100
 * @property {string} description - Max 500
 * @property {string[]} tags - e.g. ['funny', 'travel']
 * @property {mongoose.Types.ObjectId} uploader - Reference to User
 * @property {string} imagekitFileId - ImageKit internal file ID
 * @property {string} imagekitUrl - ImageKit base URL for the video
 * @property {string} thumbnailUrl - ImageKit thumbnail URL
 * @property {number} viewCount - Number of views
 * @property {mongoose.Types.ObjectId[]} likes - Array of user IDs who liked
 * @property {Date} createdAt - Timestamp
 */

const videoSchema = new mongoose.Schema({
    title: { type: String, required: true, trim: true, maxlength: 100 },
    description: { type: String, default: '', maxlength: 500 },
    tags: [{ type: String }],
    uploader: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    imagekitFileId: { type: String, required: true },
    imagekitUrl: { type: String, required: true },
    thumbnailUrl: { type: String, default: '' },
    viewCount: { type: Number, default: 0 },
    likes: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Video', videoSchema);
