# StreamVibe Build Agent

## Overview

This SOP guides an AI agent through building **StreamVibe** — a full-stack video streaming web
application similar to Instagram and YouTube. The agent will scaffold, implement, and verify a
complete working app using MongoDB Atlas for data persistence and ImageKit.io for video
upload and HLS streaming.

The agent operates in a **Windows PowerShell terminal**. All shell commands in this SOP use
PowerShell syntax only. The `&&` operator does NOT work in PowerShell — use separate
commands or `;` for chaining when absolutely necessary.

The agent **MUST** use two registered skills throughout execution:
- `ui-ux-pro-max` — for all UI decisions, component structure, color application, and layout
- `typescript-expert` — for all TypeScript typing, interface design, and type-safe patterns

The source of truth for all decisions is the `architecture/` folder in the project root.
That folder contains seven files the agent **MUST** read before writing a single line of code:

```
architecture/
├── PRD.md                  ← Features in scope. Features OUT of scope. Read this first.
├── APP_FLOW.md             ← Every page, every route, every user path
├── TECH_STACK.md           ← Exact package versions and folder structure
├── FRONTEND_GUIDELINES.md  ← Color system, spacing, typography, component specs
├── BACKEND_STRUCTURE.md    ← MongoDB schemas, every API endpoint, upload flow
├── IMPLEMENTATION_PLAN.md  ← The build sequence (this SOP maps to it)
└── AGENT_PROMPT.md         ← High-level behavioral rules for the agent
```

---

## Parameters

- **project_root** (required): Absolute path to the folder where StreamVibe will be built (e.g., `C:\Users\dev\projects\streamvibe`)
- **mongodb_uri** (required): MongoDB Atlas connection string (e.g., `mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/streamvibe?retryWrites=true&w=majority`)
- **imagekit_public_key** (required): ImageKit.io public key (starts with `public_`)
- **imagekit_private_key** (required): ImageKit.io private key (starts with `private_`)
- **imagekit_url_endpoint** (required): ImageKit.io URL endpoint (e.g., `https://ik.imagekit.io/your_id`)
- **jwt_secret** (required): A random string of at least 32 characters for signing JWTs
- **skip_to_phase** (optional, default: `"1"`): Phase number to resume from if the build was interrupted (e.g., `"7"`)

**Constraints for parameter acquisition:**
- If all required parameters are already provided, You MUST proceed to the Steps
- If any required parameters are missing, You MUST ask for them before proceeding
- When asking for parameters, You MUST request all parameters in a single prompt
- When asking for parameters, You MUST use the exact parameter names as defined
- You MUST support multiple input methods including:
  - Direct input: Values typed inline
  - File path: Path to a `.env` file containing these values
- If a file path is provided, You MUST read the file and extract values before proceeding
- You MUST confirm all six required values are acquired before starting Step 1

---

## Steps

### 1. Read Architecture Documents

Read every file in the `architecture/` directory before doing anything else.

**Constraints:**
- You MUST read all seven files in `architecture/` completely before writing any code
- You MUST read them in this order: `PRD.md` → `APP_FLOW.md` → `TECH_STACK.md` → `FRONTEND_GUIDELINES.md` → `BACKEND_STRUCTURE.md` → `IMPLEMENTATION_PLAN.md` → `AGENT_PROMPT.md`
- You MUST NOT skip or skim any file because every decision downstream depends on them
- After reading, You MUST confirm internally: what features are in scope, what is forbidden (glassmorphism, purple, Google Fonts), and what the full folder structure looks like
- If `architecture/` does not exist at `project_root`, You MUST stop and report the error — do not guess at requirements

---

### 2. PowerShell Environment Check

Verify the terminal and required tools are available.

