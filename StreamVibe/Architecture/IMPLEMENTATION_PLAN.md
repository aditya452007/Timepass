# IMPLEMENTATION_PLAN.md — Step-by-Step Build Sequence

> Rules for the AI agent:
> - Complete each step fully before moving to the next
> - Each step is a SMALL, testable task
> - After each step, verify it works before continuing
> - Do NOT skip ahead or combine multiple steps

---

## PHASE 1 — PROJECT SETUP

### Step 1.1 — Create folder structure
```
mkdir streamvibe
cd streamvibe
mkdir backend frontend
```

### Step 1.2 — Create .gitignore in root
Contents:
```
node_modules/
.env
dist/
.DS_Store
```

### Step 1.3 — Create .env in root
Copy the template from TECH_STACK.md. Fill in real values from:
- MongoDB Atlas (get connection string from Atlas dashboard)
- ImageKit.io (get keys from ImageKit dashboard)
- Make up a random JWT_SECRET (32+ characters)

### Step 1.4 — Initialize backend package.json
```bash
cd backend
npm init -y
npm install express mongoose bcryptjs jsonwebtoken cookie-parser cors dotenv imagekitio-node
npm install --save-dev nodemon
```

Add to `package.json` scripts:
```json
"scripts": {
  "start": "node server.js",
  "dev": "nodemon server.js"
}
```

### Step 1.5 — Initialize frontend package.json
```bash
cd ../frontend
npm create vite@latest . -- --template react
npm install
npm install axios react-router-dom video.js videojs-http-streaming
```

---

## PHASE 2 — BACKEND: DATABASE + SERVER SKELETON

### Step 2.1 — Create `backend/config/db.js`
- Import mongoose
- Export a `connectDB()` function that calls `mongoose.connect(process.env.MONGODB_URI)`
- Log "MongoDB connected" on success, throw error on failure

### Step 2.2 — Create `backend/server.js`
- Import express, cors, cookie-parser, dotenv
- Call `dotenv.config()`
- Call `connectDB()`
- Set up middleware: `cors({ origin: 'http://localhost:5173', credentials: true })`, `express.json()`, `cookie-parser()`
- Mount placeholder routes: `app.get('/api/health', (req, res) => res.json({ ok: true }))`
- `app.listen(process.env.PORT || 5000)`

**Verify:** Run `npm run dev` in backend. Visit `http://localhost:5000/api/health` — should return `{ "ok": true }`.

---

## PHASE 3 — BACKEND: MODELS

### Step 3.1 — Create `backend/models/User.js`
- Copy the User schema exactly from BACKEND_STRUCTURE.md
- Export the Mongoose model

### Step 3.2 — Create `backend/models/Video.js`
- Copy the Video schema exactly from BACKEND_STRUCTURE.md
- Export the Mongoose model

---

## PHASE 4 — BACKEND: AUTH MIDDLEWARE + UTILS

### Step 4.1 — Create `backend/utils/imagekit.js`
```js
// Import ImageKit from 'imagekitio-node'
// Create and export a single ImageKit instance using env vars:
//   publicKey: process.env.IMAGEKIT_PUBLIC_KEY
//   privateKey: process.env.IMAGEKIT_PRIVATE_KEY
//   urlEndpoint: process.env.IMAGEKIT_URL_ENDPOINT
```

### Step 4.2 — Create `backend/middleware/auth.js`
```js
// 1. Try to get token from: req.cookies.token OR req.headers.authorization (Bearer token)
// 2. If no token → return res.status(401).json({ error: 'Not authenticated' })
// 3. Verify token with jwt.verify(token, process.env.JWT_SECRET)
// 4. If invalid → return 401
// 5. If valid → set req.user = { id: decoded.id } and call next()
```

---

## PHASE 5 — BACKEND: AUTH ROUTES

### Step 5.1 — Create `backend/routes/auth.js`

Implement `POST /register`:
1. Validate: username, email, password all present
2. Check if email already exists → 409 if so
3. Check if username taken → 409 if so
4. Hash password: `bcrypt.hash(password, 10)`
5. Create User document, save to DB
6. Sign JWT: `jwt.sign({ id: user._id }, secret, { expiresIn: '7d' })`
7. Set httpOnly cookie: `res.cookie('token', token, { httpOnly: true, maxAge: 7*24*60*60*1000 })`
8. Return 201 with user object (exclude passwordHash)

Implement `POST /login`:
1. Validate email + password present
2. Find user by email → 401 if not found
3. `bcrypt.compare(password, user.passwordHash)` → 401 if wrong
4. Sign JWT, set cookie, return 200 with user

Implement `POST /logout`:
1. `res.clearCookie('token')`
2. Return 200

Implement `GET /me` (auth middleware required):
1. Find user by `req.user.id` (exclude passwordHash)
2. Return 200 with user

