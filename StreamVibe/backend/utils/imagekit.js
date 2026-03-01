// File: utils/imagekit.js | Purpose: Instantiates ImageKit singleton | Exports: imagekit instance
const ImageKit = require('imagekit');

/**
 * Singleton instance of ImageKit SDK used for generating client-side auth tokens.
 * Flow logic: Used by Upload route to generate signature parameters.
 * @type {ImageKit}
 */
const imagekit = new ImageKit({
    publicKey: process.env.IMAGEKIT_PUBLIC_KEY,
    privateKey: process.env.IMAGEKIT_PRIVATE_KEY,
    urlEndpoint: process.env.IMAGEKIT_URL_ENDPOINT,
});

module.exports = imagekit;