**Constraints:**
- You MUST run each verification command as a **separate PowerShell command** — never chain with `&&`
- You MUST check Node.js version: `node --version`
- You MUST check npm version: `npm --version`
- You MUST verify Node.js is version 18 or higher — if it is lower, You MUST stop and ask the user to upgrade
- You MUST NOT use `&&` at any point in this SOP because PowerShell does not support `&&` for command chaining
- When you need to run multiple commands in sequence, You MUST run them one at a time as separate tool calls
- You SHOULD note the PowerShell execution policy with `Get-ExecutionPolicy` — if it is `Restricted`, you MUST inform the user to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` before continuing

---

### 3. Create Root Folder Structure

Create the project folder and all required subdirectories.

**Constraints:**
- You MUST navigate to `project_root` first: `Set-Location "project_root_value"`
- You MUST create the backend folder: `New-Item -ItemType Directory -Path "backend" -Force`
- You MUST create the frontend folder separately: `New-Item -ItemType Directory -Path "frontend" -Force`
- You MUST create each subdirectory as a **separate command** — not chained
- The full backend subdirectory tree to create (each as a separate `New-Item` command):
  ```
  backend\config
  backend\models
  backend\routes
  backend\middleware
  backend\utils
  ```
- You MUST NOT use `mkdir a && mkdir b` syntax — use individual `New-Item` commands
- You SHOULD verify the structure was created: `Get-ChildItem -Recurse -Directory`

---

### 4. Create .env and .gitignore

Write all secrets to the `.env` file and protect it with `.gitignore`.

**Constraints:**
- You MUST create `.env` in `project_root` (not inside backend or frontend)
- You MUST write the `.env` file with exactly these keys populated from the acquired parameters:
  ```
  MONGODB_URI=<mongodb_uri>
  JWT_SECRET=<jwt_secret>
  JWT_EXPIRES_IN=7d
  IMAGEKIT_PUBLIC_KEY=<imagekit_public_key>
  IMAGEKIT_PRIVATE_KEY=<imagekit_private_key>
  IMAGEKIT_URL_ENDPOINT=<imagekit_url_endpoint>
  PORT=5000
  NODE_ENV=development
  VITE_API_BASE_URL=http://localhost:5000
  VITE_IMAGEKIT_URL_ENDPOINT=<imagekit_url_endpoint>
  ```
- You MUST create `.env.example` with all the same keys but empty values — this file IS safe to commit
- You MUST create `.gitignore` in `project_root` with at minimum:
  ```
  node_modules/
  .env
  dist/
  .DS_Store
  *.log
  ```
- You MUST NOT log or print the actual secret values in any output visible to the user after this step

---

### 5. Initialize Backend (package.json + install)

Set up the Node.js/Express backend project.

**Constraints:**
- You MUST navigate into the backend folder first: `Set-Location "backend"`
- You MUST initialize package.json: `npm init -y`
- You MUST install production dependencies as a **single npm install command**:
  ```
  npm install express mongoose bcryptjs jsonwebtoken cookie-parser cors dotenv imagekitio-node
  ```
- You MUST install dev dependencies as a separate command:
  ```
  npm install --save-dev nodemon
  ```
- You MUST add these scripts to `backend\package.json`:
  ```json
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  }
  ```
- You MUST NOT run `npm install` and script-editing in the same command
- After install completes, You MUST return to `project_root`: `Set-Location ".."`

---

### 6. Initialize Frontend (Vite + React)

Scaffold the React frontend using Vite.

**Constraints:**
- You MUST run Vite scaffold from `project_root`, targeting the `frontend` subdirectory:
  ```
  npm create vite@latest frontend -- --template react
  ```
- You MUST navigate into frontend: `Set-Location "frontend"`
- You MUST install base dependencies: `npm install`
- You MUST install additional dependencies as a **single command**:
  ```
  npm install axios react-router-dom video.js videojs-http-streaming
  ```
- You MUST delete the Vite default boilerplate files that are not needed:
  - `src\App.css` — delete with `Remove-Item "src\App.css" -Force`
  - `src\assets\react.svg` — delete with `Remove-Item "src\assets\react.svg" -Force`
- You MUST clear `src\App.jsx` completely (overwrite with empty component shell)
- You MUST return to `project_root`: `Set-Location ".."`
- You MUST NOT use `cd` — always use `Set-Location` in PowerShell

---

### 7. Build Backend — Config, Utils, Middleware

Create the foundational backend files before routes or models.

**Activate skill:** `typescript-expert` — apply strict JSDoc typing to all backend files.

**Constraints:**
- You MUST create `backend\config\db.js` with:
  - A `connectDB()` async function that calls `mongoose.connect(process.env.MONGODB_URI)`
  - A `console.log('MongoDB connected')` on success
  - A `process.exit(1)` on connection failure (with the error logged)
  - A JSDoc comment at the top of the file explaining its purpose and export
- You MUST create `backend\utils\imagekit.js` with:
  - A single ImageKit SDK instance exported as default
  - Reads `IMAGEKIT_PUBLIC_KEY`, `IMAGEKIT_PRIVATE_KEY`, `IMAGEKIT_URL_ENDPOINT` from `process.env`
  - A JSDoc comment explaining this is the singleton ImageKit instance used for auth token generation
- You MUST create `backend\middleware\auth.js` with:
  - A middleware function that reads JWT from `req.cookies.token` OR `req.headers.authorization` (Bearer token)
  - Returns `res.status(401).json({ error: 'Not authenticated' })` if no token or invalid token
  - Sets `req.user = { id: decoded.id }` and calls `next()` on valid token
  - A JSDoc comment on the middleware function
- Each file MUST have a top-of-file comment block: `// File: <filename> | Purpose: <one line> | Exports: <what it exports>`

