// File: src/api/index.js
import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    withCredentials: true,
});

/**
 * @typedef {Object} User
 * @property {string} _id
 * @property {string} username
 * @property {string} email
 * @property {string} [avatar]
 * @property {string[]} followers
 * @property {string[]} following
 */

/**
 * @typedef {Object} Video
 * @property {string} _id
 * @property {string} title
 * @property {string} description
 * @property {string[]} tags
 * @property {string} imagekitUrl
 * @property {string} thumbnailUrl
 * @property {number} viewCount
 * @property {string[]} likes
 * @property {Object} uploader
 * @property {string} createdAt
 */

// -- AUTH --

/**
 * Register a new user
 * @param {Object} data
 * @param {string} data.username
 * @param {string} data.email
 * @param {string} data.password
 * @returns {Promise<{message: string, user: User}>}
 */
export const register = async (data) => {
    const res = await api.post('/api/auth/register', data);
    return res.data;
};

/**
 * Login user
 * @param {Object} data
 * @param {string} data.email
 * @param {string} data.password
 * @returns {Promise<{message: string, user: User}>}
 */
export const login = async (data) => {
    const res = await api.post('/api/auth/login', data);
    return res.data;
};

/**
 * Logout user
 * @returns {Promise<{message: string}>}
 */
export const logout = async () => {
    const res = await api.post('/api/auth/logout');
    return res.data;
};

/**
 * Get current logged in user
 * @returns {Promise<User>}
 */
export const getMe = async () => {
    const res = await api.get('/api/auth/me');
    return res.data;
};

// -- VIDEOS --

/**
 * Get paginated list of videos
 * @param {number} page
 * @returns {Promise<{videos: Video[], totalPages: number, currentPage: number}>}
 */
export const getVideos = async (page = 1) => {
    const res = await api.get(`/api/videos?page=${page}`);
    return res.data;
};

/**
 * Get single video details
 * @param {string} id
 * @returns {Promise<Video>}
 */
export const getVideo = async (id) => {
    const res = await api.get(`/api/videos/${id}`);
    return res.data;
};

/**
 * Create a new video entry (post ImageKit upload)
 * @param {Object} data
 * @param {string} data.title
 * @param {string} data.description
 * @param {string[]} data.tags
 * @param {string} data.imagekitFileId
 * @param {string} data.imagekitUrl
 * @param {string} data.thumbnailUrl
 * @returns {Promise<Video>}
 */
export const createVideo = async (data) => {
    const res = await api.post('/api/videos', data);
    return res.data;
};

/**
 * Search videos by query
 * @param {string} q
 * @param {number} page
 * @returns {Promise<{videos: Video[], totalPages: number, currentPage: number}>}
 */
export const searchVideos = async (q, page = 1) => {
    const res = await api.get(`/api/videos/search?q=${encodeURIComponent(q)}&page=${page}`);
    return res.data;
};

// -- INTERACTIONS --

/**
 * Increment view count for a video
 * @param {string} id
 * @returns {Promise<{viewCount: number}>}
 */
export const incrementView = async (id) => {
    const res = await api.patch(`/api/videos/${id}/view`);
    return res.data;
};

/**
 * Toggle like for a video
 * @param {string} id
 * @returns {Promise<{liked: boolean, likeCount: number}>}
 */
export const toggleLike = async (id) => {
    const res = await api.patch(`/api/videos/${id}/like`);
    return res.data;
};

// -- UPLOAD --

/**
 * Get ImageKit authentication parameters
 * @returns {Promise<{token: string, expire: number, signature: string, publicKey: string}>}
 */
export const getUploadAuth = async () => {
    const res = await api.get('/api/upload/auth');
    return res.data;
};

// -- USERS --

/**
 * Get user profile and videos
 * @param {string} username
 * @returns {Promise<{_id: string, username: string, avatar: string, followerCount: number, followingCount: number, videos: Video[]}>}
 */
export const getProfile = async (username) => {
    const res = await api.get(`/api/users/${username}`);
    return res.data;
};

/**
 * Toggle follow user
 * @param {string} id 
 * @returns {Promise<{following: boolean, followerCount: number}>}
 */
export const followUser = async (id) => {
    const res = await api.patch(`/api/users/${id}/follow`);
    return res.data;
};
