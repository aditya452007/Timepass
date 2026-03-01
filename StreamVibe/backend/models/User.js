// File: models/User.js | Purpose: Defines the User schema and model | Exports: User model
const mongoose = require('mongoose');

/**
 * @typedef {Object} IUser
 * @property {string} username - Unique, trimmed, 3-30 chars
 * @property {string} email - Unique, lowercase
 * @property {string} passwordHash - bcrypt hash
 * @property {string} avatar - Optional image URL
 * @property {mongoose.Types.ObjectId[]} followers - Array of follower IDs
 * @property {mongoose.Types.ObjectId[]} following - Array of following IDs
 * @property {Date} createdAt - Timestamp
 */

const userSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true, trim: true, minlength: 3, maxlength: 30 },
    email: { type: String, required: true, unique: true, lowercase: true },
    passwordHash: { type: String, required: true },
    avatar: { type: String, default: '' },
    followers: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    following: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', userSchema);