---

### 8. Build Backend — Mongoose Models

Create the two database models exactly as specified in `architecture/BACKEND_STRUCTURE.md`.

**Activate skill:** `typescript-expert` — add JSDoc typedefs for each schema shape.

**Constraints:**
- You MUST create `backend\models\User.js` with the User schema from `BACKEND_STRUCTURE.md` — do not add or remove any fields
- You MUST create `backend\models\Video.js` with the Video schema from `BACKEND_STRUCTURE.md` — do not add or remove any fields
- Each model file MUST have:
  - A top-of-file comment block
  - JSDoc `@typedef` comment describing the document shape
  - The Mongoose schema definition
  - `module.exports = mongoose.model('ModelName', schema)`
- You MUST NOT add extra fields like `updatedAt`, `isDeleted`, `__v` hiding, or soft deletes — these are out of scope per `PRD.md`

---

### 9. Build Backend — server.js (Entry Point)

Create the main Express server file that wires everything together.

**Constraints:**
- You MUST create `backend\server.js` as the entry point
- It MUST call `require('dotenv').config()` as the **very first line** before any other require
- It MUST call `connectDB()` from `config/db.js`
- It MUST configure middleware in this order:
  1. `cors({ origin: 'http://localhost:5173', credentials: true })` — credentials: true is REQUIRED for cookies to work
  2. `express.json()`
  3. `cookie-parser()`
- It MUST include a health check: `app.get('/api/health', (req, res) => res.json({ ok: true, timestamp: new Date().toISOString() }))`
- It MUST have placeholder comments for route mounting (the routes will be added in the next steps):
  ```js
  // Routes will be mounted here in Steps 10-13
  ```
- It MUST call `app.listen(process.env.PORT || 5000, ...)`
- After creating the file, You MUST start the server and verify it works:
  - Run: `Set-Location "backend"` then `node server.js`
  - Confirm `http://localhost:5000/api/health` returns `{ "ok": true }`
  - Stop the server after verification
  - Return to `project_root`

---

### 10. Build Backend — Auth Routes

Implement all authentication endpoints.

**Constraints:**
- You MUST create `backend\routes\auth.js` implementing all four endpoints from `BACKEND_STRUCTURE.md`:
  - `POST /register` — validate fields, check duplicates, hash password with bcrypt (rounds: 10), create user, sign JWT, set httpOnly cookie, return 201
  - `POST /login` — find by email, compare password, sign JWT, set cookie, return 200
  - `POST /logout` — clear cookie, return 200
  - `GET /me` — auth middleware required, return current user (MUST use `.select('-passwordHash')`)
