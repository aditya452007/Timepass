# BACKEND_STRUCTURE.md — Database Schema & API Endpoints

---

## DATABASE: MongoDB Atlas

All collections are managed via Mongoose models.

---

## MONGOOSE MODELS (SCHEMAS)

### `User` — `backend/models/User.js`

```js
{
  username:     { type: String, required: true, unique: true, trim: true, minlength: 3, maxlength: 30 },
  email:        { type: String, required: true, unique: true, lowercase: true },
  passwordHash: { type: String, required: true },             // bcrypt hash
  avatar:       { type: String, default: '' },                // optional image URL
  followers:    [{ type: ObjectId, ref: 'User' }],           // array of user IDs
  following:    [{ type: ObjectId, ref: 'User' }],           // array of user IDs
  createdAt:    { type: Date, default: Date.now }
}
```

### `Video` — `backend/models/Video.js`

```js
{
  title:         { type: String, required: true, trim: true, maxlength: 100 },
  description:   { type: String, default: '', maxlength: 500 },
  tags:          [{ type: String }],                          // e.g. ['funny', 'travel']
  uploader:      { type: ObjectId, ref: 'User', required: true },
  imagekitFileId: { type: String, required: true },           // ImageKit internal file ID
  imagekitUrl:   { type: String, required: true },            // ImageKit base URL for the video
  thumbnailUrl:  { type: String, default: '' },               // ImageKit thumbnail URL
  viewCount:     { type: Number, default: 0 },
  likes:         [{ type: ObjectId, ref: 'User' }],          // users who liked
  createdAt:     { type: Date, default: Date.now }
}
```

---

## API ENDPOINTS

All routes are prefixed with `/api`.  
Auth-protected routes require a valid JWT in the `Authorization: Bearer <token>` header OR in an `httpOnly` cookie named `token`.

---

### AUTH ROUTES — `/api/auth`

#### `POST /api/auth/register`
Register a new user.

**Body:**
```json
{ "username": "johndoe", "email": "john@email.com", "password": "secret123" }
```

**Response 201:**
```json
{ "message": "Registered", "user": { "_id": "...", "username": "johndoe", "email": "..." } }
```
Sets `token` httpOnly cookie.

**Errors:** 400 if missing fields, 409 if email/username taken.

---

#### `POST /api/auth/login`
Login existing user.

**Body:**
```json
{ "email": "john@email.com", "password": "secret123" }
```

**Response 200:**
```json
{ "message": "Logged in", "user": { "_id": "...", "username": "johndoe" } }
```
Sets `token` httpOnly cookie.

**Errors:** 400 bad input, 401 wrong credentials.

---

#### `POST /api/auth/logout`
Clear the auth cookie.

**Response 200:** `{ "message": "Logged out" }`

---

#### `GET /api/auth/me`
Get the currently logged-in user. **(Auth required)**

**Response 200:**
```json
{ "_id": "...", "username": "johndoe", "email": "...", "followers": [...], "following": [...] }
```

---

### VIDEO ROUTES — `/api/videos`

#### `GET /api/videos`
Get all videos, newest first. Supports pagination.

**Query params:**
- `page` (default: 1)
- `limit` (default: 12)

**Response 200:**
```json
{
  "videos": [ { "_id": "...", "title": "...", "thumbnailUrl": "...", "viewCount": 42, "uploader": { "username": "johndoe" }, "createdAt": "..." } ],
  "totalPages": 5,
  "currentPage": 1
}
```

---

#### `GET /api/videos/:id`
Get a single video by ID.

**Response 200:**
```json
{
  "_id": "...",
  "title": "...",
  "description": "...",
  "tags": ["funny"],
  "imagekitUrl": "https://ik.imagekit.io/...",
  "thumbnailUrl": "...",
  "viewCount": 43,
  "likes": ["userId1", "userId2"],
  "uploader": { "_id": "...", "username": "johndoe" },
  "createdAt": "..."
}
```

---

#### `POST /api/videos`
Save video metadata after ImageKit upload. **(Auth required)**