### Step 5.2 — Mount auth routes in `server.js`
```js
const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);
```

**Verify:** Test register + login with a REST client (curl, Postman, or Thunder Client).

---

## PHASE 6 — BACKEND: UPLOAD ROUTE

### Step 6.1 — Create `backend/routes/upload.js`

Implement `GET /auth` (auth middleware required):
1. Call `imagekit.getAuthenticationParameters()` — this is built into the SDK
2. Return the result: `{ token, expire, signature, publicKey }`

### Step 6.2 — Mount upload route in `server.js`
```js
const uploadRoutes = require('./routes/upload');
app.use('/api/upload', uploadRoutes);
```

---

## PHASE 7 — BACKEND: VIDEO ROUTES

### Step 7.1 — Create `backend/routes/videos.js`

Implement `GET /` (list all, paginated):
1. Get `page` and `limit` from query (default 1 and 12)
2. `Video.find().sort({ createdAt: -1 }).skip((page-1)*limit).limit(limit).populate('uploader', 'username')`
3. Get total count with `Video.countDocuments()`
4. Return `{ videos, totalPages: Math.ceil(total/limit), currentPage: page }`

Implement `GET /search`:
1. Get `q` from query
2. `Video.find({ title: { $regex: q, $options: 'i' } }).populate('uploader', 'username')`
3. Return same paginated shape

Implement `GET /:id` (single video):
1. `Video.findById(id).populate('uploader', 'username avatar')`
2. 404 if not found
3. Return video

Implement `POST /` (auth required):
1. Get `title, description, tags, imagekitFileId, imagekitUrl, thumbnailUrl` from body
2. Validate title is present
3. Create Video: `{ title, description, tags, imagekitFileId, imagekitUrl, thumbnailUrl, uploader: req.user.id }`
4. Save and return 201

Implement `PATCH /:id/view`:
1. `Video.findByIdAndUpdate(id, { $inc: { viewCount: 1 } }, { new: true })`
2. Return `{ viewCount: video.viewCount }`

Implement `PATCH /:id/like` (auth required):
1. Find video by id
2. Check if `req.user.id` is in `video.likes`
3. If yes → `$pull` to unlike; if no → `$addToSet` to like
4. Save, return `{ liked: true/false, likeCount: video.likes.length }`

### Step 7.2 — Mount video routes in `server.js`
```js
const videoRoutes = require('./routes/videos');
app.use('/api/videos', videoRoutes);
```

---

## PHASE 8 — BACKEND: USER ROUTES

### Step 8.1 — Create `backend/routes/users.js`

Implement `GET /:username` (public profile):
1. Find user by username (not by id)
2. 404 if not found
3. Also fetch their videos: `Video.find({ uploader: user._id })`
4. Return `{ _id, username, followerCount: user.followers.length, followingCount: user.following.length, videos }`