- You MUST set the JWT cookie with: `res.cookie('token', token, { httpOnly: true, maxAge: 7 * 24 * 60 * 60 * 1000 })`
- You MUST wrap every route handler in try/catch — on catch return `res.status(500).json({ error: err.message })`
- You MUST validate required fields at the top of each handler and return 400 if missing
- You MUST mount this router in `backend\server.js`: `app.use('/api/auth', require('./routes/auth'))`
- You MUST NOT return `passwordHash` in any response — ever

---

### 11. Build Backend — Upload Route

Implement the ImageKit authentication endpoint for client-side direct upload.

**Constraints:**
- You MUST create `backend\routes\upload.js` with one endpoint:
  - `GET /auth` — auth middleware required — calls `imagekit.getAuthenticationParameters()` and returns the result
- The response shape MUST be: `{ token, expire, signature, publicKey: process.env.IMAGEKIT_PUBLIC_KEY }`
- You MUST mount this router in `backend\server.js`: `app.use('/api/upload', require('./routes/upload'))`
- You MUST add a JSDoc comment explaining the ImageKit direct upload flow:
  ```
  // This endpoint provides auth params so the frontend can upload files
  // DIRECTLY to ImageKit without routing the video through this server.
  // Flow: 1) Frontend calls GET /api/upload/auth
  //       2) Frontend uploads file to ImageKit using returned params
  //       3) Frontend calls POST /api/videos with the resulting metadata
  ```

---

### 12. Build Backend — Video Routes

Implement all video CRUD and interaction endpoints.

**Constraints:**
- You MUST create `backend\routes\videos.js` implementing all six endpoints from `BACKEND_STRUCTURE.md`:
  - `GET /` — paginated list (page, limit=12), sorted newest first, populate uploader username
  - `GET /search` — text search on title using `$regex` with `$options: 'i'`, same paginated shape
  - `GET /:id` — single video, populate uploader with username and avatar
  - `POST /` — auth required, create video from body fields, return 201
  - `PATCH /:id/view` — no auth, increment viewCount by 1 with `$inc`, return `{ viewCount }`
  - `PATCH /:id/like` — auth required, toggle like using `$addToSet` / `$pull`, return `{ liked, likeCount }`
- You MUST put the `GET /search` route BEFORE `GET /:id` in the file — otherwise Express will interpret "search" as an ID
- You MUST wrap every handler in try/catch
- You MUST mount this router: `app.use('/api/videos', require('./routes/videos'))`

---

### 13. Build Backend — User Routes

Implement user profile and follow/unfollow endpoints.

**Constraints:**
- You MUST create `backend\routes\users.js` implementing both endpoints from `BACKEND_STRUCTURE.md`:
  - `GET /:username` — find by username (not _id), fetch their videos separately, return profile shape
  - `PATCH /:id/follow` — auth required, prevent self-follow (return 400), toggle follow on both users
- For the follow toggle: check if `req.user.id` exists in `target.followers`
  - If following: use `$pull` on both users' arrays to unfollow
  - If not following: use `$addToSet` on both users' arrays to follow
  - Save both user documents separately (two `await user.save()` calls)
- You MUST mount this router: `app.use('/api/users', require('./routes/users'))`
- After mounting all routes, You MUST do a final backend verification:
  - Start the server: `Set-Location "backend"` then `node server.js`
  - Test `GET /api/health` returns 200
  - Stop the server and return to `project_root`

---

### 14. Build Frontend — CSS Design System

Create the global CSS files using the exact design tokens from `architecture/FRONTEND_GUIDELINES.md`.

**Activate skill:** `ui-ux-pro-max` — apply the full design system rigorously.

**Constraints:**
- You MUST create `frontend\src\styles\global.css` containing:
  - ALL CSS custom properties (variables) from `FRONTEND_GUIDELINES.md` inside `:root {}`
  - Body reset: `*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }`
  - Body styles: background `var(--color-bg-primary)`, color `var(--color-text-primary)`, font-family `var(--font-family)`
  - Anchor reset: `a { color: inherit; text-decoration: none; }`