**Body:**
```json
{
  "title": "My Video",
  "description": "Cool video",
  "tags": ["tag1", "tag2"],
  "imagekitFileId": "file_abc123",
  "imagekitUrl": "https://ik.imagekit.io/myid/myvideo.mp4",
  "thumbnailUrl": "https://ik.imagekit.io/myid/myvideo.mp4/ik-thumbnail.jpg"
}
```

**Response 201:**
```json
{ "_id": "...", "title": "My Video", ... }
```

---

#### `PATCH /api/videos/:id/view`
Increment view count by 1. (No auth required)

**Response 200:** `{ "viewCount": 44 }`

---

#### `PATCH /api/videos/:id/like`
Toggle like on a video. **(Auth required)**

**Response 200:**
```json
{ "liked": true, "likeCount": 10 }
```
or `{ "liked": false, "likeCount": 9 }` if unliked.

---

#### `GET /api/videos/search`
Search videos by title.

**Query params:** `q` (search term)

**Response 200:** Same shape as `GET /api/videos` paginated response.

---

### USER ROUTES — `/api/users`

#### `GET /api/users/:username`
Get a user's public profile.

**Response 200:**
```json
{
  "_id": "...",
  "username": "johndoe",
  "followerCount": 5,
  "followingCount": 3,
  "videos": [ /* array of user's videos */ ]
}
```

---

#### `PATCH /api/users/:id/follow`
Follow or unfollow a user. **(Auth required)**

**Response 200:**
```json
{ "following": true, "followerCount": 6 }
```
or `{ "following": false, "followerCount": 5 }` if unfollowed.

---

### UPLOAD ROUTES — `/api/upload`

#### `GET /api/upload/auth`
Generate ImageKit authentication parameters for client-side upload. **(Auth required)**

**Response 200:**
```json
{
  "token": "...",
  "expire": 1234567890,
  "signature": "...",
  "publicKey": "public_xxxxx"
}
```

The frontend uses these params to upload the file directly to ImageKit.io without sending the file through your server.

---

## HOW THE UPLOAD FLOW WORKS (DETAILED)

```
1. Frontend:  GET /api/upload/auth
              ↓ receives { token, expire, signature, publicKey }

2. Frontend:  POST https://upload.imagekit.io/api/v1/files/upload
              Body (FormData):
                - file: <the MP4 file>
                - fileName: "myvideo.mp4"
                - publicKey: "public_xxx"
                - signature: "..."
                - expire: 1234567890
                - token: "..."
                - folder: "/videos"
              ↓ ImageKit returns { fileId, url, name, ... }

3. Frontend:  POST /api/videos
              Body: { title, description, tags, imagekitFileId, imagekitUrl, thumbnailUrl }
              ↓ Server saves to MongoDB

4. Frontend:  Show success + link to /watch/:newVideoId
```

---

## HLS STREAMING URL FORMAT

ImageKit serves HLS for any uploaded video by appending `/ik-master.m3u8` to the base video URL:

```
Video uploaded URL:  https://ik.imagekit.io/myid/videos/myvideo.mp4
HLS manifest URL:    https://ik.imagekit.io/myid/videos/myvideo.mp4/ik-master.m3u8
```

Video.js in the frontend player uses the `.m3u8` URL to stream adaptively.

---

## MIDDLEWARE

### `backend/middleware/auth.js`

```js
// Reads JWT from cookie or Authorization header
// If valid: attaches decoded user to req.user
// If invalid/missing: returns 401
```

Usage: Add to any route that requires authentication:
```js
router.post('/api/videos', authMiddleware, createVideo);
```

---

## ERROR RESPONSE FORMAT

All errors follow this shape:
```json
{ "error": "Human readable message" }
```

HTTP status codes:
- `400` — Bad request / validation error
- `401` — Not authenticated
- `403` — Authenticated but not allowed
- `404` — Resource not found
- `409` — Conflict (e.g., duplicate email)
- `500` — Server error