Implement `PATCH /:id/follow` (auth required):
1. Cannot follow yourself → 400
2. Find target user
3. Check if `req.user.id` is in `target.followers`
4. If following → unfollow (remove from both users' arrays)
5. If not following → follow (add to both users' arrays)
6. Save both users
7. Return `{ following: true/false, followerCount: target.followers.length }`

### Step 8.2 — Mount user routes in `server.js`
```js
const userRoutes = require('./routes/users');
app.use('/api/users', userRoutes);
```

**Verify backend is complete:** All 5 route files work. Test every endpoint.

---

## PHASE 9 — FRONTEND: SETUP

### Step 9.1 — Clean up Vite default files
- Delete `src/App.css`, `src/assets/react.svg`
- Clear `src/App.jsx` completely

### Step 9.2 — Create `src/styles/global.css`
- Add all CSS variables from FRONTEND_GUIDELINES.md
- Add body reset:
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--color-bg-primary); color: var(--color-text-primary); font-family: var(--font-family); }
a { color: inherit; text-decoration: none; }
```

### Step 9.3 — Create `src/styles/components.css`
- Add all component styles from FRONTEND_GUIDELINES.md (Navbar, VideoCard, Buttons, Inputs, etc.)

### Step 9.4 — Create `src/api/index.js`
```js
// Single axios instance with base URL from env
// All API calls exported as named functions:
// - register(data), login(data), logout(), getMe()
// - getVideos(page), getVideo(id), createVideo(data), searchVideos(q)
// - incrementView(id), toggleLike(id)
// - getUploadAuth()
// - getProfile(username), followUser(id)
// Use withCredentials: true on the axios instance (for cookies)
```

### Step 9.5 — Create `src/context/AuthContext.jsx`
```jsx
// - Holds { user, loading } in state
// - On mount: call getMe() to check if user is already logged in
// - Exposes: login(userData), logout(), user, loading
// - Wrap entire app in <AuthProvider>
```

### Step 9.6 — Update `src/main.jsx`
```jsx
import './styles/global.css'
import './styles/components.css'
// Wrap <App> in <AuthProvider> and <BrowserRouter>
```

---

## PHASE 10 — FRONTEND: COMPONENTS

### Step 10.1 — Create `src/components/Navbar.jsx`
- Logo "StreamVibe" (links to `/`)
- Search bar (form with input, on submit navigate to `/search?q=...`)
- If user logged in: show username avatar + Logout button
- If not logged in: show Login + Register links
- Use `useAuth()` hook from AuthContext

### Step 10.2 — Create `src/components/VideoCard.jsx`
- Props: `{ video }` (has title, thumbnailUrl, uploader.username, viewCount, _id)
- Thumbnail img (link to `/watch/:id`)
- Title (link to `/watch/:id`)
- Username (link to `/profile/:username`)
- View count
- Apply `.video-card` CSS class

### Step 10.3 — Create `src/components/VideoPlayer.jsx`
- Props: `{ videoUrl }` (the ImageKit base URL)
- Construct HLS URL: `videoUrl + '/ik-master.m3u8'`
- Initialize Video.js player on a `<video>` ref
- Use `videojs({ sources: [{ src: hlsUrl, type: 'application/x-mpegURL' }] })`
- Cleanup: `player.dispose()` on unmount
- Apply 16:9 aspect ratio container

---

## PHASE 11 — FRONTEND: PAGES

### Step 11.1 — Create `src/pages/Home.jsx`
1. On mount: fetch `getVideos(page=1)`
2. Show video grid with `<VideoCard>` for each
3. "Load More" button calls `getVideos(page+1)` and appends

### Step 11.2 — Create `src/pages/Login.jsx`
1. Form: email + password
2. On submit: call `login(data)` API, update AuthContext, redirect to `/`
3. Show error if login fails
4. If already logged in: redirect to `/`

### Step 11.3 — Create `src/pages/Register.jsx`
1. Form: username + email + password
2. On submit: call `register(data)`, auto-login, redirect to `/`
3. Show errors inline

### Step 11.4 — Create `src/pages/Watch.jsx`
1. Get `videoId` from URL params
2. Fetch video data on mount, call `incrementView(videoId)` once
3. Render `<VideoPlayer videoUrl={video.imagekitUrl} />`
4. Show title, description, tags, uploader link
5. Like button: show count, call `toggleLike(id)` on click, update UI optimistically
6. If not logged in: Like button redirects to `/login`

### Step 11.5 — Create `src/pages/Profile.jsx`
1. Get `username` from URL params
2. Fetch profile with `getProfile(username)`
3. Show username, follower/following counts
4. Show Follow/Unfollow button (hide if own profile)
5. Video grid of user's videos

### Step 11.6 — Create `src/pages/Upload.jsx`
1. Guard: redirect to `/login` if not logged in
2. Form: file picker (`.mp4` only), title, description, tags
3. On submit:
   a. Call `getUploadAuth()` to get ImageKit auth params
   b. Build FormData with file + auth params
   c. POST directly to `https://upload.imagekit.io/api/v1/files/upload` with axios
   d. Track upload progress with `onUploadProgress` → update progress bar
   e. On success, call `createVideo()` with metadata
   f. Show success message + link to `/watch/:newId`

### Step 11.7 — Create `src/pages/Search.jsx`
1. Get `q` from URL query string
2. Fetch `searchVideos(q)` on mount and when `q` changes
3. Show video grid or "No results found"

---

## PHASE 12 — FRONTEND: ROUTER

### Step 12.1 — Update `src/App.jsx`
```jsx
// Import all pages
// Set up <Routes>:
//   / → <Home>
//   /login → <Login>
//   /register → <Register>
//   /upload → <Upload>
//   /watch/:videoId → <Watch>
//   /profile/:username → <Profile>
//   /search → <Search>
// Wrap all routes in <Navbar> layout
```

---

## PHASE 13 — FINAL WIRING + TEST

### Step 13.1 — Test full user journey
1. Register a new account → verify cookie is set
2. Login → verify redirect works
3. Upload a video → verify it appears in ImageKit dashboard
4. Go to `/` → verify video card shows
5. Click video → verify HLS playback starts in Video.js
6. Like video → verify count updates
7. Visit own profile → verify video shows there
8. Search by title → verify result appears
9. Logout → verify cookie cleared

### Step 13.2 — Fix any broken pieces found in 13.1
Only fix what's broken. Don't refactor working code.

### Step 13.3 — Add `.env.example` to repo root
Copy `.env` structure with all keys but empty values. Commit this file only.

---

## DONE ✓

The app is complete when Step 13.1 passes with no errors.