- You MUST create `frontend\src\styles\components.css` containing CSS classes for:
  - `.navbar` — sticky, 60px height, bg secondary, z-index 100
  - `.video-grid` — CSS Grid, 3 columns desktop, 2 tablet, 1 mobile (using media queries)
  - `.video-card` — bg secondary, border, border-radius lg, hover transform
  - `.btn-primary` — red background accent, white text, border-radius md, transitions
  - `.btn-ghost` — transparent background, border, hover bg hover color
  - `.form-input` — bg secondary, border, border-radius md, focus border accent
  - `.avatar` — circle 36px, bg accent, white text, border-radius full
  - `.progress-bar` and `.progress-fill` — for upload progress
  - `.tag-chip` — small pill for video tags
- You MUST NOT import any external fonts — system font stack only
- You MUST NOT use glassmorphism, `backdrop-filter`, or gradient backgrounds anywhere
- You MUST NOT use purple, violet, or indigo as any color value anywhere in the CSS

---

### 15. Build Frontend — API Layer

Create the centralized API module.

**Activate skill:** `typescript-expert` — add JSDoc types for all function signatures and return types.

**Constraints:**
- You MUST create `frontend\src\api\index.js` as the single file that contains ALL axios API calls
- You MUST create a single axios instance at the top of the file:
  ```js
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    withCredentials: true,  // Required for httpOnly cookie auth
  });
  ```
- You MUST export these named functions (no default export from this file):
  - Auth: `register(data)`, `login(data)`, `logout()`, `getMe()`
  - Videos: `getVideos(page)`, `getVideo(id)`, `createVideo(data)`, `searchVideos(q, page)`
  - Interactions: `incrementView(id)`, `toggleLike(id)`
  - Upload: `getUploadAuth()`
  - Users: `getProfile(username)`, `followUser(id)`
- Each function MUST have a JSDoc comment with `@param` and `@returns` types
- You MUST NOT call axios directly from any component or page — all API calls go through this file
- You MUST NOT put any ImageKit upload logic here — that upload goes directly to ImageKit's API from the Upload page (Step 22)

---

### 16. Build Frontend — AuthContext

Create global authentication state management.

**Constraints:**
- You MUST create `frontend\src\context\AuthContext.jsx`
- It MUST export:
  - `AuthProvider` component that wraps children
  - `useAuth` custom hook that returns `{ user, loading, login, logout }`
- On mount, `AuthProvider` MUST call `getMe()` to restore session state from cookie
- The `login(userData)` function MUST update the user state (receives user object from the auth API response)
- The `logout()` function MUST call the `logout()` API then clear user state
- Loading MUST be `true` during the initial `getMe()` call and `false` after (whether it succeeds or fails)
- You MUST NOT redirect inside AuthContext — components handle their own redirects

---

### 17. Build Frontend — Update main.jsx and App.jsx

Wire up providers and routing.

**Constraints:**
- You MUST update `frontend\src\main.jsx` to:
  - Import `./styles/global.css`
  - Import `./styles/components.css`
  - Wrap `<App />` with `<BrowserRouter>` from react-router-dom
  - Wrap `<App />` with `<AuthProvider>` from AuthContext
  - Order MUST be: `<BrowserRouter><AuthProvider><App /></AuthProvider></BrowserRouter>`
- You MUST update `frontend\src\App.jsx` to:
  - Import all 7 page components (Home, Login, Register, Upload, Watch, Profile, Search)
  - Import `<Navbar>` component
  - Define all routes from `architecture/APP_FLOW.md`:
    - `/` → Home
    - `/login` → Login
    - `/register` → Register
    - `/upload` → Upload
    - `/watch/:videoId` → Watch
    - `/profile/:username` → Profile
    - `/search` → Search
  - Render `<Navbar />` outside of `<Routes>` so it appears on every page
- You MUST create stub/placeholder files for all page and component files that don't exist yet so the app compiles — each stub can return a simple `<div>PageName</div>` for now

---

### 18. Build Frontend — Navbar Component

**Activate skill:** `ui-ux-pro-max` — follow `.navbar` CSS class spec exactly.

**Constraints:**
- You MUST create `frontend\src\components\Navbar.jsx`
- It MUST use the `useAuth()` hook to get `{ user, logout }`
- It MUST render:
  - Logo: text "StreamVibe" in `--color-accent` red, links to `/`
  - Search bar: a form with an input, on submit navigates to `/search?q=<value>`
  - If `user` exists: show avatar (initials circle) + a Logout button that calls `logout()`
  - If `user` is null: show "Login" link to `/login` and "Register" link to `/register`
