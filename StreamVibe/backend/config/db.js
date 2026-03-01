// File: config/db.js | Purpose: Connects to MongoDB Atlas using mongoose | Exports: connectDB
const mongoose = require('mongoose');

/**
 * Connects to the MongoDB Atlas cluster using the URI from environment variables.
 * Exits the process if the connection fails.
 * 
 * @async
 * @function connectDB
 * @returns {Promise<void>} Resolves when the connection is successful.
 */
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('MongoDB connected');
  } catch (error) {
    console.error('MongoDB connection error:', error.message);
    process.exit(1);
  }
};

module.exports = connectDB;