- It MUST use the `.navbar` CSS class
- You MUST NOT add any `useState` for the search input — use `useRef` or read the form event value directly on submit
- The avatar MUST show the first letter of `user.username` uppercase, styled with `.avatar` CSS class

---

### 19. Build Frontend — VideoCard Component

**Activate skill:** `ui-ux-pro-max` — follow `.video-card` CSS class spec exactly.

**Constraints:**
- You MUST create `frontend\src\components\VideoCard.jsx`
- It MUST accept a single prop: `video` (object)
- It MUST render:
  - Thumbnail `<img>` with `src={video.thumbnailUrl}`, wrapped in a `<Link to={/watch/${video._id}}>`, aspect ratio 16:9 via CSS
  - Title as `<Link to={/watch/${video._id}}>`, max 2 lines with CSS `line-clamp: 2`
  - Username as `<Link to={/profile/${video.uploader?.username}}>`, styled with `--color-text-secondary`
  - View count with `--color-text-secondary` styling
- It MUST use the `.video-card` CSS class
- You MUST handle missing thumbnail gracefully: if `video.thumbnailUrl` is empty, show a placeholder div with bg `--color-bg-hover`

---

### 20. Build Frontend — VideoPlayer Component

**Constraints:**
- You MUST create `frontend\src\components\VideoPlayer.jsx`
- It MUST accept one prop: `videoUrl` (the base ImageKit URL for the video file)
- It MUST construct the HLS URL internally: `const hlsUrl = videoUrl + '/ik-master.m3u8'`
- It MUST use a `useRef` to hold the video DOM element
- It MUST initialize Video.js in a `useEffect`:
  ```js
  const player = videojs(videoRef.current, {
    controls: true,
    responsive: true,
    fluid: true,
    sources: [{ src: hlsUrl, type: 'application/x-mpegURL' }]
  });
  ```
- It MUST clean up on unmount: `return () => { if (player) player.dispose(); }`
- It MUST import Video.js CSS: `import 'video.js/dist/video-js.css'`
- The container MUST have a 16:9 aspect ratio
- You MUST NOT pass the `.mp4` URL directly to the player — always use the `.m3u8` HLS URL

---

### 21. Build Frontend — Home Page

**Activate skill:** `ui-ux-pro-max` — use `.video-grid` CSS class for the grid layout.

**Constraints:**
- You MUST create `frontend\src\pages\Home.jsx`
- On mount, it MUST call `getVideos(1)` and store results in state
- It MUST render a grid of `<VideoCard>` components using the `.video-grid` CSS class
- It MUST show a "Load More" button that calls `getVideos(page + 1)` and appends new videos to the existing list
- It MUST show "Loading..." text while fetching
- It MUST show "No videos yet." if the response is empty
- You MUST NOT show a spinner or loader animation — plain text "Loading..." is sufficient

---

### 22. Build Frontend — Upload Page

This is the most complex page. The upload goes directly to ImageKit — not through your backend.

**Constraints:**
- You MUST create `frontend\src\pages\Upload.jsx`
- You MUST redirect to `/login` at the top if `user` is null (use `useNavigate` + `useEffect`)
- The form MUST include: file picker (`accept=".mp4"`), title input (required), description textarea, tags input (comma-separated)
- The upload flow MUST follow these steps in order:
  1. Call `getUploadAuth()` from the API to get `{ token, expire, signature, publicKey }`
  2. Build a `FormData` object with:
     - `file`: the selected MP4 file
     - `fileName`: the file's name
     - `publicKey`: from auth response
     - `signature`, `expire`, `token`: from auth response
     - `folder`: `"/videos"`
  3. POST the FormData to `https://upload.imagekit.io/api/v1/files/upload` using **axios directly** (not the api module) with `onUploadProgress` callback
  4. On ImageKit success, call `createVideo({ title, description, tags, imagekitFileId: response.fileId, imagekitUrl: response.url, thumbnailUrl: response.url + '/ik-thumbnail.jpg' })`
  5. Navigate to `/watch/:newVideoId`
- You MUST show a progress bar (`<div className="progress-bar"><div className="progress-fill" style={{ width: percent + '%' }} /></div>`) during upload
- You MUST show error messages inline if anything fails — do NOT use `alert()`
- You MUST disable the submit button while upload is in progress

---

### 23. Build Frontend — Watch Page

**Activate skill:** `ui-ux-pro-max` — layout the page with player on top, info below.

**Constraints:**
- You MUST create `frontend\src\pages\Watch.jsx`
- It MUST get `videoId` from `useParams()`
- On mount it MUST:
  1. Call `getVideo(videoId)` and store in state
  2. Call `incrementView(videoId)` once (do not repeat on re-render)
- It MUST render `<VideoPlayer videoUrl={video.imagekitUrl} />` when video data is available
- It MUST show: title, description, uploader username (as link to `/profile/:username`), view count
- It MUST render tags as `.tag-chip` elements
- The Like button MUST:
  - Show current like count
  - Show a filled heart (♥) if the current user has liked it, outline heart (♡) if not
  - Call `toggleLike(videoId)` on click and update count optimistically in state
  - If user is not logged in, clicking MUST navigate to `/login`
- It MUST show "Loading..." while fetching and "Video not found." if fetch returns null

---

### 24. Build Frontend — Login and Register Pages

**Constraints:**
- You MUST create `frontend\src\pages\Login.jsx` with:
  - Email and password inputs with `.form-input` CSS class
  - On submit: call `login({ email, password })` API, then call the AuthContext `login(user)` function, then navigate to `/`
  - Show error message in red text below the form if login fails
  - If user is already logged in (from AuthContext), redirect to `/`
  - Link to `/register`
- You MUST create `frontend\src\pages\Register.jsx` with:
  - Username, email, and password inputs with `.form-input` CSS class
  - On submit: call `register({ username, email, password })`, then AuthContext `login(user)`, then navigate to `/`
  - Show inline error messages
  - If user is already logged in, redirect to `/`
  - Link to `/login`
- Both pages MUST be centered on screen with a max-width of 400px card using `--color-bg-secondary` background

---

### 25. Build Frontend — Profile and Search Pages

**Constraints:**
- You MUST create `frontend\src\pages\Profile.jsx` with:
  - Gets `username` from `useParams()`
  - Calls `getProfile(username)` on mount
  - Shows username, follower count, following count
  - Shows Follow/Unfollow button (`.btn-primary` / `.btn-ghost`) — hidden if viewing own profile (compare `user._id === profile._id`)
  - Follow button calls `followUser(profile._id)` and updates counts optimistically
  - Grid of user's videos using `<VideoCard>` and `.video-grid` CSS class
- You MUST create `frontend\src\pages\Search.jsx` with:
  - Reads `q` from URL query string: `const [searchParams] = useSearchParams(); const q = searchParams.get('q')`
  - Calls `searchVideos(q)` whenever `q` changes (dependency in useEffect)
  - Shows "No results for 'q'" empty state
  - Shows same video grid as Home page

---

### 26. Final Integration and Verification

Run both servers and test the complete user journey.

**Constraints:**
- You MUST start the backend server: `Set-Location "backend"` then `npm run dev` — **in a separate terminal or background process**
- You MUST start the frontend: `Set-Location "frontend"` then `npm run dev` — **in a separate terminal**
- You MUST NOT try to run both servers in the same PowerShell command with `&&` or `&`
- You MUST verify each item in this checklist — report PASS or FAIL for each:
  - [ ] `http://localhost:5000/api/health` returns `{ ok: true }`
  - [ ] Register a new user → user saved in MongoDB Atlas
  - [ ] Login → `token` cookie appears in browser DevTools → Application → Cookies
  - [ ] Upload a video → file visible in ImageKit dashboard
  - [ ] Home page shows the uploaded video card
  - [ ] Watch page loads and HLS video plays in Video.js player
  - [ ] Like button toggles and count updates
  - [ ] Profile page shows user's uploaded videos
  - [ ] Search by title returns the video
  - [ ] Logout clears the cookie
- For any FAIL item, You MUST fix only that specific issue without modifying working code
- After all items PASS, You MUST report "Build complete. All 10 verification checks passed."

---

## Examples

### Example 1: Fresh Build from project root

**Input parameters:**
- `project_root`: `C:\Users\dev\projects\streamvibe`
- `mongodb_uri`: `mongodb+srv://dev:pass123@cluster0.abc.mongodb.net/streamvibe?retryWrites=true&w=majority`
- `imagekit_public_key`: `public_AbCdEfGhIjKlMnOp`
- `imagekit_private_key`: `private_AbCdEfGhIjKlMnOp`
- `imagekit_url_endpoint`: `https://ik.imagekit.io/myapp123`
- `jwt_secret`: `myapp_super_secret_key_at_least_32_characters_long`
- `skip_to_phase`: `"1"` (build from start)

**Expected behavior:**
Agent reads all 7 architecture files, then works through Steps 1–26 in order, completing each and verifying before moving on. Final output is a running application accessible at `http://localhost:5173`.

---

### Example 2: Resuming interrupted build at Phase 7

**Input parameters:**
- All required parameters provided
- `skip_to_phase`: `"7"`

**Expected behavior:**
Agent skips Steps 1–6 (folder setup and npm install are already done), reads architecture docs, then starts from Step 7 (backend config/utils/middleware files).

---

## Troubleshooting

### PowerShell: `&&` causes "token '&&' is not a valid statement separator"
**Cause:** `&&` is a bash/cmd operator and does NOT work in PowerShell.
**Fix:** Run each command as a separate tool call or use `;` for sequential execution: `Set-Location "backend"; npm install`

### PowerShell: `npm` command not found
**Cause:** Node.js is not installed or not in PATH.
**Fix:** Install Node.js 18+ from nodejs.org and restart PowerShell. Verify with `node --version`.

### CORS error in browser console: "has been blocked by CORS policy"
**Cause:** Missing `credentials: true` in CORS config or `withCredentials: true` in axios.
**Fix:** Verify `backend\server.js` has `cors({ origin: 'http://localhost:5173', credentials: true })`. Verify `frontend\src\api\index.js` has `withCredentials: true` on the axios instance.

### Cookie not being sent with API requests
**Cause:** Either the axios instance is missing `withCredentials: true` or the CORS config is missing `credentials: true`.
**Fix:** Both must be set simultaneously — fix both files even if one looks correct.

### Video does not play — Video.js shows error
**Cause:** The HLS URL is wrong or ImageKit has not yet processed the video for HLS.
**Fix:** Verify the URL ends in `/ik-master.m3u8`. Check ImageKit dashboard — newly uploaded videos may take 30–60 seconds to be available for HLS streaming. Confirm the video file was successfully uploaded (not just the metadata).

### "Route /:id catches /search" — search returns 404 or wrong result
**Cause:** In `backend\routes\videos.js`, `GET /:id` is defined before `GET /search`.
**Fix:** Move `GET /search` route above `GET /:id` in the file. Express matches routes top-to-bottom.

### ImageKit upload fails with 401
**Cause:** The auth signature is expired or incorrectly generated.
**Fix:** Verify `backend\utils\imagekit.js` uses the correct private key. Verify `backend\routes\upload.js` calls `imagekit.getAuthenticationParameters()` correctly. Check that the frontend is using all four fields: `token`, `expire`, `signature`, and `publicKey`.

### Frontend blank page / compile error after adding Video.js
**Cause:** Video.js CSS import missing or the component is not properly initializing.
**Fix:** Ensure `import 'video.js/dist/video-js.css'` is in `VideoPlayer.jsx`. Ensure `videojs()` is called inside `useEffect`, not at the top level of the component.

### npm scripts fail: `nodemon is not recognized`
**Cause:** nodemon was installed as a dev dependency but the PATH is not updated in the current shell.
**Fix:** Use `npx nodemon server.js` instead, or close and re-open PowerShell after install.
